from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Argon2id hashed password")
    full_name: str = Field(min_length=2, max_length=100)
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str
    status: str
    email_verified: bool = False
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserResponse

class PreferencesUpdate(BaseModel):
    default_vehicle_type: Optional[str] = "CAR"
    preferred_facilities: Optional[List[str]] = Field(default_factory=list)
    max_walking_distance_m: Optional[int] = 1000
    max_budget_paise: Optional[int] = None

class PreferencesResponse(BaseModel):
    user_id: int
    default_vehicle_type: str
    preferred_facilities: List[str]
    max_walking_distance_m: Optional[int]
    max_budget_paise: Optional[int]
