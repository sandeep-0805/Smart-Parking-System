from typing import Optional, List, Dict, Any
from fastapi import Request, Depends, Header
from jose import jwt, JWTError

from app.config import settings
from app.exceptions import UnauthorizedError, ForbiddenError
from app.redis_client import is_token_denied

async def get_current_user(request: Request) -> Dict[str, Any]:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise UnauthorizedError("Missing Authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid Authorization header format. Expected 'Bearer <token>'")

    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        jti = payload.get("jti")
        if jti and await is_token_denied(jti):
            raise UnauthorizedError("Token has been revoked")

        user_id = payload.get("sub")
        role = payload.get("role")
        email = payload.get("email")

        if not user_id or not role:
            raise UnauthorizedError("Invalid token payload")

        return {
            "id": int(user_id),
            "user_id": int(user_id),
            "role": role,
            "email": email,
        }
    except JWTError as e:
        raise UnauthorizedError(f"Token validation failed: {str(e)}")

async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    try:
        return await get_current_user(request)
    except Exception:
        return None

def require_role(*allowed_roles: str):
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "")
        if user_role not in allowed_roles:
            raise ForbiddenError(f"Access denied for role '{user_role}'. Required: {allowed_roles}")
        return current_user
    return role_checker

async def verify_service_token(
    x_service_token: Optional[str] = Header(None, alias="X-Service-Token"),
    authorization: Optional[str] = Header(None),
) -> str:
    token = x_service_token
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    if not token or token != settings.AI_SERVICE_TOKEN:
        raise UnauthorizedError("Invalid internal service token")
    return token
