import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import pytz

from app.config import settings
from app.database import fetch_all, fetch_one, execute
from app.services.booking_service import create_booking_reservation
from app.services.search_service import search_parking
from app.services.notification_service import send_auto_booking_notification
from app.utils import utc_now

logger = logging.getLogger("auto_booking_service")
KOLKATA_TZ = pytz.timezone(settings.TIMEZONE)

async def evaluate_auto_booking_rules():
    """Worker background job checking enabled rules."""
    now_utc = utc_now()
    now_kolkata = datetime.now(KOLKATA_TZ)
    current_weekday = now_kolkata.weekday()  # 0=Monday, 6=Sunday

    rules = await fetch_all("SELECT * FROM auto_booking_rules WHERE enabled = 1")
    if not rules:
        return 0

    executed_count = 0
    for r in rules:
        try:
            rule_id = r["id"]
            user_id = r["user_id"]
            cfg = json.loads(r["rule"]) if isinstance(r["rule"], str) else r["rule"]
            lead_mins = r["lead_time_minutes"]
            weekly_cap = r["weekly_booking_cap"]

            # 1. Check if today matches rule active days
            active_days = cfg.get("days", [0, 1, 2, 3, 4, 5, 6])
            if current_weekday not in active_days:
                continue

            # 2. Check weekly booking cap
            week_start = now_utc - timedelta(days=7)
            cap_row = await fetch_one(
                "SELECT COUNT(*) as cnt FROM bookings WHERE user_id = %s AND source = 'AUTO' AND created_at >= %s",
                (user_id, week_start),
            )
            if cap_row and cap_row["cnt"] >= weekly_cap:
                await log_auto_booking_audit(
                    rule_id=rule_id,
                    user_id=user_id,
                    decision="WEEKLY_CAP_EXCEEDED",
                    decision_reason=f"Reached weekly limit of {weekly_cap} auto-bookings",
                    rule_snapshot=cfg,
                )
                continue

            # 3. Check target time window
            start_time_str = cfg.get("start_time", "09:00")
            target_start = now_kolkata + timedelta(minutes=lead_mins)
            
            # Run search for candidate
            search_res = await search_parking(
                user_preferences={"default_vehicle_type": cfg.get("vehicle_type", "CAR")},
                place_name=cfg.get("location_name") or cfg.get("area"),
                date_text="today",
                start_time_text=start_time_str,
                duration_minutes=cfg.get("duration_minutes", 120),
                vehicle_type=cfg.get("vehicle_type", "CAR"),
                max_budget_paise=cfg.get("max_price_paise"),
                facilities=cfg.get("facilities", []),
            )

            locations = search_res.get("locations", [])
            if not locations:
                await log_auto_booking_audit(
                    rule_id=rule_id,
                    user_id=user_id,
                    decision="NO_CANDIDATES",
                    decision_reason="No available slots matching criteria found",
                    rule_snapshot=cfg,
                )
                continue

            # Select top ranked slot
            best_loc = locations[0]
            best_slot = best_loc["slots"][0]

            # Price check
            if cfg.get("max_price_paise") and best_slot["total_price_paise"] > cfg["max_price_paise"]:
                await log_auto_booking_audit(
                    rule_id=rule_id,
                    user_id=user_id,
                    decision="PRICE_CAP_EXCEEDED",
                    decision_reason=f"Quoted price ₹{best_slot['total_price_paise']/100:.2f} exceeded cap",
                    rule_snapshot=cfg,
                )
                continue

            # 4. Reserve through standard transactional service
            booking = await create_booking_reservation(
                user_id=user_id,
                quote_id=best_slot["quote_id"],
                source="AUTO",
            )

            await log_auto_booking_audit(
                rule_id=rule_id,
                user_id=user_id,
                candidates_count=len(locations),
                selected_slot_id=best_slot["slot_id"],
                selected_location_id=best_loc["location_id"],
                booking_id=booking["id"],
                decision="BOOKED",
                decision_reason=f"Auto-booked slot {best_slot['slot_code']} at {best_loc['name']}",
                rule_snapshot=cfg,
            )

            await send_auto_booking_notification(user_id, booking)
            executed_count += 1

        except Exception as e:
            logger.error(f"Error evaluating rule {r['id']}: {e}")

    return executed_count

async def log_auto_booking_audit(
    rule_id: int,
    user_id: int,
    decision: str,
    decision_reason: str,
    rule_snapshot: Dict[str, Any],
    candidates_count: int = 0,
    selected_slot_id: Optional[int] = None,
    selected_location_id: Optional[int] = None,
    booking_id: Optional[int] = None,
):
    await execute(
        """
        INSERT INTO auto_booking_audit (
            rule_id, user_id, candidates_count, selected_slot_id,
            selected_location_id, booking_id, decision, decision_reason, rule_snapshot
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            rule_id,
            user_id,
            candidates_count,
            selected_slot_id,
            selected_location_id,
            booking_id,
            decision,
            decision_reason,
            json.dumps(rule_snapshot),
        ),
    )
