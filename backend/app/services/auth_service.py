import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError

from app.config import settings
from app.database import fetch_one, execute, transaction
from app.exceptions import UnauthorizedError, AppException
from app.redis_client import deny_token, is_token_denied
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, PreferencesUpdate

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def create_access_token(user_id: int, role: str, email: str) -> Tuple[str, str, int]:
    jti = str(uuid.uuid4())
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "jti": jti,
        "type": "access",
        "exp": expire,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti, int(expires_delta.total_seconds())

def create_refresh_token(user_id: int) -> Tuple[str, str, int]:
    jti = str(uuid.uuid4())
    expires_delta = timedelta(days=settings.JWT_REFRESH_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "refresh",
        "exp": expire,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti, int(expires_delta.total_seconds())

async def register_user(req: RegisterRequest) -> UserResponse:
    # Check if user already exists
    existing = await fetch_one("SELECT id FROM users WHERE email = %s", (req.email.lower(),))
    if existing:
        raise AppException(400, "EMAIL_EXISTS", "A user with this email already exists")

    hashed = hash_password(req.password)
    
    async with transaction() as conn:
        last_id, _ = await execute(
            """
            INSERT INTO users (email, password_hash, full_name, phone, role, status, email_verified)
            VALUES (%s, %s, %s, %s, 'DRIVER', 'ACTIVE', 0)
            """,
            (req.email.lower(), hashed, req.full_name, req.phone),
            conn=conn,
        )
        # Create default preferences
        await execute(
            """
            INSERT INTO preferences (user_id, default_vehicle_type, preferred_facilities, max_walking_distance_m)
            VALUES (%s, 'CAR', JSON_ARRAY(), 1000)
            """,
            (last_id,),
            conn=conn,
        )

    user_row = await fetch_one("SELECT * FROM users WHERE id = %s", (last_id,))
    return UserResponse(**user_row)

async def login_user(req: LoginRequest) -> Tuple[UserResponse, str, str, int, int]:
    user_row = await fetch_one("SELECT * FROM users WHERE email = %s", (req.email.lower(),))
    if not user_row:
        raise UnauthorizedError("Invalid email or password")

    if user_row["status"] != "ACTIVE":
        raise AppException(403, "ACCOUNT_SUSPENDED", "Your account has been deactivated or suspended")

    if not verify_password(user_row["password_hash"], req.password):
        raise UnauthorizedError("Invalid email or password")

    user = UserResponse(**user_row)
    acc_token, _, acc_exp = create_access_token(user.id, user.role, user.email)
    ref_token, _, ref_exp = create_refresh_token(user.id)

    return user, acc_token, ref_token, acc_exp, ref_exp

async def rotate_refresh_token(refresh_token_str: str) -> Tuple[str, str, int, int, UserResponse]:
    try:
        payload = jwt.decode(
            refresh_token_str,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        jti = payload.get("jti")
        if not jti or await is_token_denied(jti):
            raise UnauthorizedError("Refresh token has been revoked")

        user_id = int(payload.get("sub"))
        user_row = await fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        if not user_row or user_row["status"] != "ACTIVE":
            raise UnauthorizedError("User is inactive or not found")

        # Invalidate old refresh token
        exp = payload.get("exp", 0)
        now_ts = int(datetime.now(timezone.utc).timestamp())
        remaining = max(1, exp - now_ts)
        await deny_token(jti, remaining)

        user = UserResponse(**user_row)
        new_acc, _, acc_exp = create_access_token(user.id, user.role, user.email)
        new_ref, _, ref_exp = create_refresh_token(user.id)

        return new_acc, new_ref, acc_exp, ref_exp, user
    except JWTError:
        raise UnauthorizedError("Invalid or expired refresh token")

async def logout_user(access_token_str: Optional[str], refresh_token_str: Optional[str]):
    # Deny access token
    if access_token_str:
        try:
            payload = jwt.decode(access_token_str, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            jti = payload.get("jti")
            if jti:
                exp = payload.get("exp", 0)
                remaining = max(1, exp - int(datetime.now(timezone.utc).timestamp()))
                await deny_token(jti, remaining)
        except Exception:
            pass

    # Deny refresh token
    if refresh_token_str:
        try:
            payload = jwt.decode(refresh_token_str, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            jti = payload.get("jti")
            if jti:
                exp = payload.get("exp", 0)
                remaining = max(1, exp - int(datetime.now(timezone.utc).timestamp()))
                await deny_token(jti, remaining)
        except Exception:
            pass

async def get_user_profile(user_id: int) -> Dict[str, Any]:
    user_row = await fetch_one("SELECT id, email, full_name, phone, role, status, email_verified, created_at FROM users WHERE id = %s", (user_id,))
    if not user_row:
        raise AppException(404, "USER_NOT_FOUND", "User profile not found")
    pref_row = await fetch_one("SELECT * FROM preferences WHERE user_id = %s", (user_id,))
    
    return {
        "user": user_row,
        "preferences": pref_row or {
            "default_vehicle_type": "CAR",
            "preferred_facilities": [],
            "max_walking_distance_m": 1000,
            "max_budget_paise": None,
        }
    }
