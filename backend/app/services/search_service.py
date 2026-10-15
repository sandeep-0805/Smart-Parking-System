import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import httpx

from app.config import settings
from app.database import fetch_all, fetch_one
from app.redis_client import get_cache, set_cache
from app.services.ai_client import ai_client
from app.services.pricing_service import calculate_quote_for_slot
from app.utils import haversine_distance_m, utc_now, generate_blocks, parse_time_window

logger = logging.getLogger("search_service")

# ── Geocoding via Nominatim with Redis Caching ────────────────────────────────
async def geocode_place_name(place_name: str) -> Optional[Tuple[float, float]]:
    clean = place_name.strip().lower()
    cache_key = f"geo:{clean}"
    cached = await get_cache(cache_key)
    if cached:
        return float(cached["lat"]), float(cached["lng"])

    # Fallback known Hyderabad coordinates
    known_spots = {
        "hitech city": (17.4435, 78.3772),
        "gachibowli": (17.4401, 78.3489),
        "madhapur": (17.4483, 78.3915),
        "jubilee hills": (17.4319, 78.4073),
        "banjara hills": (17.4156, 78.4350),
        "inorbit mall": (17.4344, 78.3866),
        "ikea": (17.4375, 78.3756),
        "secunderabad": (17.4399, 78.4983),
        "charminar": (17.3616, 78.4747),
        "hyderabad airport": (17.2403, 78.4294),
        "financial district": (17.4178, 78.3400),
    }
    for k, coords in known_spots.items():
        if k in clean:
            await set_cache(cache_key, {"lat": coords[0], "lng": coords[1]}, 86400)
            return coords

    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "SmartParkingApp/1.0 (admin@smartparking.local)"}
    params = {"q": f"{place_name}, Hyderabad, India", "format": "json", "limit": 1}

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    lat, lng = float(data[0]["lat"]), float(data[0]["lon"])
                    await set_cache(cache_key, {"lat": lat, "lng": lng}, 86400)
                    return lat, lng
    except Exception as e:
        logger.warning(f"Nominatim geocoding failed: {e}")

    # Default to Hitech City center
    return 17.4435, 78.3772

