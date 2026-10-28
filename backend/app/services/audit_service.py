import json
import logging
from typing import Optional, Any
from app.database import execute

logger = logging.getLogger("audit_service")

async def log_audit_event(
    action: str,
    resource_type: str,
    user_id: Optional[int] = None,
    resource_id: Optional[int] = None,
    details: Optional[Any] = None,
    ip_address: Optional[str] = None,
):
    try:
        details_json = json.dumps(details) if details is not None else None
        await execute(
            """
            INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, resource_type, resource_id, details_json, ip_address),
        )
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")
