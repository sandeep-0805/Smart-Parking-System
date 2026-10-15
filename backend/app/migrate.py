import asyncio
import logging
import os
import re
from app.database import init_pool, close_pool, fetch_all, execute

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrator")

async def run_migrations():
    logger.info("Checking database migrations...")
    await init_pool()

    # Ensure schema_migrations table exists
    await execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version   INT          NOT NULL PRIMARY KEY,
            name      VARCHAR(255) NOT NULL,
            applied_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    )

    applied_rows = await fetch_all("SELECT version FROM schema_migrations ORDER BY version ASC")
    applied_versions = {r["version"] for r in applied_rows}
    logger.info(f"Currently applied migration versions: {applied_versions}")

    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    if os.path.exists(migrations_dir):
        files = sorted(os.listdir(migrations_dir))
        for f in files:
            m = re.match(r"^(\d+)_(.+)\.sql$", f)
            if m:
                version = int(m.group(1))
                name = m.group(2)
                if version not in applied_versions:
                    logger.info(f"Applying migration {f}...")
                    sql_path = os.path.join(migrations_dir, f)
                    with open(sql_path, "r", encoding="utf-8") as sql_file:
                        statements = [stmt.strip() for stmt in sql_file.read().split(";") if stmt.strip()]
                    for stmt in statements:
                        await execute(stmt)
                    await execute(
                        "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
                        (version, name),
                    )
                    logger.info(f"Successfully applied migration {f}.")

    logger.info("All migrations up to date.")
    await close_pool()

if __name__ == "__main__":
    asyncio.run(run_migrations())
