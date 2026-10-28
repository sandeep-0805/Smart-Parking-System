import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Request
from app.dependencies import require_role, get_current_user
from app.database import fetch_all, fetch_one, execute
from app.exceptions import NotFoundError, AppException
from app.services.audit_service import log_audit_event
from app.schemas.admin import (
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    ConfigUpdateRequest,
    SystemConfigItem,
    AuditLogItem,
)

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_role("ADMIN"))])

@router.get("/users")
async def list_users(
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    conds = []
    params = []
    if role:
        conds.append("role = %s")
        params.append(role)
    if status:
        conds.append("status = %s")
        params.append(status)
    where_sql = f"WHERE {' AND '.join(conds)}" if conds else ""
    return await fetch_all(
        f"SELECT id, email, full_name, phone, role, status, email_verified, created_at FROM users {where_sql} ORDER BY id DESC",
        tuple(params) if params else None,
    )

@router.patch("/users/{id}/role")
async def update_user_role(
    id: int,
    req: UpdateUserRoleRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None,
):
    # Prevent admin self-demotion
    if current_user["id"] == id and req.role != "ADMIN":
        raise AppException(400, "CANNOT_DEMOTE_SELF", "Administrators cannot demote their own account")

    await execute("UPDATE users SET role = %s WHERE id = %s", (req.role, id))
    updated = await fetch_one("SELECT id, email, full_name, role, status FROM users WHERE id = %s", (id,))
    
    # Audit log
    ip = request.client.host if request and request.client else None
    await log_audit_event(
        action="USER_ROLE_UPDATED",
        resource_type="user",
        user_id=current_user["id"],
        resource_id=id,
        details={"new_role": req.role, "user_email": updated.get("email") if updated else None},
        ip_address=ip,
    )
    return updated

@router.patch("/users/{id}/status")
async def update_user_status(
    id: int,
    req: UpdateUserStatusRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None,
):
    # Prevent admin self-suspension
    if current_user["id"] == id and req.status != "ACTIVE":
        raise AppException(400, "CANNOT_SUSPEND_SELF", "Administrators cannot suspend their own account")

    await execute("UPDATE users SET status = %s WHERE id = %s", (req.status, id))
    updated = await fetch_one("SELECT id, email, full_name, role, status FROM users WHERE id = %s", (id,))

    # Audit log
    ip = request.client.host if request and request.client else None
    await log_audit_event(
        action="USER_STATUS_UPDATED",
        resource_type="user",
        user_id=current_user["id"],
        resource_id=id,
        details={"new_status": req.status, "user_email": updated.get("email") if updated else None},
        ip_address=ip,
    )
    return updated

@router.get("/config", response_model=List[SystemConfigItem])
async def get_system_config():
    rows = await fetch_all("SELECT config_key, config_value, description, updated_at FROM system_config")
    for r in rows:
        if isinstance(r["config_value"], str):
            try:
                r["config_value"] = json.loads(r["config_value"])
            except Exception:
                pass
    return rows

@router.patch("/config/{key}")
async def update_config_value(
    key: str,
    req: ConfigUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None,
):
    val_json = json.dumps(req.config_value)
    await execute(
        "UPDATE system_config SET config_value = %s, updated_at = NOW() WHERE config_key = %s",
        (val_json, key),
    )
    row = await fetch_one("SELECT config_key, config_value, description, updated_at FROM system_config WHERE config_key = %s", (key,))
    if not row:
        raise NotFoundError("Config key not found")
    if isinstance(row["config_value"], str):
        try:
            row["config_value"] = json.loads(row["config_value"])
        except Exception:
            pass

    # Audit log
    ip = request.client.host if request and request.client else None
    await log_audit_event(
        action="SYSTEM_CONFIG_UPDATED",
        resource_type="system_config",
        user_id=current_user["id"],
        resource_id=None,
        details={"config_key": key, "new_value": req.config_value},
        ip_address=ip,
    )
    return row

@router.get("/audit-log", response_model=List[AuditLogItem])
async def get_audit_log(limit: int = 50):
    rows = await fetch_all("SELECT * FROM audit_log ORDER BY id DESC LIMIT %s", (limit,))
    for r in rows:
        if isinstance(r["details"], str):
            try:
                r["details"] = json.loads(r["details"])
            except Exception:
                pass
    return rows

@router.get("/locations")
async def get_all_locations_admin():
    # Explicit column list excluding raw binary location_point (BUG-01 fix)
    rows = await fetch_all(
        """
        SELECT id, owner_id, name, address, lat, lng, operating_hours,
               facilities, base_rate_paise, min_rate_paise, max_rate_paise,
               rate_update_interval_min, pay_at_venue, status, total_slots, created_at, updated_at
        FROM parking_locations
        ORDER BY id DESC
        """
    )
    for r in rows:
        if isinstance(r.get("operating_hours"), str):
            try:
                r["operating_hours"] = json.loads(r["operating_hours"])
            except Exception:
                pass
        if isinstance(r.get("facilities"), str):
            try:
                r["facilities"] = json.loads(r["facilities"])
            except Exception:
                pass
    return rows
