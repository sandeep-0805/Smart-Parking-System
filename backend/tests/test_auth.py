import pytest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from jose import jwt
from app.config import settings

def test_password_hashing():
    raw = "SecurePassword@123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(hashed, raw) is True
    assert verify_password(hashed, "WrongPassword") is False

def test_jwt_access_token_creation():
    token, jti, exp_secs = create_access_token(user_id=42, role="DRIVER", email="test@parking.local")
    assert token is not None
    assert len(jti) > 0
    assert exp_secs == settings.JWT_ACCESS_MINUTES * 60

    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["role"] == "DRIVER"
    assert payload["email"] == "test@parking.local"
    assert payload["type"] == "access"
