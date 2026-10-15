import logging
from contextlib import asynccontextmanager
from typing import Any, List, Optional, Dict, Tuple
import aiomysql
from app.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[aiomysql.Pool] = None

async def init_pool():
    global _pool
    logger.info(f"Connecting to MySQL at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}...")
    _pool = await aiomysql.create_pool(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DATABASE,
        charset="utf8mb4",
        autocommit=True,
        minsize=5,
        maxsize=25,
        pool_recycle=3600,
        cursorclass=aiomysql.DictCursor,
    )
    logger.info("MySQL connection pool established successfully (no SQLAlchemy).")

async def close_pool():
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
        logger.info("MySQL connection pool closed.")

@asynccontextmanager
async def get_conn():
    if not _pool:
        raise RuntimeError("Database connection pool is not initialized")
    async with _pool.acquire() as conn:
        yield conn

@asynccontextmanager
async def transaction():
    """
    Async transaction context manager.
    Begins transaction, yields connection, commits on clean exit, rolls back on exception.
    """
    if not _pool:
        raise RuntimeError("Database connection pool is not initialized")
    async with _pool.acquire() as conn:
        await conn.begin()
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise

async def fetch_one(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
    conn: Optional[aiomysql.Connection] = None,
) -> Optional[Dict[str, Any]]:
    if conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params or ())
            return await cur.fetchone()
    async with get_conn() as c:
        async with c.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params or ())
            return await cur.fetchone()

async def fetch_all(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
    conn: Optional[aiomysql.Connection] = None,
) -> List[Dict[str, Any]]:
    if conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params or ())
            return await cur.fetchall()
    async with get_conn() as c:
        async with c.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params or ())
            return await cur.fetchall()

async def execute(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
    conn: Optional[aiomysql.Connection] = None,
) -> Tuple[int, int]:
    """
    Executes an INSERT/UPDATE/DELETE.
    Returns (lastrowid, rowcount).
    """
    if conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params or ())
            return cur.lastrowid or 0, cur.rowcount
    async with get_conn() as c:
        async with c.cursor() as cur:
            await cur.execute(query, params or ())
            return cur.lastrowid or 0, cur.rowcount

async def execute_many(
    query: str,
    params_list: List[Tuple[Any, ...]],
    conn: Optional[aiomysql.Connection] = None,
) -> int:
    """Batch execute statement. Returns affected rowcount."""
    if not params_list:
        return 0
    if conn:
        async with conn.cursor() as cur:
            await cur.executemany(query, params_list)
            return cur.rowcount
    async with get_conn() as c:
        async with c.cursor() as cur:
            await cur.executemany(query, params_list)
            return cur.rowcount

async def check_db_health() -> bool:
    try:
        row = await fetch_one("SELECT 1 AS healthy")
        return bool(row and row.get("healthy") == 1)
    except Exception as e:
        logger.error(f"DB healthcheck failed: {e}")
        return False
