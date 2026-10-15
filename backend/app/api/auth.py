from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Response, Request, Cookie
from app.config import settings
from app.dependencies import get_current_user
from app.exceptions import RateLimitError, UnauthorizedError
from app.redis_client import check_rate_limit
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    PreferencesUpdate,
)
from app.services.auth_service import (
    register_user,
    login_user,
    rotate_refresh_token,
    logout_user,
    get_user_profile,
)
from app.database import execute, fetch_all

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(f"reg:{client_ip}", settings.RATE_LIMIT_REGISTER, 60):
        raise RateLimitError("Too many registration attempts. Please wait a minute.")
    return await register_user(req)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, response: Response, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(f"login:{client_ip}", settings.RATE_LIMIT_LOGIN, 60):
        raise RateLimitError("Too many login attempts. Please wait a minute.")

    user, acc_token, ref_token, acc_exp, ref_exp = await login_user(req)

    # FR-A2: 7-day refresh token in httpOnly, Secure, SameSite=Lax cookie
    response.set_cookie(
        key="refresh_token",
        value=ref_token,
        max_age=ref_exp,
        httponly=True,
        secure=False,  # False for dev HTTP; True in prod HTTPS
        samesite="lax",
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=acc_token,
        token_type="bearer",
        expires_in_seconds=acc_exp,
        user=user,
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    request: Request,
    refresh_token: Optional[str] = Cookie(None),
):
    token = refresh_token
    if not token:
        # Fallback to JSON body or auth header if cookie not present
        body = await request.json() if request.headers.get("content-type") == "application/json" else {}
        token = body.get("refresh_token")

    if not token:
        raise UnauthorizedError("Missing refresh token cookie")

    new_acc, new_ref, acc_exp, ref_exp, user = await rotate_refresh_token(token)

    response.set_cookie(
        key="refresh_token",
        value=new_ref,
        max_age=ref_exp,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=new_acc,
        token_type="bearer",
        expires_in_seconds=acc_exp,
        user=user,
    )

@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    refresh_token: Optional[str] = Cookie(None),
):
    auth_header = request.headers.get("Authorization", "")
    acc_token = auth_header.split()[1] if len(auth_header.split()) == 2 else None
    await logout_user(acc_token, refresh_token)
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return await get_user_profile(user["id"])

@router.put("/preferences")
async def update_preferences(
    req: PreferencesUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
):
    import json
    await execute(
        """
        UPDATE preferences
        SET default_vehicle_type = %s,
            preferred_facilities = %s,
            max_walking_distance_m = %s,
            max_budget_paise = %s
        WHERE user_id = %s
        """,
        (
            req.default_vehicle_type,
            json.dumps(req.preferred_facilities or []),
            req.max_walking_distance_m,
            req.max_budget_paise,
            user["id"],
        ),
    )
    return await get_user_profile(user["id"])

@router.get("/notifications")
async def get_notifications(user: Dict[str, Any] = Depends(get_current_user)):
    rows = await fetch_all(
        "SELECT id, type, title, message, is_read, data, created_at FROM notifications WHERE user_id = %s ORDER BY id DESC LIMIT 50",
        (user["id"],),
    )
    import json
    for r in rows:
        if isinstance(r["data"], str):
            r["data"] = json.loads(r["data"])
    return rows
