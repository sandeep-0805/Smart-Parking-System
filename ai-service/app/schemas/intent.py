from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class IntentRequest(BaseModel):
    message: str
    collected_fields: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)

class IntentResponse(BaseModel):
    intent: str = "other"  # search, select_option, confirm, cancel_booking, other
    location_text: Optional[str] = None
    date_text: Optional[str] = None
    start_time_text: Optional[str] = None
    end_time_text: Optional[str] = None
    duration_minutes: Optional[int] = None
    vehicle_type: Optional[str] = None
    max_budget_inr: Optional[float] = None
    facilities: List[str] = Field(default_factory=list)
    option_index: Optional[int] = None
    confidence: float = 1.0
