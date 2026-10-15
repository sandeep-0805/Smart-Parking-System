import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import init_pool, close_pool, fetch_all, execute
from app.redis_client import init_redis, close_redis
from app.services.booking_service import expire_unpaid_holds
from app.services.auto_booking_service import evaluate_auto_booking_rules
from app.utils import utc_now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

async def take_occupancy_snapshots():
    """FR-F1: Stores an occupancy snapshot per location every 5 minutes in occupancy_records."""
    try:
        now = utc_now()
        locations = await fetch_all("SELECT id, total_slots FROM parking_locations WHERE status = 'APPROVED'")
        if not locations:
            return

        loc_ids = [str(l["id"]) for l in locations]
        loc_ids_str = ",".join(loc_ids)

        # Count current occupied slots from booking_blocks for active window
        occ_rows = await fetch_all(
            f"""
            SELECT s.location_id, COUNT(DISTINCT bb.slot_id) as occ_count
            FROM booking_blocks bb
            JOIN parking_slots s ON bb.slot_id = s.id
            WHERE s.location_id IN ({loc_ids_str})
              AND bb.block_start <= %s AND bb.block_start > DATE_SUB(%s, INTERVAL 15 MINUTE)
            GROUP BY s.location_id
            """,
            (now, now),
        )
        occ_map = {r["location_id"]: r["occ_count"] for r in occ_rows}

        for l in locations:
            lid = l["id"]
            tot = l["total_slots"] or 50
            occ = occ_map.get(lid, 0)
            avail = max(0, tot - occ)

            await execute(
                """
                INSERT INTO occupancy_records (location_id, ts, total_slots, occupied, available, synthetic)
                VALUES (%s, %s, %s, %s, %s, 0)
                """,
                (lid, now, tot, occ, avail),
            )
        logger.info(f"Recorded live occupancy snapshot for {len(locations)} locations.")
    except Exception as e:
        logger.error(f"Error recording occupancy snapshot: {e}")

async def main():
    logger.info("Starting background worker scheduler...")
    await init_pool()
    await init_redis()

    scheduler = AsyncIOScheduler()
    
    # 1. Hold expiry every 60 seconds (FR-B5)
    scheduler.add_job(expire_unpaid_holds, "interval", seconds=60, id="hold_expiry")

    # 2. Occupancy snapshot every 5 minutes (FR-F1)
    scheduler.add_job(take_occupancy_snapshots, "interval", minutes=5, id="occ_snapshots")

    # 3. Auto-booking check every 5 minutes (FR-AB2)
    scheduler.add_job(evaluate_auto_booking_rules, "interval", minutes=5, id="auto_booking")

    scheduler.start()
    logger.info("APScheduler worker started successfully.")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping worker...")
        scheduler.shutdown()
        await close_pool()
        await close_redis()

if __name__ == "__main__":
    asyncio.run(main())
