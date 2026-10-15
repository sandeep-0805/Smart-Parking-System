from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
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

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("", response_model=List[LocationResponse])
async def get_locations(
    status: Optional[str] = Query(None),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    owner_id = None
    if user and user.get("role") == "OPERATOR" and status != "APPROVED":
        owner_id = user["id"]
    return await list_locations(owner_id=owner_id, status_filter=status)

@router.get("/{id}", response_model=LocationResponse)
async def get_location_by_id(id: int):
    return await get_location(id)

@router.post("", response_model=LocationResponse)
async def create_new_location(
    req: LocationCreate,
    user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN")),
):
    return await create_location(user["id"], req)

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
    _user: Dict[str, Any] = Depends(require_role("ADMIN")),
):
    await delete_location(id)
    return {"message": f"Location {id} deleted successfully"}

@router.post("/{id}/approve", response_model=LocationResponse)
async def approve_location_endpoint(
    id: int,
    _user: Dict[str, Any] = Depends(require_role("ADMIN")),
):
    return await approve_location(id)
