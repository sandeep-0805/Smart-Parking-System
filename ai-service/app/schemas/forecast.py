from typing import Optional, Dict, Any
from pydantic import BaseModel

class ForecastRequest(BaseModel):
    location_id: int
    target_time: str
    horizon_minutes: int = 60

class ForecastResponse(BaseModel):
    location_id: int
    target_time: str
    predicted_available: float
    predicted_occupied: float
    total_slots: int
    occupancy_pct: float
    uncertainty_low: float
    uncertainty_high: float
    generated_at: str
    model_version: str
    is_estimate: bool = True

class TrainResponse(BaseModel):
    version: str
    metrics: Dict[str, Any]
    message: str = "Training completed"
