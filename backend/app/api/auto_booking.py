import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.database import fetch_all, fetch_one, execute
from app.exceptions import NotFoundError, ForbiddenError
from app.schemas.auto_booking import (
    AutoBookingRuleCreate,
    AutoBookingRuleUpdate,
    AutoBookingRuleResponse,
    AutoBookingAuditResponse,
)

router = APIRouter(prefix="/auto-booking", tags=["Auto-Booking"])

@router.get("/rules", response_model=List[AutoBookingRuleResponse])
async def list_my_rules(user: Dict[str, Any] = Depends(get_current_user)):
    rows = await fetch_all("SELECT * FROM auto_booking_rules WHERE user_id = %s", (user["id"],))
    for r in rows:
        if isinstance(r["rule"], str):
            r["rule"] = json.loads(r["rule"])
    return rows

@router.post("/rules", response_model=AutoBookingRuleResponse)
async def create_rule(
    req: AutoBookingRuleCreate,
    user: Dict[str, Any] = Depends(get_current_user),
):
    last_id, _ = await execute(
        """
        INSERT INTO auto_booking_rules (user_id, name, rule, lead_time_minutes, weekly_booking_cap, enabled)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            user["id"],
            req.name,
            json.dumps(req.rule),
            req.lead_time_minutes,
            req.weekly_booking_cap,
            1 if req.enabled else 0,
        ),
    )
    row = await fetch_one("SELECT * FROM auto_booking_rules WHERE id = %s", (last_id,))
    if isinstance(row["rule"], str):
        row["rule"] = json.loads(row["rule"])
    return row

@router.patch("/rules/{id}", response_model=AutoBookingRuleResponse)
async def update_rule(
    id: int,
    req: AutoBookingRuleUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
):
    existing = await fetch_one("SELECT * FROM auto_booking_rules WHERE id = %s", (id,))
    if not existing:
        raise NotFoundError("Rule not found")
    if existing["user_id"] != user["id"]:
        raise ForbiddenError("Cannot modify another user's rule")

    updates = []
    params = []
    if req.name is not None:
        updates.append("name = %s")
        params.append(req.name)
    if req.rule is not None:
        updates.append("rule = %s")
        params.append(json.dumps(req.rule))
    if req.lead_time_minutes is not None:
        updates.append("lead_time_minutes = %s")
        params.append(req.lead_time_minutes)
    if req.weekly_booking_cap is not None:
        updates.append("weekly_booking_cap = %s")
        params.append(req.weekly_booking_cap)
    if req.enabled is not None:
        updates.append("enabled = %s")
        params.append(1 if req.enabled else 0)

    if updates:
        params.append(id)
        await execute(f"UPDATE auto_booking_rules SET {', '.join(updates)} WHERE id = %s", tuple(params))

    row = await fetch_one("SELECT * FROM auto_booking_rules WHERE id = %s", (id,))
    if isinstance(row["rule"], str):
        row["rule"] = json.loads(row["rule"])
    return row

@router.delete("/rules/{id}")
async def delete_rule(id: int, user: Dict[str, Any] = Depends(get_current_user)):
    existing = await fetch_one("SELECT * FROM auto_booking_rules WHERE id = %s", (id,))
    if not existing:
        raise NotFoundError("Rule not found")
    if existing["user_id"] != user["id"]:
        raise ForbiddenError("Cannot delete another user's rule")

    await execute("DELETE FROM auto_booking_rules WHERE id = %s", (id,))
    return {"message": "Rule deleted"}

@router.get("/audit", response_model=List[AutoBookingAuditResponse])
async def get_audit_trail(user: Dict[str, Any] = Depends(get_current_user)):
    rows = await fetch_all(
        "SELECT * FROM auto_booking_audit WHERE user_id = %s ORDER BY id DESC LIMIT 50",
        (user["id"],),
    )
    for r in rows:
        if isinstance(r["rule_snapshot"], str):
            r["rule_snapshot"] = json.loads(r["rule_snapshot"])
        if isinstance(r["scores"], str):
            r["scores"] = json.loads(r["scores"])
    return rows
