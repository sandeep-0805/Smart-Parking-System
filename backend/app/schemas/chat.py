from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: Optional[str] = None

class ChatOption(BaseModel):
    option_index: int
    slot_id: int
    quote_id: int
    location_id: int
    location_name: str
    address: str
    slot_code: str
    total_price_paise: int
    price_formatted: str
    distance_m: float
    reason_tags: List[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    intent: str
    options: List[ChatOption] = Field(default_factory=list)
    requires_login: bool = False
    action_type: Optional[str] = None  # show_options, show_booking, redirect_search, payment_ready
    booking_id: Optional[int] = None
    prefill_search: Optional[Dict[str, Any]] = None
