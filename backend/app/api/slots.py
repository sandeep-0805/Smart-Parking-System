from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.dependencies import require_role
from app.schemas.slots import SlotCreate, SlotBulkCreate, SlotUpdate, SlotResponse
from app.services.slot_service import (
    create_slot,
    bulk_create_slots,
    get_slots_for_location,
    get_slot,
    update_slot,
    set_slot_status,
)

router = APIRouter(tags=["Slots"])

@router.get("/locations/{location_id}/slots", response_model=List[SlotResponse])
async def list_location_slots(location_id: int):
    return await get_slots_for_location(location_id)

@router.post("/locations/{location_id}/slots", response_model=SlotResponse)
async def add_slot(
    location_id: int,
    req: SlotCreate,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await create_slot(location_id, req, user_id=user["id"], user_role=user["role"])

@router.post("/locations/{location_id}/slots/bulk", response_model=List[SlotResponse])
async def add_slots_bulk(
    location_id: int,
    req: SlotBulkCreate,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await bulk_create_slots(location_id, req, user_id=user["id"], user_role=user["role"])

@router.patch("/slots/{id}", response_model=SlotResponse)
async def update_slot_by_id(
    id: int,
    req: SlotUpdate,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await update_slot(id, req, user_id=user["id"], user_role=user["role"])

@router.post("/slots/{id}/block", response_model=SlotResponse)
async def block_slot_endpoint(
    id: int,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await set_slot_status(id, "BLOCKED", user_id=user["id"], user_role=user["role"])

@router.post("/slots/{id}/unblock", response_model=SlotResponse)
async def unblock_slot_endpoint(
    id: int,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await set_slot_status(id, "ACTIVE", user_id=user["id"], user_role=user["role"])
