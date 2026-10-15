from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class SlotCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    vehicle_type: str = Field(default="CAR", pattern="^(CAR|MOTORCYCLE|SUV|TRUCK|EV)$")
    restrictions: Optional[Dict[str, Any]] = None

class SlotBulkCreate(BaseModel):
    prefix: str = "A"
    count: int = Field(ge=1, le=100)
    vehicle_type: str = "CAR"

class SlotUpdate(BaseModel):
    code: Optional[str] = None
    vehicle_type: Optional[str] = None
    restrictions: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(default=None, pattern="^(ACTIVE|BLOCKED)$")

class SlotResponse(BaseModel):
    id: int
    location_id: int
    code: str
    vehicle_type: str
    restrictions: Optional[Dict[str, Any]] = None
    status: str
    created_at: Optional[datetime] = None
    is_available: Optional[bool] = None
