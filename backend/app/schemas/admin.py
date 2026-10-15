from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class UpdateUserRoleRequest(BaseModel):
    role: str = Field(pattern="^(DRIVER|OPERATOR|ADMIN)$")

class UpdateUserStatusRequest(BaseModel):
    status: str = Field(pattern="^(ACTIVE|INACTIVE|SUSPENDED)$")

class ConfigUpdateRequest(BaseModel):
    config_value: Any

class SystemConfigItem(BaseModel):
    config_key: str
    config_value: Any
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

class AuditLogItem(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None
