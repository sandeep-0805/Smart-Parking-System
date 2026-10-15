import json
from typing import List, Dict, Any, Optional
from app.database import fetch_one, fetch_all, execute, execute_many, transaction
from app.exceptions import NotFoundError, AppException
from app.schemas.slots import SlotCreate, SlotBulkCreate, SlotUpdate

async def create_slot(location_id: int, req: SlotCreate) -> Dict[str, Any]:
    restr_json = json.dumps(req.restrictions) if req.restrictions else None
    async with transaction() as conn:
        last_id, _ = await execute(
            """
            INSERT INTO parking_slots (location_id, code, vehicle_type, restrictions, status)
            VALUES (%s, %s, %s, %s, 'ACTIVE')
            """,
            (location_id, req.code, req.vehicle_type, restr_json),
            conn=conn,
        )
        await execute(
            "UPDATE parking_locations SET total_slots = (SELECT COUNT(*) FROM parking_slots WHERE location_id = %s) WHERE id = %s",
            (location_id, location_id),
            conn=conn,
        )
    return await get_slot(last_id)

async def bulk_create_slots(location_id: int, req: SlotBulkCreate) -> List[Dict[str, Any]]:
    slots_data = []
    for i in range(1, req.count + 1):
        code = f"{req.prefix}{i:02d}"
        slots_data.append((location_id, code, req.vehicle_type, None, "ACTIVE"))

    async with transaction() as conn:
        await execute_many(
            """
            INSERT INTO parking_slots (location_id, code, vehicle_type, restrictions, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            slots_data,
            conn=conn,
        )
        await execute(
            "UPDATE parking_locations SET total_slots = (SELECT COUNT(*) FROM parking_slots WHERE location_id = %s) WHERE id = %s",
            (location_id, location_id),
            conn=conn,
        )

    return await get_slots_for_location(location_id)

async def get_slot(slot_id: int) -> Dict[str, Any]:
    row = await fetch_one(
        "SELECT id, location_id, code, vehicle_type, restrictions, status, created_at FROM parking_slots WHERE id = %s",
        (slot_id,),
    )
    if not row:
        raise NotFoundError("Slot not found")
    if isinstance(row["restrictions"], str):
        row["restrictions"] = json.loads(row["restrictions"])
    return row

async def update_slot(slot_id: int, req: SlotUpdate) -> Dict[str, Any]:
    updates = []
    params = []
    if req.code is not None:
        updates.append("code = %s")
        params.append(req.code)
    if req.vehicle_type is not None:
        updates.append("vehicle_type = %s")
        params.append(req.vehicle_type)
    if req.restrictions is not None:
        updates.append("restrictions = %s")
        params.append(json.dumps(req.restrictions))
    if req.status is not None:
        updates.append("status = %s")
        params.append(req.status)

    if updates:
        params.append(slot_id)
        await execute(f"UPDATE parking_slots SET {', '.join(updates)} WHERE id = %s", tuple(params))
    return await get_slot(slot_id)

async def set_slot_status(slot_id: int, status_str: str) -> Dict[str, Any]:
    await execute("UPDATE parking_slots SET status = %s WHERE id = %s", (status_str, slot_id))
    return await get_slot(slot_id)

async def get_slots_for_location(location_id: int) -> List[Dict[str, Any]]:
    rows = await fetch_all(
        "SELECT id, location_id, code, vehicle_type, restrictions, status, created_at FROM parking_slots WHERE location_id = %s ORDER BY code ASC",
        (location_id,),
    )
    for r in rows:
        if isinstance(r["restrictions"], str):
            r["restrictions"] = json.loads(r["restrictions"])
    return rows
