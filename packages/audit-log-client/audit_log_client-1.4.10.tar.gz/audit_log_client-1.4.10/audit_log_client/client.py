import json
import time
import threading
import asyncio
import logging
import httpx
from datetime import datetime
from typing import List, Optional

from .models import AuditLog

# ====================== 同步客户端 ======================
class SyncAuditLogClient:
    def __init__(
        self,
        base_url: str,
        app_id: str,  #  AppID
        secret_key: str,  #  SecretKey
        buffer_size: int = 100,
        flush_interval: float = 10.0,
        max_retries: int = 3,
        timeout: float = 10.0
    ):
        MAX_BATCH_SIZE = 500 
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id  # 存储 AppID
        self.secret_key = secret_key  # 存储 SecretKey
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.timeout = timeout
        
        self.buffer = []
        self.lock = threading.Lock()
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-App-ID": self.app_id,
                "X-Secret-Key": self.secret_key,
                "Content-Type": "application/json"         
            }
        )
        
        # 启动后台刷新线程
        self.flush_thread = threading.Thread(target=self._periodic_flush, daemon=True)
        self.running = True
        self.flush_thread.start()
    
    def log(self, log: AuditLog) -> bool:
        """同步记录审计日志（缓冲处理）"""
        with self.lock:
            self.buffer.append(log)
            if len(self.buffer) >= self.buffer_size:
                self._flush_buffer()
        return True
    
    def batch_log(self, logs: List[AuditLog]) -> bool:
        """同步批量记录审计日志"""
        with self.lock:
            self.buffer.extend(logs)
            if len(self.buffer) >= self.buffer_size:
                self._flush_buffer()
        return True
    
    def _periodic_flush(self):
        """定期刷新缓冲区"""
        while self.running:
            time.sleep(self.flush_interval)
            self._flush_buffer()
    
    def _flush_buffer(self):
        """刷新缓冲区到日志服务（分批次处理）"""
        if not self.buffer:
            return True
        
        with self.lock:
            logs_to_send = self.buffer.copy()
            self.buffer = []
        
        # 分批次处理（每批最大500条）
        batch_size = 500  # 与服务端max_batch_size保持一致
        batches = [logs_to_send[i:i+batch_size] 
                for i in range(0, len(logs_to_send), batch_size)]
        
        all_success = True
        
        for batch in batches:
            # JSON序列化准备（字段名转换）
            logs_data = []
            for log in batch:
                log_dict = log.dict()
                # 字段名适配：ip_address -> IPAddress
                if 'ip_address' in log_dict:
                    log_dict['IPAddress'] = log_dict.pop('ip_address')
                logs_data.append(log_dict)
            
            # 重试逻辑
            batch_success = False
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.post(
                        "/logs/batch",
                        json=logs_data,
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code == 201:
                        batch_success = True
                        break
                    elif response.status_code == 413:  # 处理批次过大错误
                        logging.warning("Batch too large, splitting further")
                        self._fallback_write(batch)  # 直接降级处理
                        break
                    else:
                        logging.error(f"Failed to send logs: HTTP {response.status_code}")
                except Exception as e:
                    logging.error(f"Flush attempt {attempt+1} failed: {str(e)}")
                
                # 指数退避
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
            
            if not batch_success:
                all_success = False
                # 当前批次所有尝试失败后的降级处理
                self._fallback_write(batch)
        
        return all_success
    
    def _fallback_write(self, logs: List[AuditLog]):
        """降级策略：写入本地文件"""
        try:
            with open("audit_fallback.log", "a") as f:
                for log in logs:
                    f.write(json.dumps(log.model_dump()) + "\n")
            logging.warning(f"Wrote {len(logs)} logs to fallback file")
        except Exception as e:
            logging.error(f"Fallback write failed: {str(e)}")
    
    def query_logs(
        self,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """查询审计日志（同步）"""
        params = {}
        if action: params["action"] = action
        if target_type: params["target_type"] = target_type
        if target_id: params["target_id"] = target_id
        if user_id: params["user_id"] = user_id
        if start_time: params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_time: params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        params["limit"] = limit
        
        try:
            response = self.client.get("/logs", params=params)
            if response.status_code == 200:
                return [AuditLog(**item) for item in response.json()]
        except Exception as e:
            logging.error(f"Query failed: {str(e)}")
        
        return []
    
    def close(self):
        """关闭客户端并清理资源"""
        self.running = False
        self.flush_thread.join(timeout=5)
        self._flush_buffer()  # Final flush
        self.client.close()

# ====================== 异步客户端 ======================
class AsyncAuditLogClient:
    def __init__(
        self,
        base_url: str,
        app_id: str,  #  AppID
        secret_key: str,  #  SecretKey
        buffer_size: int = 100,
        flush_interval: float = 10.0,
        max_retries: int = 3,
        timeout: float = 10.0
    ):
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id  # 存储 AppID
        self.secret_key = secret_key  # 存储 SecretKey
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.timeout = timeout
        
        self.buffer = []
        self.lock = asyncio.Lock()
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-App-ID": self.app_id,
                "X-Secret-Key": self.secret_key,
                "Content-Type": "application/json"         
            }
        )
        self.flush_task = None
        self.running = False
    
    async def initialize(self):
        """异步初始化客户端"""
        self.running = True
        self.flush_task = asyncio.create_task(self._periodic_flush())
    
    async def log(self, log: AuditLog) -> bool:
        """异步记录审计日志（缓冲处理）"""
        async with self.lock:
            self.buffer.append(log)
            if len(self.buffer) >= self.buffer_size:
                await self._flush_buffer()
        return True
    
    async def batch_log(self, logs: List[AuditLog]) -> bool:
        """异步批量记录审计日志"""
        async with self.lock:
            self.buffer.extend(logs)
            if len(self.buffer) >= self.buffer_size:
                await self._flush_buffer()
        return True
    
    async def _periodic_flush(self):
        """定期刷新缓冲区"""
        while self.running:
            await asyncio.sleep(self.flush_interval)
            await self._flush_buffer()
    
    async def _flush_buffer(self):
        """刷新缓冲区到日志服务"""
        if not self.buffer:
            return True
        
        async with self.lock:
            logs_to_send = self.buffer.copy()
            self.buffer = []
        
        # JSON序列化准备
        logs_data = [log.dict() for log in logs_to_send]
        
        # 重试逻辑
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(
                    "/logs/batch",
                    json=logs_data,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 201:
                    return True
                else:
                    logging.error(f"Failed to send logs: HTTP {response.status_code}")
            except Exception as e:
                logging.error(f"Flush attempt {attempt+1} failed: {str(e)}")
            
            # 指数退避
            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)
        
        # 所有尝试失败后的降级处理
        await self._fallback_write(logs_to_send)
        return False
    
    async def _fallback_write(self, logs: List[AuditLog]):
        """降级策略：写入本地文件"""
        try:
            with open("audit_fallback.log", "a") as f:
                for log in logs:
                    f.write(json.dumps(log.dict()) + "\n")
            logging.warning(f"Wrote {len(logs)} logs to fallback file")
        except Exception as e:
            logging.error(f"Fallback write failed: {str(e)}")
    
    async def query_logs(
        self,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """查询审计日志（异步）"""
        params = {}
        if action: params["action"] = action
        if target_type: params["target_type"] = target_type
        if target_id: params["target_id"] = target_id
        if user_id: params["user_id"] = user_id
        if start_time: params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_time: params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        params["limit"] = limit
        
        try:
            response = await self.client.get("/logs", params=params)
            if response.status_code == 200:
                return [AuditLog(**item) for item in response.json()]
        except Exception as e:
            logging.error(f"Query failed: {str(e)}")
        
        return []
    
    async def shutdown(self):
        """关闭客户端并清理资源"""
        self.running = False
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        await self._flush_buffer()  # Final flush
        await self.client.aclose()