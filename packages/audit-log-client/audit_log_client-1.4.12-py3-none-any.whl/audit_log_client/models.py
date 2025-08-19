import datetime
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    EXECUTE = "EXECUTE"
    GRANT = "GRANT"
    REVOKE = "REVOKE"


class AuditTarget(str, Enum):
    USER = "USER"
    FILE = "FILE"
    ROLE = "ROLE"
    PERMISSION = "PERMISSION"
    CONFIG = "CONFIG"
    SETTING = "SETTING"
    PRODUCT = "PRODUCT"
    ORDER = "ORDER"
    CUSTOMER = "CUSTOMER"
    SESSION = "SESSION"
    API_KEY = "API_KEY"
    DATABASE = "DATABASE"
    REPORT = "REPORT"
    PAYMENT = "PAYMENT"


class AuditLog(BaseModel):
    """审计日志数据模型 - 开放扩展字段"""
    # 核心字段
    action: AuditAction
    target_type: AuditTarget
    user_id: str
    description: str
    
    # 可选核心字段
    target_id: Optional[str] = None
    ip_address: Optional[str] = None
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    
    # 时间戳 - 修复默认值工厂
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    
    # Pydantic v2 配置语法
    model_config = ConfigDict(
        extra="allow",  # 允许任意额外字段
        arbitrary_types_allowed=True  # 允许自定义类型
    )
