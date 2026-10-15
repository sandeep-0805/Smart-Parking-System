from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Header, Query
from app.dependencies import get_current_user
from app.schemas.bookings import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
    BookingCancelRequest,
)
from app.services.booking_service import (
    create_booking_reservation,
    get_booking_details,
    cancel_booking,
)
from app.database import fetch_all, fetch_one

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("", response_model=BookingResponse)
async def create_booking(
    req: BookingCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    user: Dict[str, Any] = Depends(get_current_user),
):
    key = idempotency_key or req.idempotency_key
    return await create_booking_reservation(
        user_id=user["id"],
        quote_id=req.quote_id,
        idempotency_key=key,
        source=req.source,
    )

@router.get("", response_model=BookingListResponse)
async def list_user_bookings(
    status: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user),
):
    conditions = ["b.user_id = %s"]
    params = [user["id"]]

    if status:
        conditions.append("b.status = %s")
        params.append(status)

    where_clause = "WHERE " + " AND ".join(conditions)
    query = f"""
    SELECT b.id, b.user_id, b.slot_id, b.quote_id, b.start_at, b.end_at,
           b.status, b.total_paise, b.hold_expires_at, b.source,
           b.cancellation_reason, b.created_at,
           s.code as slot_code, s.vehicle_type,
           l.id as location_id, l.name as location_name, l.address as location_address,
           p.status as payment_status
    FROM bookings b
    JOIN parking_slots s ON b.slot_id = s.id
    JOIN parking_locations l ON s.location_id = l.id
    LEFT JOIN payments p ON p.booking_id = b.id
    {where_clause}
    ORDER BY b.id DESC
    """
    rows = await fetch_all(query, tuple(params))
    
    # Calculate time remaining for any holds
    from app.utils import utc_now
    now = utc_now()
    for r in rows:
        time_rem = 0
        if r["status"] == "PENDING_PAYMENT" and r["hold_expires_at"]:
            time_rem = max(0, int((r["hold_expires_at"] - now).total_seconds()))
        r["time_remaining_seconds"] = time_rem

    return BookingListResponse(bookings=rows, total=len(rows))

@router.get("/{id}", response_model=BookingResponse)
async def get_booking_by_id(
    id: int,
    user: Dict[str, Any] = Depends(get_current_user),
):
    booking = await get_booking_details(id)
    if user["role"] != "ADMIN" and booking["user_id"] != user["id"]:
        from app.exceptions import ForbiddenError
        raise ForbiddenError("You cannot view this booking")
    return booking

@router.post("/{id}/cancel", response_model=BookingResponse)
async def cancel_user_booking(
    id: int,
    req: BookingCancelRequest,
    user: Dict[str, Any] = Depends(get_current_user),
):
    return await cancel_booking(
        booking_id=id,
        user_id=user["id"],
        user_role=user["role"],
        reason=req.reason,
    )
