from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class OperatorLocationStats(BaseModel):
    location_id: int
    name: str
    total_slots: int
    occupied_slots: int
    available_slots: int
    occupancy_pct: float
    today_revenue_paise: int
    status: str

class OperatorDashboardResponse(BaseModel):
    total_locations: int
    total_slots: int
    occupied_slots: int
    overall_occupancy_pct: float
    today_bookings_count: int
    today_revenue_paise: int
    locations: List[OperatorLocationStats]
    recent_bookings: List[Dict[str, Any]]
