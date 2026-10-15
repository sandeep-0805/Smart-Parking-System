from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CandidateSlot(BaseModel):
    slot_id: int
    location_id: int
    location_name: str
    distance_m: float
    total_price_paise: int
    vehicle_type: str = "CAR"
    facilities: List[str] = Field(default_factory=list)
    availability_confidence: float = 1.0

class RankRequest(BaseModel):
    candidates: List[CandidateSlot]
    preferences: Dict[str, Any] = Field(default_factory=dict)
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "distance": 0.35,
            "price": 0.30,
            "availability": 0.15,
            "facilities": 0.20,
        }
    )

class ScoredSlot(BaseModel):
    slot_id: int
    location_id: int
    score: float
    factors: Dict[str, float]
    reason_tags: List[str]

class RankResponse(BaseModel):
    ranked: List[ScoredSlot]
    ranking_type: str = "weighted"
