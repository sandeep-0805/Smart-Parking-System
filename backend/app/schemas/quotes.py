from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class QuoteRequest(BaseModel):
    slot_id: int
    start_at: datetime
    end_at: datetime

class LineItem(BaseModel):
    label: str
    amount_paise: int

class QuoteResponse(BaseModel):
    id: int
    slot_id: int
    start_at: datetime
    end_at: datetime
    total_paise: int
    line_items: List[Dict[str, Any]]
    valid_until: datetime
    rule_version: str
    location_name: Optional[str] = None
    slot_code: Optional[str] = None
