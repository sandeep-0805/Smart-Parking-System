from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from app.dependencies import get_current_user, require_role, get_optional_user
from app.schemas.locations import LocationCreate, LocationUpdate, LocationResponse
from app.services.location_service import (
    create_location,
    get_location,
    update_location,
    list_locations,
    approve_location,
    delete_location,
)
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("", response_model=List[LocationResponse])
async def get_locations(
    status: Optional[str] = Query(None),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    owner_id = None
    status_filter = status

    # Unauthenticated users and drivers should only see APPROVED locations
    if not user or user.get("role") == "DRIVER":
        status_filter = status or "APPROVED"
    elif user.get("role") == "OPERATOR":
        # Operators see their own locations by default unless inspecting approved public ones
        if status != "APPROVED":
            owner_id = user["id"]

    return await list_locations(owner_id=owner_id, status_filter=status_filter)

@router.get("/my", response_model=List[LocationResponse])
async def get_my_locations(
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    """Returns all locations owned by the authenticated operator/admin."""
    return await list_locations(owner_id=user["id"])

@router.get("/{id}", response_model=LocationResponse)
async def get_location_by_id(id: int):
    return await get_location(id)

@router.post("", response_model=LocationResponse)
async def create_new_location(
    req: LocationCreate,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
    request: Request = None,
):
    loc = await create_location(user["id"], req)
    ip = request.client.host if request and request.client else None
    await log_audit_event(
        action="LOCATION_CREATED",
        resource_type="parking_location",
        user_id=user["id"],
        resource_id=loc["id"],
        details={"name": loc["name"], "address": loc["address"]},
        ip_address=ip,
    )
    return loc

@router.patch("/{id}", response_model=LocationResponse)
async def update_existing_location(
    id: int,
    req: LocationUpdate,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await update_location(id, user["id"], user["role"], req)

@router.delete("/{id}")
async def remove_location(
    id: int,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
    request: Request = None,
):
    await delete_location(id, user_id=user["id"], user_role=user["role"])
    ip = request.client.host if request and request.client else None
    await log_audit_event(
        action="LOCATION_DELETED",
        resource_type="parking_location",
        user_id=user["id"],
        resource_id=id,
        details={},
        ip_address=ip,
    )
    return {"message": f"Location {id} deleted successfully"}

@router.post("/{id}/approve", response_model=LocationResponse)
@router.put("/{id}/approve", response_model=LocationResponse)
async def approve_location_endpoint(
    id: int,
    user: Dict[str, Any] = Depends(require_role("ADMIN")),
    request: Request = None,
):
    loc = await approve_location(id)
    ip = request.client.host if request and request.client else None
    await log_audit_event(
        action="LOCATION_APPROVED",
        resource_type="parking_location",
        user_id=user["id"],
        resource_id=id,
        details={"name": loc["name"]},
        ip_address=ip,
    )
    return loc
