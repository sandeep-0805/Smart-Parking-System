import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
import math
from app.database import init_pool, close_pool, execute, execute_many, fetch_one
from app.services.auth_service import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

async def seed_data():
    logger.info("Seeding demo data into MySQL database...")
    await init_pool()

    # 1. Users
    pwd_hash = hash_password("Test@1234")
    users_data = [
        ("driver@test.com", pwd_hash, "Rahul Driver", "9876543210", "DRIVER", "ACTIVE", 1),
        ("operator@test.com", pwd_hash, "Priya Operator", "9876543211", "OPERATOR", "ACTIVE", 1),
        ("admin@test.com", pwd_hash, "Kiran Admin", "9876543212", "ADMIN", "ACTIVE", 1),
    ]
    for email, phash, name, phone, role, status, ev in users_data:
        await execute(
            """
            INSERT INTO users (email, password_hash, full_name, phone, role, status, email_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), password_hash = VALUES(password_hash)
            """,
            (email, phash, name, phone, role, status, ev),
        )
    logger.info("Created 3 demo users (driver, operator, admin).")

    driver_user = await fetch_one("SELECT id FROM users WHERE email = 'driver@test.com'")
    operator_user = await fetch_one("SELECT id FROM users WHERE email = 'operator@test.com'")
    op_id = operator_user["id"]
    driver_id = driver_user["id"]

    # 2. Driver Preferences
    await execute(
        """
        INSERT INTO preferences (user_id, default_vehicle_type, preferred_facilities, max_walking_distance_m, max_budget_paise)
        VALUES (%s, 'CAR', JSON_ARRAY('ev_charging', 'covered'), 800, 15000)
        ON DUPLICATE KEY UPDATE default_vehicle_type = VALUES(default_vehicle_type)
        """,
        (driver_id,),
    )

    # 3. Parking Locations in Hyderabad
    locations = [
        {
            "name": "Hitech Cyber Towers Plaza",
            "address": "Cyber Towers, Hitech City Main Rd, Hyderabad 500081",
            "lat": 17.4504,
            "lng": 78.3809,
            "facilities": ["ev_charging", "covered", "cctv", "valet"],
            "base_rate": 3000,
            "min_rate": 1500,
            "max_rate": 8000,
            "total_slots": 15,
            "pay_at_venue": 0,
        },
        {
            "name": "Gachibowli Stadium Multi-Level",
            "address": "Old Mumbai Hwy, Gachibowli, Hyderabad 500032",
            "lat": 17.4435,
            "lng": 78.3489,
            "facilities": ["covered", "cctv", "disabled_access"],
            "base_rate": 2000,
            "min_rate": 1000,
            "max_rate": 5000,
            "total_slots": 15,
            "pay_at_venue": 1,
        },
        {
            "name": "Inorbit Mall Premium Parking",
            "address": "Inorbit Mall Rd, Mindspace, Madhapur, Hyderabad 500081",
            "lat": 17.4344,
            "lng": 78.3866,
            "facilities": ["ev_charging", "covered", "cctv", "valet", "disabled_access"],
            "base_rate": 4000,
            "min_rate": 2000,
            "max_rate": 12000,
            "total_slots": 15,
            "pay_at_venue": 0,
        },
        {
            "name": "Jubilee Hills Square Parking",
            "address": "Road No 36, Jubilee Hills, Hyderabad 500033",
            "lat": 17.4319,
            "lng": 78.4073,
            "facilities": ["covered", "cctv", "valet"],
            "base_rate": 3500,
            "min_rate": 2000,
            "max_rate": 9000,
            "total_slots": 12,
            "pay_at_venue": 0,
        },
        {
            "name": "Banjara One Central Deck",
            "address": "Road No 1, Banjara Hills, Hyderabad 500034",
            "lat": 17.4156,
            "lng": 78.4350,
            "facilities": ["cctv", "disabled_access"],
            "base_rate": 2500,
            "min_rate": 1500,
            "max_rate": 6000,
            "total_slots": 12,
            "pay_at_venue": 0,
        },
        {
            "name": "Financial District Tech Park",
            "address": "Nanakramguda, Financial District, Hyderabad 500032",
            "lat": 17.4178,
            "lng": 78.3400,
            "facilities": ["ev_charging", "covered", "cctv"],
            "base_rate": 2500,
            "min_rate": 1000,
            "max_rate": 7000,
            "total_slots": 12,
            "pay_at_venue": 0,
        },
    ]

    loc_ids = []
    for loc in locations:
        pt_wkt = f"POINT({loc['lng']} {loc['lat']})"
        existing_loc = await fetch_one("SELECT id FROM parking_locations WHERE name = %s", (loc["name"],))
        if existing_loc:
            loc_id = existing_loc["id"]
        else:
            loc_id, _ = await execute(
                """
                INSERT INTO parking_locations (
                    owner_id, name, address, lat, lng, location_point,
                    operating_hours, facilities, base_rate_paise, min_rate_paise,
                    max_rate_paise, total_slots, pay_at_venue, status
                ) VALUES (
                    %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326),
                    %s, %s, %s, %s, %s, %s, %s, 'APPROVED'
                )
                """,
                (
                    op_id,
                    loc["name"],
                    loc["address"],
                    loc["lat"],
                    loc["lng"],
                    pt_wkt,
                    json.dumps({"all": {"open": "00:00", "close": "23:59"}}),
                    json.dumps(loc["facilities"]),
                    loc["base_rate"],
                    loc["min_rate"],
                    loc["max_rate"],
                    loc["total_slots"],
                    loc["pay_at_venue"],
                ),
            )
        loc_ids.append(loc_id)

    logger.info(f"Seeded {len(loc_ids)} approved parking locations.")

    # 4. Slots per location
    slot_configs = [
        ("A01", "CAR"), ("A02", "CAR"), ("A03", "CAR"), ("A04", "CAR"), ("A05", "CAR"),
        ("E01", "EV"),  ("E02", "EV"),
        ("S01", "SUV"), ("S02", "SUV"),
        ("M01", "MOTORCYCLE"), ("M02", "MOTORCYCLE"),
    ]
    total_slots_created = 0
    for lid in loc_ids:
        existing_slots = await fetch_one("SELECT COUNT(*) as cnt FROM parking_slots WHERE location_id = %s", (lid,))
        if existing_slots and existing_slots["cnt"] > 0:
            continue
        slots_batch = []
        for code, vtype in slot_configs:
            slots_batch.append((lid, code, vtype, None, "ACTIVE"))
        await execute_many(
            "INSERT INTO parking_slots (location_id, code, vehicle_type, restrictions, status) VALUES (%s, %s, %s, %s, %s)",
            slots_batch,
        )
        total_slots_created += len(slots_batch)
        await execute("UPDATE parking_locations SET total_slots = %s WHERE id = %s", (len(slots_batch), lid))

    logger.info(f"Seeded {total_slots_created} parking slots.")

    # 5. Synthetic Occupancy History (4 weeks, 1-hour intervals for cold start)
    existing_occ = await fetch_one("SELECT COUNT(*) as cnt FROM occupancy_records")
    if not existing_occ or existing_occ["cnt"] < 500:
        logger.info("Generating synthetic occupancy records for ML forecasting...")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        records = []
        # Generate 4 weeks (672 hourly steps)
        for hour_step in range(672, 0, -1):
            ts = now - timedelta(hours=hour_step)
            hour_of_day = ts.hour
            is_weekend = (ts.weekday() >= 5)

            for lid in loc_ids:
                total_s = 15
                # Realistic daily cycle: peak between 10am and 8pm
                if 10 <= hour_of_day <= 20:
                    base_occ = 0.65 if not is_weekend else 0.80
                elif 8 <= hour_of_day < 10 or 20 < hour_of_day <= 22:
                    base_occ = 0.45
                else:
                    base_occ = 0.15

                # Add sine wave modulation
                occ_factor = min(0.95, max(0.05, base_occ + 0.1 * math.sin(hour_step / 12.0)))
                occupied = int(round(occ_factor * total_s))
                available = total_s - occupied

                records.append((lid, ts, total_s, occupied, available, 1))

        await execute_many(
            """
            INSERT INTO occupancy_records (location_id, ts, total_slots, occupied, available, synthetic)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            records,
        )
        logger.info(f"Seeded {len(records)} synthetic occupancy records.")

    logger.info("✅ Database seed completed successfully!")
    await close_pool()

if __name__ == "__main__":
    asyncio.run(seed_data())
