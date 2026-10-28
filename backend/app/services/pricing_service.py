import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple, List
from app.config import settings
from app.database import fetch_one, execute
from app.exceptions import NotFoundError, QuoteExpiredError, AppException
from app.utils import utc_now

async def calculate_quote_for_slot(
    slot_id: int,
    start_at: datetime,
    end_at: datetime,
) -> Dict[str, Any]:
    min_secs = settings.MIN_DURATION_MINUTES * 60
    if end_at <= start_at or (end_at - start_at).total_seconds() < min_secs:
        raise AppException(400, "INVALID_TIME_WINDOW", f"Booking duration must be at least {settings.MIN_DURATION_MINUTES} minutes")
    # Look up slot and its location rates
    slot_row = await fetch_one(
        """
        SELECT s.id as slot_id, s.code as slot_code, s.location_id, s.vehicle_type, s.status as slot_status,
               l.name as location_name, l.base_rate_paise, l.min_rate_paise,
               l.max_rate_paise, l.total_slots
        FROM parking_slots s
        JOIN parking_locations l ON s.location_id = l.id
        WHERE s.id = %s
        """,
        (slot_id,),
    )
    if not slot_row:
        raise NotFoundError(f"Slot {slot_id} not found")

    location_id = slot_row["location_id"]
    total_slots = max(1, slot_row["total_slots"] or 1)
    veh_type = slot_row.get("vehicle_type", "CAR")

    # 1. Compute current active occupancy ratio for location
    # Count distinct slots booked during this requested window
    occ_row = await fetch_one(
        """
        SELECT COUNT(DISTINCT slot_id) as occupied_count
        FROM booking_blocks
        WHERE slot_id IN (SELECT id FROM parking_slots WHERE location_id = %s)
          AND block_start >= %s AND block_start < %s
        """,
        (location_id, start_at, end_at),
    )
    occupied_count = occ_row["occupied_count"] if occ_row else 0
    occupancy_pct = occupied_count / float(total_slots)

    # 2. Vehicle-type and demand-based multipliers
    base_rate = slot_row["base_rate_paise"]
    min_rate = slot_row["min_rate_paise"]
    max_rate = slot_row["max_rate_paise"]

    # Vehicle type multiplier (e.g. 2-wheelers pay 40% of car rates)
    VEHICLE_MULTIPLIERS = {
        "MOTORCYCLE": 0.40,
        "CAR": 1.00,
        "SUV": 1.20,
        "EV": 1.10,
        "TRUCK": 1.50,
    }
    veh_mult = VEHICLE_MULTIPLIERS.get(veh_type, 1.00)

    if occupancy_pct < 0.50:
        multiplier = 1.0
        band_name = "Standard Demand (<50%)"
    elif occupancy_pct <= 0.80:
        multiplier = 1.15
        band_name = "Moderate Demand (50-80%)"
    else:
        multiplier = 1.30
        band_name = "High Demand (>80%)"

    effective_hourly = int(round(base_rate * veh_mult * multiplier))
    min_allowed = int(round(min_rate * veh_mult))
    max_allowed = int(round(max_rate * veh_mult))
    effective_hourly = max(min_allowed, min(max_allowed, effective_hourly))

    duration_mins = int((end_at - start_at).total_seconds() / 60)
    duration_hours = max(0.5, duration_mins / 60.0)

    total_paise = int(round(effective_hourly * duration_hours))

    line_items = [
        {
            "label": f"{veh_type.capitalize()} parking ({duration_hours:.1f} hrs @ ₹{effective_hourly / 100:.2f}/hr)",
            "amount_paise": total_paise,
            "vehicle_type": veh_type,
            "band": band_name,
            "multiplier": multiplier,
        }
    ]

    valid_until = utc_now() + timedelta(minutes=settings.HOLD_MINUTES)

    # Insert into price_quotes table
    last_id, _ = await execute(
        """
        INSERT INTO price_quotes (slot_id, start_at, end_at, total_paise, line_items, valid_until, rule_version)
        VALUES (%s, %s, %s, %s, %s, %s, 'v1')
        """,
        (
            slot_id,
            start_at,
            end_at,
            total_paise,
            json.dumps(line_items),
            valid_until,
        ),
    )

    return {
        "id": last_id,
        "slot_id": slot_id,
        "slot_code": slot_row["slot_code"],
        "location_name": slot_row["location_name"],
        "start_at": start_at,
        "end_at": end_at,
        "total_paise": total_paise,
        "line_items": line_items,
        "valid_until": valid_until,
        "rule_version": "v1",
    }

async def validate_quote(quote_id: int) -> Dict[str, Any]:
    row = await fetch_one("SELECT * FROM price_quotes WHERE id = %s", (quote_id,))
    if not row:
        raise NotFoundError("Price quote not found")

    now = utc_now()
    if row["valid_until"] < now:
        raise QuoteExpiredError("Price quote has expired. Please refresh search to get an updated quote.")

    if isinstance(row["line_items"], str):
        row["line_items"] = json.loads(row["line_items"])
    return row
