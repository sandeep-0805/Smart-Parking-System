import json
import logging
from typing import Dict, Any, Optional
from email.message import EmailMessage
import aiosmtplib

from app.config import settings
from app.database import execute, fetch_one

logger = logging.getLogger("notification_service")

async def send_in_app_notification(
    user_id: int,
    type_str: str,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
):
    await execute(
        """
        INSERT INTO notifications (user_id, type, title, message, is_read, data)
        VALUES (%s, %s, %s, %s, 0, %s)
        """,
        (user_id, type_str, title, message, json.dumps(data) if data else None),
    )

async def send_email_async(to_email: str, subject: str, body_text: str):
    if not settings.SMTP_HOST:
        return
    try:
        msg = EmailMessage()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body_text)

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            use_tls=settings.SMTP_TLS,
        )
        logger.info(f"Sent notification email to {to_email}")
    except Exception as e:
        logger.warning(f"Failed to send email to {to_email}: {e}")

async def send_booking_confirmed_notification(booking_id: int):
    row = await fetch_one(
        """
        SELECT b.id, b.user_id, b.total_paise, s.code, l.name, u.email
        FROM bookings b
        JOIN parking_slots s ON b.slot_id = s.id
        JOIN parking_locations l ON s.location_id = l.id
        JOIN users u ON b.user_id = u.id
        WHERE b.id = %s
        """,
        (booking_id,),
    )
    if not row:
        return

    title = f"Booking #{row['id']} Confirmed!"
    msg = f"Your parking slot {row['code']} at {row['name']} has been confirmed. Total paid: ₹{row['total_paise']/100:.2f}."
    
    await send_in_app_notification(
        user_id=row["user_id"],
        type_str="BOOKING_CONFIRMED",
        title=title,
        message=msg,
        data={"booking_id": booking_id},
    )
    if row.get("email"):
        await send_email_async(row["email"], title, msg)

async def send_auto_booking_notification(user_id: int, booking: Dict[str, Any]):
    user = await fetch_one("SELECT email FROM users WHERE id = %s", (user_id,))
    title = f"Auto-Booking Created: Slot {booking.get('slot_code')}"
    msg = (
        f"SmartParking has reserved slot {booking.get('slot_code')} at {booking.get('location_name')} "
        f"for ₹{booking.get('total_paise', 0)/100:.2f}. Please confirm and complete payment before expiry."
    )
    await send_in_app_notification(
        user_id=user_id,
        type_str="AUTO_BOOKING_CREATED",
        title=title,
        message=msg,
        data={"booking_id": booking.get("id")},
    )
    if user and user.get("email"):
        await send_email_async(user["email"], title, msg)
