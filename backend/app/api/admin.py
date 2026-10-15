import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from app.dependencies import require_role
from app.database import fetch_all, fetch_one, execute
from app.exceptions import NotFoundError
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
async def update_user_role(id: int, req: UpdateUserRoleRequest):
    await execute("UPDATE users SET role = %s WHERE id = %s", (req.role, id))
    return await fetch_one("SELECT id, email, full_name, role, status FROM users WHERE id = %s", (id,))

@router.patch("/users/{id}/status")
async def update_user_status(id: int, req: UpdateUserStatusRequest):
    await execute("UPDATE users SET status = %s WHERE id = %s", (req.status, id))
    return await fetch_one("SELECT id, email, full_name, role, status FROM users WHERE id = %s", (id,))

@router.get("/config", response_model=List[SystemConfigItem])
async def get_system_config():
    rows = await fetch_all("SELECT config_key, config_value, description, updated_at FROM system_config")
    for r in rows:
        if isinstance(r["config_value"], str):
            r["config_value"] = json.loads(r["config_value"])
    return rows

@router.patch("/config/{key}")
async def update_config_value(key: str, req: ConfigUpdateRequest):
    await execute(
        "UPDATE system_config SET config_value = %s, updated_at = NOW() WHERE config_key = %s",
        (json.dumps(req.config_value), key),
    )
    row = await fetch_one("SELECT config_key, config_value, description, updated_at FROM system_config WHERE config_key = %s", (key,))
    if not row:
        raise NotFoundError("Config key not found")
    if isinstance(row["config_value"], str):
        row["config_value"] = json.loads(row["config_value"])
    return row

@router.get("/audit-log", response_model=List[AuditLogItem])
async def get_audit_log(limit: int = 50):
    rows = await fetch_all("SELECT * FROM audit_log ORDER BY id DESC LIMIT %s", (limit,))
    for r in rows:
        if isinstance(r["details"], str):
            r["details"] = json.loads(r["details"])
    return rows

@router.get("/locations")
async def get_all_locations_admin():
    return await fetch_all("SELECT * FROM parking_locations ORDER BY id DESC")
