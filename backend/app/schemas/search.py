from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SearchSlotOption(BaseModel):
    slot_id: int
    slot_code: str
    vehicle_type: str
    total_price_paise: int
    quote_id: int
    score: float = 1.0
    reason_tags: List[str] = Field(default_factory=list)

class SearchLocationResult(BaseModel):
    location_id: int
    name: str
    address: str
    lat: float
    lng: float
    distance_m: float
    base_rate_paise: int
    facilities: List[str] = Field(default_factory=list)
    available_slots_count: int
    pay_at_venue: bool = False
    slots: List[SearchSlotOption] = Field(default_factory=list)

class SearchResponse(BaseModel):
    locations: List[SearchLocationResult]
    total_locations: int
    ranking_type: str = "weighted"  # weighted or basic
    start_at: datetime
    end_at: datetime

class LocationSuggestion(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float
    category: str = "area"  # 'parking' | 'area' | 'landmark'

class ReverseGeocodeResponse(BaseModel):
    display_name: str
    area: str
    lat: float
    lng: float
