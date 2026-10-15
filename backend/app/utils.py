import math
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional
import pytz
import dateparser
from app.config import settings

KOLKATA_TZ = pytz.timezone(settings.TIMEZONE)

def utc_now() -> datetime:
    """Returns the current UTC datetime without tzinfo for MySQL compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def to_kolkata_str(dt: Optional[datetime]) -> str:
    """Converts a UTC datetime to Asia/Kolkata formatted string."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(KOLKATA_TZ).strftime("%Y-%m-%d %I:%M %p")

def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def round_down_to_block(dt: datetime, granularity_mins: int = 15) -> datetime:
    """Rounds a datetime down to the nearest granularity block."""
    minute = (dt.minute // granularity_mins) * granularity_mins
    return dt.replace(minute=minute, second=0, microsecond=0)

def round_up_to_block(dt: datetime, granularity_mins: int = 15) -> datetime:
    """Rounds a datetime up to the nearest granularity block."""
    rem = dt.minute % granularity_mins or (1 if dt.second > 0 or dt.microsecond > 0 else 0)
    if rem == 0:
        return dt.replace(second=0, microsecond=0)
    added = granularity_mins - (dt.minute % granularity_mins)
    return (dt + timedelta(minutes=added)).replace(second=0, microsecond=0)

def generate_blocks(
    start_at: datetime,
    end_at: datetime,
    granularity_mins: int = 15,
) -> List[datetime]:
    """
    Generates a list of block_start datetimes covering [start_at, end_at).
    Every block is exactly `granularity_mins` minutes long.
    """
    blocks: List[datetime] = []
    # Ensure aligned to boundary
    current = round_down_to_block(start_at, granularity_mins)
    end_aligned = round_up_to_block(end_at, granularity_mins)

    step = timedelta(minutes=granularity_mins)
    while current < end_aligned:
        blocks.append(current)
        current += step

    return blocks

def parse_time_window(
    date_text: Optional[str] = None,
    start_time_text: Optional[str] = None,
    duration_mins: Optional[int] = None,
    end_time_text: Optional[str] = None,
) -> Tuple[datetime, datetime]:
    """
    Parses natural language date and time strings relative to Asia/Kolkata
    and returns (start_utc, end_utc) datetimes without tzinfo for MySQL.
    """
    now_kolkata = datetime.now(KOLKATA_TZ)
    
    parsed_start = None
    if date_text and start_time_text:
        combined = f"{date_text} {start_time_text}"
        parsed_start = dateparser.parse(
            combined,
            settings={"TIMEZONE": settings.TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True},
        )
    elif start_time_text:
        parsed_start = dateparser.parse(
            start_time_text,
            settings={"TIMEZONE": settings.TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True},
        )
    elif date_text:
        parsed_start = dateparser.parse(
            date_text,
            settings={"TIMEZONE": settings.TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True},
        )

    if not parsed_start or parsed_start < now_kolkata - timedelta(minutes=15):
        # Default to now + 15 min rounded
        parsed_start = now_kolkata + timedelta(minutes=15)

    duration = duration_mins or 120  # default 2 hours
    if end_time_text:
        parsed_end = dateparser.parse(
            end_time_text,
            settings={"TIMEZONE": settings.TIMEZONE, "RETURN_AS_TIMEZONE_AWARE": True},
        )
        if parsed_end and parsed_end > parsed_start:
            duration = int((parsed_end - parsed_start).total_seconds() / 60)

    # Convert to UTC and strip tzinfo
    start_utc = parsed_start.astimezone(pytz.utc).replace(tzinfo=None)
    start_utc = round_up_to_block(start_utc, settings.BOOKING_GRANULARITY_MINUTES)
    end_utc = start_utc + timedelta(minutes=duration)

    return start_utc, end_utc
