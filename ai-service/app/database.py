import logging
from typing import Any, List, Optional, Dict
import aiomysql
from app.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[aiomysql.Pool] = None

async def init_pool():
    global _pool
    try:
        _pool = await aiomysql.create_pool(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_AI_USER,
            password=settings.MYSQL_AI_PASSWORD,
            db=settings.MYSQL_DATABASE,
            charset="utf8mb4",
            autocommit=True,
            minsize=2,
            maxsize=10,
            cursorclass=aiomysql.DictCursor,
        )
        logger.info("AI service DB pool initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize AI DB pool: {e}")
        _pool = None

async def close_pool():
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
        logger.info("AI service DB pool closed.")

async def fetch_one(query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    if not _pool:
        return None
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params or ())
            return await cur.fetchone()

async def fetch_all(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    if not _pool:
        return []
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params or ())
            return await cur.fetchall()

async def check_db_health() -> bool:
    try:
        res = await fetch_one("SELECT 1 as healthy")
        return bool(res and res.get("healthy") == 1)
    except Exception:
        return False
