import json
from typing import List, Dict, Any, Optional
from app.database import fetch_one, fetch_all, execute
from app.exceptions import NotFoundError, ForbiddenError
from app.schemas.locations import LocationCreate, LocationUpdate

async def create_location(owner_id: int, req: LocationCreate) -> Dict[str, Any]:
    point_wkt = f"POINT({req.lng} {req.lat})"
    hours_json = json.dumps(req.operating_hours)
    fac_json = json.dumps(req.facilities)

    query = """
    INSERT INTO parking_locations (
        owner_id, name, address, lat, lng, location_point,
        operating_hours, facilities, base_rate_paise, min_rate_paise,
        max_rate_paise, rate_update_interval_min, pay_at_venue, status
    ) VALUES (
        %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326),
        %s, %s, %s, %s, %s, %s, %s, 'PENDING'
    )
    """
    last_id, _ = await execute(
        query,
        (
            owner_id,
            req.name,
            req.address,
            req.lat,
            req.lng,
            point_wkt,
            hours_json,
            fac_json,
            req.base_rate_paise,
            req.min_rate_paise,
            req.max_rate_paise,
            req.rate_update_interval_min,
            1 if req.pay_at_venue else 0,
        ),
    )
    return await get_location(last_id)

async def get_location(location_id: int) -> Dict[str, Any]:
    row = await fetch_one(
        """
        SELECT id, owner_id, name, address, lat, lng, operating_hours,
               facilities, base_rate_paise, min_rate_paise, max_rate_paise,
               rate_update_interval_min, pay_at_venue, status, total_slots, created_at
        FROM parking_locations
        WHERE id = %s
        """,
        (location_id,),
    )
    if not row:
        raise NotFoundError("Location not found")
    
    # Parse JSON fields if string
    if isinstance(row["operating_hours"], str):
        row["operating_hours"] = json.loads(row["operating_hours"])
    if isinstance(row["facilities"], str):
        row["facilities"] = json.loads(row["facilities"])
    return row

async def update_location(
    location_id: int,
    user_id: int,
    user_role: str,
    req: LocationUpdate,
) -> Dict[str, Any]:
    loc = await get_location(location_id)
    if user_role != "ADMIN" and loc["owner_id"] != user_id:
        raise ForbiddenError("You do not own this parking location")

    updates = []
    params = []

    if req.name is not None:
        updates.append("name = %s")
        params.append(req.name)
    if req.address is not None:
        updates.append("address = %s")
        params.append(req.address)
    if req.lat is not None and req.lng is not None:
        updates.append("lat = %s, lng = %s, location_point = ST_GeomFromText(%s, 4326)")
        params.extend([req.lat, req.lng, f"POINT({req.lng} {req.lat})"])
    if req.operating_hours is not None:
        updates.append("operating_hours = %s")
        params.append(json.dumps(req.operating_hours))
    if req.facilities is not None:
        updates.append("facilities = %s")
        params.append(json.dumps(req.facilities))
    if req.base_rate_paise is not None:
        updates.append("base_rate_paise = %s")
        params.append(req.base_rate_paise)
    if req.min_rate_paise is not None:
        updates.append("min_rate_paise = %s")
        params.append(req.min_rate_paise)
    if req.max_rate_paise is not None:
        updates.append("max_rate_paise = %s")
        params.append(req.max_rate_paise)
    if req.rate_update_interval_min is not None:
        updates.append("rate_update_interval_min = %s")
        params.append(req.rate_update_interval_min)
    if req.pay_at_venue is not None:
        updates.append("pay_at_venue = %s")
        params.append(1 if req.pay_at_venue else 0)

    if updates:
        params.append(location_id)
        query = f"UPDATE parking_locations SET {', '.join(updates)} WHERE id = %s"
        await execute(query, tuple(params))

    return await get_location(location_id)

async def list_locations(
    owner_id: Optional[int] = None,
    status_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conditions = []
    params = []

    if owner_id:
        conditions.append("owner_id = %s")
        params.append(owner_id)
    if status_filter:
        conditions.append("status = %s")
        params.append(status_filter)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
    SELECT id, owner_id, name, address, lat, lng, operating_hours,
           facilities, base_rate_paise, min_rate_paise, max_rate_paise,
           rate_update_interval_min, pay_at_venue, status, total_slots, created_at
    FROM parking_locations
    {where_clause}
    ORDER BY id DESC
    """
    rows = await fetch_all(query, tuple(params) if params else None)
    for r in rows:
        if isinstance(r["operating_hours"], str):
            r["operating_hours"] = json.loads(r["operating_hours"])
        if isinstance(r["facilities"], str):
            r["facilities"] = json.loads(r["facilities"])
    return rows

async def approve_location(location_id: int) -> Dict[str, Any]:
    await execute("UPDATE parking_locations SET status = 'APPROVED' WHERE id = %s", (location_id,))
    return await get_location(location_id)

async def delete_location(location_id: int):
    await execute("DELETE FROM parking_locations WHERE id = %s", (location_id,))
