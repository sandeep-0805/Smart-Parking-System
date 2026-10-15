import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pymysql.err

from app.config import settings
from app.database import fetch_one, fetch_all, execute, execute_many, transaction, get_conn
from app.exceptions import NotFoundError, SlotTakenError, ForbiddenError, AppException
from app.services.pricing_service import validate_quote
from app.utils import utc_now, generate_blocks

logger = logging.getLogger("booking_service")

async def create_booking_reservation(
    user_id: int,
    quote_id: int,
    idempotency_key: Optional[str] = None,
    source: str = "MANUAL",
) -> Dict[str, Any]:
    # 1. Idempotency fast path check
    if idempotency_key:
        existing = await fetch_one(
            "SELECT id FROM bookings WHERE user_id = %s AND idempotency_key = %s",
            (user_id, idempotency_key),
        )
        if existing:
            return await get_booking_details(existing["id"])

    # 2. Check per-user pending booking limit
    pending_count_row = await fetch_one(
        "SELECT COUNT(*) as cnt FROM bookings WHERE user_id = %s AND status = 'PENDING_PAYMENT' AND hold_expires_at > %s",
        (user_id, utc_now()),
    )
    if pending_count_row and pending_count_row["cnt"] >= settings.PER_USER_PENDING_LIMIT:
        raise AppException(
            400,
            "PENDING_LIMIT_REACHED",
            f"You already have {pending_count_row['cnt']} pending bookings awaiting payment. Please pay or cancel them first.",
        )

    # 3. Validate quote
    quote = await validate_quote(quote_id)
    slot_id = quote["slot_id"]
    start_at = quote["start_at"]
    end_at = quote["end_at"]
    total_paise = quote["total_paise"]

    # Generate 15-minute time blocks
    blocks = generate_blocks(start_at, end_at, settings.BOOKING_GRANULARITY_MINUTES)
    if not blocks:
        raise AppException(400, "INVALID_WINDOW", "Booking window is empty or too short")

    # 4. Transactional reserve with deadlock retry (up to 3 attempts)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with transaction() as conn:
                now = utc_now()
                # a. Row lock on parking slot
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT id, location_id, status FROM parking_slots WHERE id = %s FOR UPDATE",
                        (slot_id,),
                    )
                    slot_row = await cur.fetchone()
                
                if not slot_row:
                    raise NotFoundError(f"Slot {slot_id} not found")
                if slot_row["status"] != "ACTIVE":
                    raise AppException(409, "SLOT_NOT_ACTIVE", "This slot is currently blocked or inactive")

                # b. Clean up expired holds for this slot inside transaction
                await execute(
                    """
                    DELETE bb FROM booking_blocks bb
                    JOIN bookings b ON bb.booking_id = b.id
                    WHERE bb.slot_id = %s
                      AND b.status = 'PENDING_PAYMENT'
                      AND b.hold_expires_at <= %s
                    """,
                    (slot_id, now),
                    conn=conn,
                )
                await execute(
                    """
                    UPDATE bookings
                    SET status = 'EXPIRED'
                    WHERE slot_id = %s
                      AND status = 'PENDING_PAYMENT'
                      AND hold_expires_at <= %s
                    """,
                    (slot_id, now),
                    conn=conn,
                )

                # c. Check if any conflicting block exists
                block_placeholders = ",".join(["%s"] * len(blocks))
                conflict_query = f"""
                SELECT COUNT(*) as cnt
                FROM booking_blocks
                WHERE slot_id = %s AND block_start IN ({block_placeholders})
                """
                conflict_params = [slot_id] + blocks
                async with conn.cursor() as cur:
                    await cur.execute(conflict_query, tuple(conflict_params))
                    conf_res = await cur.fetchone()
                    if conf_res and conf_res["cnt"] > 0:
                        raise SlotTakenError("Slot is no longer available for the requested time window")

                # d. Check location pay_at_venue setting
                loc_row = await fetch_one(
                    "SELECT pay_at_venue FROM parking_locations WHERE id = %s",
                    (slot_row["location_id"],),
                    conn=conn,
                )
                is_pay_at_venue = bool(loc_row and loc_row.get("pay_at_venue"))

                initial_status = "CONFIRMED" if is_pay_at_venue else "PENDING_PAYMENT"
                hold_expires_at = None if is_pay_at_venue else (now + timedelta(minutes=settings.HOLD_MINUTES))

                # e. Insert booking record
                insert_booking_query = """
                INSERT INTO bookings (
                    user_id, slot_id, quote_id, start_at, end_at,
                    status, total_paise, hold_expires_at, source, idempotency_key
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                booking_id, _ = await execute(
                    insert_booking_query,
                    (
                        user_id,
                        slot_id,
                        quote_id,
                        start_at,
                        end_at,
                        initial_status,
                        total_paise,
                        hold_expires_at,
                        source,
                        idempotency_key,
                    ),
                    conn=conn,
                )

                # f. Insert booking blocks (guarded by UNIQUE KEY uq_slot_block)
                block_records = [(slot_id, b, booking_id) for b in blocks]
                await execute_many(
                    "INSERT INTO booking_blocks (slot_id, block_start, booking_id) VALUES (%s, %s, %s)",
                    block_records,
                    conn=conn,
                )

            # Success! Break out of retry loop
            return await get_booking_details(booking_id)

        except pymysql.err.IntegrityError as e:
            # Duplicate key error on uq_slot_block or idempotency
            logger.warning(f"Integrity error during reservation: {e}")
            raise SlotTakenError("Slot is no longer available for the requested time window")
        except pymysql.err.OperationalError as e:
            # Deadlock error 1213
            if e.args[0] == 1213 and attempt < max_retries - 1:
                logger.info(f"Deadlock detected on attempt {attempt+1}. Retrying in 50ms...")
                await asyncio.sleep(0.05 * (2 ** attempt))
                continue
            raise

    raise SlotTakenError("Slot booking contention, please try again")

async def get_booking_details(booking_id: int) -> Dict[str, Any]:
    row = await fetch_one(
        """
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
        WHERE b.id = %s
        """,
        (booking_id,),
    )
    if not row:
        raise NotFoundError(f"Booking {booking_id} not found")

    # Calculate remaining time if pending payment
    time_rem = 0
    if row["status"] == "PENDING_PAYMENT" and row["hold_expires_at"]:
        diff = (row["hold_expires_at"] - utc_now()).total_seconds()
        time_rem = max(0, int(diff))

    row["time_remaining_seconds"] = time_rem
    return row

async def cancel_booking(
    booking_id: int,
    user_id: int,
    user_role: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    booking = await get_booking_details(booking_id)
    if user_role != "ADMIN" and booking["user_id"] != user_id:
        raise ForbiddenError("You cannot cancel another user's booking")

    if booking["status"] not in ("PENDING_PAYMENT", "CONFIRMED"):
        raise AppException(
            400,
            "INVALID_STATUS",
            f"Cannot cancel booking with current status '{booking['status']}'",
        )

    now = utc_now()
    refund_pct = 0.0
    if booking["status"] == "CONFIRMED":
        # Check cancellation policy (FR-B6)
        minutes_until_start = (booking["start_at"] - now).total_seconds() / 60.0
        if minutes_until_start >= 60:
            refund_pct = 1.0  # 100% refund
        elif minutes_until_start > 0:
            refund_pct = 0.5  # 50% refund
        else:
            refund_pct = 0.0  # No refund after start

    async with transaction() as conn:
        # Delete blocks in same transaction
        await execute(
            "DELETE FROM booking_blocks WHERE booking_id = %s",
            (booking_id,),
            conn=conn,
        )
        await execute(
            """
            UPDATE bookings
            SET status = 'CANCELLED', cancellation_reason = %s
            WHERE id = %s
            """,
            (reason or f"Cancelled by user (refund {int(refund_pct*100)}%)", booking_id),
            conn=conn,
        )

    # Process refund asynchronously if needed
    if refund_pct > 0:
        from app.services.payment_service import process_cancellation_refund
        await process_cancellation_refund(booking_id, refund_pct)

    return await get_booking_details(booking_id)

async def expire_unpaid_holds():
    """Worker background job running every 60s."""
    now = utc_now()
    rows = await fetch_all(
        "SELECT id FROM bookings WHERE status = 'PENDING_PAYMENT' AND hold_expires_at <= %s",
        (now,),
    )
    if not rows:
        return 0

    expired_ids = [r["id"] for r in rows]
    for b_id in expired_ids:
        try:
            async with transaction() as conn:
                await execute("DELETE FROM booking_blocks WHERE booking_id = %s", (b_id,), conn=conn)
                await execute("UPDATE bookings SET status = 'EXPIRED' WHERE id = %s AND status = 'PENDING_PAYMENT'", (b_id,), conn=conn)
        except Exception as e:
            logger.error(f"Error expiring hold {b_id}: {e}")

    logger.info(f"Expired {len(expired_ids)} unpaid parking holds.")
    return len(expired_ids)
