from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class AutoBookingRuleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    rule: Dict[str, Any] = Field(
        description="Rule criteria: location_id, vehicle_type, days [0-6], start_time, end_time, max_price_paise, facilities"
    )
    lead_time_minutes: int = Field(default=60, ge=15, le=1440)
    weekly_booking_cap: int = Field(default=5, ge=1, le=50)
    enabled: bool = True

class AutoBookingRuleUpdate(BaseModel):
    name: Optional[str] = None
    rule: Optional[Dict[str, Any]] = None
    lead_time_minutes: Optional[int] = None
    weekly_booking_cap: Optional[int] = None
    enabled: Optional[bool] = None

class AutoBookingRuleResponse(BaseModel):
    id: int
    user_id: int
    name: str
    rule: Dict[str, Any]
    lead_time_minutes: int
    weekly_booking_cap: int
    enabled: bool
    created_at: Optional[datetime] = None

class AutoBookingAuditResponse(BaseModel):
    id: int
    rule_id: int
    user_id: int
    candidates_count: int
    selected_slot_id: Optional[int] = None
    selected_location_id: Optional[int] = None
    booking_id: Optional[int] = None
    scores: Optional[Dict[str, Any]] = None
    decision: str
    decision_reason: Optional[str] = None
    rule_snapshot: Dict[str, Any]
    created_at: Optional[datetime] = None
