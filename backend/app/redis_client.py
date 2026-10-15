import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None

async def init_redis():
    global _redis_client
    logger.info(f"Connecting to Redis at {settings.REDIS_URL}...")
    _redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await _redis_client.ping()
    logger.info("Redis connected successfully.")

async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed.")

def get_redis() -> redis.Redis:
    if not _redis_client:
        raise RuntimeError("Redis client is not initialized")
    return _redis_client

async def set_cache(key: str, value: Any, ttl_seconds: Optional[int] = None):
    r = get_redis()
    serialized = json.dumps(value) if not isinstance(value, str) else value
    if ttl_seconds:
        await r.setex(key, ttl_seconds, serialized)
    else:
        await r.set(key, serialized)

async def get_cache(key: str) -> Optional[Any]:
    r = get_redis()
    val = await r.get(key)
    if val is None:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val

async def delete_cache(key: str):
    r = get_redis()
    await r.delete(key)

# ── Token Denylist ───────────────────────────────────────────
async def deny_token(jti: str, ttl_seconds: int):
    r = get_redis()
    await r.setex(f"denylist:{jti}", ttl_seconds, "1")

async def is_token_denied(jti: str) -> bool:
    r = get_redis()
    return bool(await r.exists(f"denylist:{jti}"))

# ── Rate Limiting ─────────────────────────────────────────────
async def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> bool:
    """
    Sliding/fixed window rate limiter.
    Returns True if allowed, False if exceeded.
    """
    r = get_redis()
    redis_key = f"rl:{key}"
    count = await r.incr(redis_key)
    if count == 1:
        await r.expire(redis_key, window_seconds)
    return count <= limit

async def check_redis_health() -> bool:
    try:
        r = get_redis()
        return await r.ping()
    except Exception as e:
        logger.error(f"Redis healthcheck failed: {e}")
        return False
