from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class BookingCreate(BaseModel):
    quote_id: int
    idempotency_key: Optional[str] = None
    source: str = Field(default="MANUAL", pattern="^(MANUAL|CHAT|AUTO)$")

class BookingCancelRequest(BaseModel):
    reason: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    quote_id: Optional[int] = None
    start_at: datetime
    end_at: datetime
    status: str
    total_paise: int
    hold_expires_at: Optional[datetime] = None
    source: str
    cancellation_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # Enriched fields for UX
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    slot_code: Optional[str] = None
    vehicle_type: Optional[str] = None
    payment_status: Optional[str] = None
    pay_link: Optional[str] = None
    time_remaining_seconds: Optional[int] = None

class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    total: int
