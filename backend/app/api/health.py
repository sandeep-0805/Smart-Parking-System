from fastapi import APIRouter
from app.database import check_db_health
from app.redis_client import check_redis_health

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health():
    return {"status": "ok", "service": "smart-parking-backend"}

@router.get("/ready")
async def ready():
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()

    status_str = "ready" if (db_ok and redis_ok) else "degraded"
    return {
        "status": status_str,
        "database": db_ok,
        "redis": redis_ok,
    }
