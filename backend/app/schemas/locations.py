from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class LocationBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    address: str
    lat: float = Field(ge=-90.0, le=90.0)
    lng: float = Field(ge=-180.0, le=180.0)
    operating_hours: Dict[str, Any] = Field(
        default_factory=lambda: {
            "all": {"open": "00:00", "close": "23:59"}
        }
    )
    facilities: List[str] = Field(default_factory=list)
    base_rate_paise: int = Field(default=2000, ge=0)
    min_rate_paise: int = Field(default=1000, ge=0)
    max_rate_paise: int = Field(default=10000, ge=0)
    rate_update_interval_min: int = Field(default=15, ge=5)
    pay_at_venue: bool = False

    @model_validator(mode="after")
    def validate_rate_bounds(self):
        if self.min_rate_paise > self.max_rate_paise:
            raise ValueError(f"min_rate_paise ({self.min_rate_paise}) cannot exceed max_rate_paise ({self.max_rate_paise})")
        if not (self.min_rate_paise <= self.base_rate_paise <= self.max_rate_paise):
            raise ValueError(f"base_rate_paise ({self.base_rate_paise}) must be between min_rate_paise ({self.min_rate_paise}) and max_rate_paise ({self.max_rate_paise})")
        return self

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    operating_hours: Optional[Dict[str, Any]] = None
    facilities: Optional[List[str]] = None
    base_rate_paise: Optional[int] = None
    min_rate_paise: Optional[int] = None
    max_rate_paise: Optional[int] = None
    rate_update_interval_min: Optional[int] = None
    pay_at_venue: Optional[bool] = None

    @model_validator(mode="after")
    def validate_update_rate_bounds(self):
        if self.min_rate_paise is not None and self.max_rate_paise is not None:
            if self.min_rate_paise > self.max_rate_paise:
                raise ValueError("min_rate_paise cannot exceed max_rate_paise")
        return self

class LocationResponse(LocationBase):
    id: int
    owner_id: int
    status: str
    total_slots: int = 0
    created_at: Optional[datetime] = None
    distance_m: Optional[float] = None
    available_slots_count: Optional[int] = None
