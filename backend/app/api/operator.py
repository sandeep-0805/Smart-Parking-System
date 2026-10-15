from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.dependencies import require_role
from app.database import fetch_all, fetch_one
from app.schemas.operator import OperatorDashboardResponse, OperatorLocationStats
from app.utils import utc_now

router = APIRouter(prefix="/operator", tags=["Operator"])

@router.get("/dashboard", response_model=OperatorDashboardResponse)
async def get_operator_dashboard(user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN"))):
    owner_id = user["id"]
    is_admin = (user["role"] == "ADMIN")

    where_loc = "" if is_admin else "WHERE owner_id = %s"
    loc_params = () if is_admin else (owner_id,)

    locations = await fetch_all(
        f"SELECT id, name, total_slots, base_rate_paise, status FROM parking_locations {where_loc}",
        loc_params,
    )

    if not locations:
        return OperatorDashboardResponse(
            total_locations=0,
            total_slots=0,
            occupied_slots=0,
            overall_occupancy_pct=0.0,
            today_bookings_count=0,
            today_revenue_paise=0,
            locations=[],
            recent_bookings=[],
        )

    loc_ids = [l["id"] for l in locations]
    loc_ids_str = ",".join(map(str, loc_ids))
    now = utc_now()

    # Active blocks right now
    occ_rows = await fetch_all(
        f"""
        SELECT s.location_id, COUNT(DISTINCT bb.slot_id) as occ_cnt
        FROM booking_blocks bb
        JOIN parking_slots s ON bb.slot_id = s.id
        WHERE s.location_id IN ({loc_ids_str})
          AND bb.block_start <= %s AND bb.block_start > DATE_SUB(%s, INTERVAL 15 MINUTE)
        GROUP BY s.location_id
        """,
        (now, now),
    )
    occ_map = {r["location_id"]: r["occ_cnt"] for r in occ_rows}

    # Revenue today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    rev_rows = await fetch_all(
        f"""
        SELECT s.location_id, COUNT(b.id) as b_cnt, COALESCE(SUM(b.total_paise), 0) as rev_paise
        FROM bookings b
        JOIN parking_slots s ON b.slot_id = s.id
        WHERE s.location_id IN ({loc_ids_str})
          AND b.status IN ('CONFIRMED', 'COMPLETED')
          AND b.created_at >= %s
        GROUP BY s.location_id
        """,
        (today_start,),
    )
    rev_map = {r["location_id"]: r for r in rev_rows}

    total_slots = sum(l["total_slots"] for l in locations)
    total_occupied = sum(occ_map.get(l["id"], 0) for l in locations)
    total_revenue = sum(int(rev_map.get(l["id"], {}).get("rev_paise", 0)) for l in locations)
    total_bookings = sum(int(rev_map.get(l["id"], {}).get("b_cnt", 0)) for l in locations)

    loc_stats: List[OperatorLocationStats] = []
    for l in locations:
        lid = l["id"]
        tslots = l["total_slots"] or 1
        occ = occ_map.get(lid, 0)
        avail = max(0, tslots - occ)
        loc_rev = int(rev_map.get(lid, {}).get("rev_paise", 0))
        pct = round(occ / float(tslots), 4)

        loc_stats.append(OperatorLocationStats(
            location_id=lid,
            name=l["name"],
            total_slots=tslots,
            occupied_slots=occ,
            available_slots=avail,
            occupancy_pct=pct,
            today_revenue_paise=loc_rev,
            status=l["status"],
        ))

    recent_b = await fetch_all(
        f"""
        SELECT b.id, b.status, b.total_paise, b.start_at, b.end_at, b.created_at,
               s.code as slot_code, l.name as location_name
        FROM bookings b
        JOIN parking_slots s ON b.slot_id = s.id
        JOIN parking_locations l ON s.location_id = l.id
        WHERE s.location_id IN ({loc_ids_str})
        ORDER BY b.id DESC LIMIT 10
        """
    )

    return OperatorDashboardResponse(
        total_locations=len(locations),
        total_slots=total_slots,
        occupied_slots=total_occupied,
        overall_occupancy_pct=round(total_occupied / float(max(1, total_slots)), 4),
        today_bookings_count=total_bookings,
        today_revenue_paise=total_revenue,
        locations=loc_stats,
        recent_bookings=recent_b,
    )

@router.get("/bookings")
async def get_operator_bookings(user: Dict[str, Any] = Depends(require_role("OPERATOR", "ADMIN"))):
    owner_id = user["id"]
    is_admin = (user["role"] == "ADMIN")
    where_clause = "" if is_admin else "WHERE l.owner_id = %s"
    params = () if is_admin else (owner_id,)

    query = f"""
    SELECT b.id, b.user_id, b.start_at, b.end_at, b.status, b.total_paise, b.created_at,
           s.code as slot_code, s.vehicle_type, l.name as location_name
    FROM bookings b
    JOIN parking_slots s ON b.slot_id = s.id
    JOIN parking_locations l ON s.location_id = l.id
    {where_clause}
    ORDER BY b.id DESC LIMIT 100
    """
    return await fetch_all(query, params)