# ── Main Parking Search ───────────────────────────────────────────────────────
async def search_parking(
    user_preferences: Dict[str, Any],
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    place_name: Optional[str] = None,
    date_text: Optional[str] = None,
    start_time_text: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    end_time_text: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    max_budget_paise: Optional[int] = None,
    max_distance_m: Optional[int] = None,
    facilities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    # 1. Resolve coordinates
    target_lat = lat
    target_lng = lng
    if (target_lat is None or target_lng is None) and place_name:
        coords = await geocode_place_name(place_name)
        if coords:
            target_lat, target_lng = coords

    if target_lat is None or target_lng is None:
        target_lat, target_lng = 17.4435, 78.3772  # Hyderabad central default

    # 2. Parse time window into UTC
    start_at, end_at = parse_time_window(
        date_text=date_text,
        start_time_text=start_time_text,
        duration_mins=duration_minutes or 120,
        end_time_text=end_time_text,
    )

    veh_type = vehicle_type or user_preferences.get("default_vehicle_type") or "CAR"
    required_facilities = set(facilities or [])

    # 3. Query approved locations
    locations = await fetch_all(
        """
        SELECT id, owner_id, name, address, lat, lng, operating_hours,
               facilities, base_rate_paise, min_rate_paise, max_rate_paise,
               pay_at_venue, status, total_slots
        FROM parking_locations
        WHERE status = 'APPROVED'
        """
    )

    # 4. Filter locations and compute availability for time window
    candidate_slots = []
    location_results = {}

    blocks = generate_blocks(start_at, end_at, settings.BOOKING_GRANULARITY_MINUTES)
    block_placeholders = ",".join(["%s"] * len(blocks))

    for loc in locations:
        loc_id = loc["id"]
        dist = haversine_distance_m(target_lat, target_lng, float(loc["lat"]), float(loc["lng"]))

        if max_distance_m and dist > max_distance_m:
            continue

        loc_facs = json.loads(loc["facilities"]) if isinstance(loc["facilities"], str) else (loc["facilities"] or [])
        if required_facilities and not required_facilities.issubset(set(loc_facs)):
            continue

        # Find ACTIVE slots for this vehicle type that have NO conflicting booking blocks
        query = f"""
        SELECT s.id, s.code, s.vehicle_type
        FROM parking_slots s
        WHERE s.location_id = %s
          AND s.status = 'ACTIVE'
          AND s.vehicle_type = %s
          AND s.id NOT IN (
              SELECT slot_id FROM booking_blocks
              WHERE slot_id = s.id AND block_start IN ({block_placeholders})
          )
        """
        params = [loc_id, veh_type] + blocks
        available_slots = await fetch_all(query, tuple(params))

        if not available_slots:
            continue

        location_results[loc_id] = {
            "location_id": loc_id,
            "name": loc["name"],
            "address": loc["address"],
            "lat": float(loc["lat"]),
            "lng": float(loc["lng"]),
            "distance_m": round(dist, 1),
            "base_rate_paise": loc["base_rate_paise"],
            "facilities": loc_facs,
            "pay_at_venue": bool(loc["pay_at_venue"]),
            "available_slots_count": len(available_slots),
            "slots": [],
        }

        # Pick up to 3 candidate slots per location to quote and rank
        for slot in available_slots[:3]:
            quote = await calculate_quote_for_slot(slot["id"], start_at, end_at)
            
            if max_budget_paise and quote["total_paise"] > max_budget_paise:
                continue

            candidate_slots.append({
                "slot_id": slot["id"],
                "slot_code": slot["code"],
                "location_id": loc_id,
                "location_name": loc["name"],
                "distance_m": dist,
                "total_price_paise": quote["total_paise"],
                "quote_id": quote["id"],
                "vehicle_type": veh_type,
                "facilities": loc_facs,
                "availability_confidence": 1.0,
            })

    if not candidate_slots:
        return {
            "locations": [],
            "total_locations": 0,
            "ranking_type": "none",
            "start_at": start_at,
            "end_at": end_at,
        }

    # 5. Score candidates with AI ranker or fallback to basic sorting
    ranking_type = "basic"
    scored_candidates = []

    ai_ranked = await ai_client.rank_candidates(
        candidates=candidate_slots,
        preferences=user_preferences,
    )

    if ai_ranked:
        ranking_type = "weighted"
        score_map = {item["slot_id"]: item for item in ai_ranked}
        for c in candidate_slots:
            s_info = score_map.get(c["slot_id"])
            scored_candidates.append({
                **c,
                "score": s_info.get("score", 0.5) if s_info else 0.5,
                "reason_tags": s_info.get("reason_tags", []) if s_info else ["Available"],
            })
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    else:
        # Fallback: sort by distance ascending, then price ascending (FR-R4)
        ranking_type = "basic"
        for c in candidate_slots:
            tags = []
            if c["distance_m"] < 1000:
                tags.append("Within 1 km")
            if "ev_charging" in c["facilities"]:
                tags.append("Has EV charging")
            scored_candidates.append({
                **c,
                "score": 1.0,
                "reason_tags": tags or ["Standard Match"],
            })
        scored_candidates.sort(key=lambda x: (x["distance_m"], x["total_price_paise"]))

    # 6. Group back into location results
    for sc in scored_candidates:
        loc_id = sc["location_id"]
        if loc_id in location_results:
            location_results[loc_id]["slots"].append({
                "slot_id": sc["slot_id"],
                "slot_code": sc["slot_code"],
                "vehicle_type": sc["vehicle_type"],
                "total_price_paise": sc["total_price_paise"],
                "quote_id": sc["quote_id"],
                "score": sc["score"],
                "reason_tags": sc["reason_tags"],
            })

    # Sort locations by their best slot score / distance
    res_list = [v for v in location_results.values() if v["slots"]]
    res_list.sort(key=lambda l: l["slots"][0]["score"] if ranking_type == "weighted" else l["distance_m"],
                  reverse=(ranking_type == "weighted"))

    return {
        "locations": res_list,
        "total_locations": len(res_list),
        "ranking_type": ranking_type,
        "start_at": start_at,
        "end_at": end_at,
    }
