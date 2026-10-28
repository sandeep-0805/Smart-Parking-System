import json
import logging
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import httpx

from app.config import settings
from app.database import fetch_all, fetch_one, execute, execute_many
from app.redis_client import get_cache, set_cache
from app.services.ai_client import ai_client
from app.services.pricing_service import calculate_quote_for_slot
from app.utils import haversine_distance_m, utc_now, generate_blocks, parse_time_window

logger = logging.getLogger("search_service")

# ── Comprehensive Indian Metro & Regional Hubs Registry ───────────────────────
KNOWN_LOCATIONS = [
    # Telangana / Hyderabad
    {"name": "Hitech City", "address": "Cyberabad, Madhapur, Hyderabad, Telangana", "lat": 17.4435, "lng": 78.3772, "category": "area"},
    {"name": "Cyber Towers", "address": "Hitech City Main Rd, Madhapur, Hyderabad", "lat": 17.4504, "lng": 78.3808, "category": "landmark"},
    {"name": "Inorbit Mall Cyberabad", "address": "Mindspace, Madhapur, Hyderabad, Telangana", "lat": 17.4344, "lng": 78.3866, "category": "landmark"},
    {"name": "Inorbit Mall", "address": "Mindspace, Madhapur, Hyderabad, Telangana", "lat": 17.4344, "lng": 78.3866, "category": "landmark"},
    {"name": "Sarath City Capital Mall", "address": "Gachibowli - Miyapur Rd, Whitefields, Kondapur, Hyderabad", "lat": 17.4578, "lng": 78.3638, "category": "landmark"},
    {"name": "Nexus Hyderabad Mall", "address": "Sujana Forum Mall, KPHB Phase 9, Kukatpally, Hyderabad", "lat": 17.4849, "lng": 78.3905, "category": "landmark"},
    {"name": "Forum Sujana Mall", "address": "KPHB Colony, Kukatpally, Hyderabad", "lat": 17.4849, "lng": 78.3905, "category": "landmark"},
    {"name": "GVK One Mall", "address": "Road No 1, Banjara Hills, Hyderabad", "lat": 17.4194, "lng": 78.4484, "category": "landmark"},
    {"name": "Lulu Mall Hyderabad", "address": "KPHB Colony, Kukatpally, Hyderabad", "lat": 17.4930, "lng": 78.3912, "category": "landmark"},
    {"name": "Next Galleria Mall Punjagutta", "address": "Punjagutta Circle, Hyderabad", "lat": 17.4265, "lng": 78.4515, "category": "landmark"},
    {"name": "IKEA Hyderabad", "address": "Raidurg, Hitech City, Hyderabad", "lat": 17.4375, "lng": 78.3756, "category": "landmark"},
    {"name": "DLF Cybercity", "address": "Gachibowli, Hyderabad, Telangana", "lat": 17.4475, "lng": 78.3585, "category": "landmark"},
    {"name": "Mindspace Madhapur", "address": "IT Corridor, Madhapur, Hyderabad", "lat": 17.4380, "lng": 78.3815, "category": "area"},
    {"name": "Raidurg Metro Station", "address": "Mindspace Junction, Raidurg, Hyderabad", "lat": 17.4382, "lng": 78.3768, "category": "landmark"},
    {"name": "Hitec City Metro Station", "address": "Hitec City Rd, Cyber Towers, Madhapur, Hyderabad", "lat": 17.4473, "lng": 78.3831, "category": "landmark"},
    {"name": "Gachibowli", "address": "Financial District, Hyderabad, Telangana", "lat": 17.4401, "lng": 78.3489, "category": "area"},
    {"name": "Madhapur", "address": "IT Corridor, Hyderabad, Telangana", "lat": 17.4483, "lng": 78.3915, "category": "area"},
    {"name": "Jubilee Hills", "address": "Road No 36, Hyderabad, Telangana", "lat": 17.4319, "lng": 78.4073, "category": "area"},
    {"name": "Banjara Hills", "address": "Road No 1 & 12, Hyderabad, Telangana", "lat": 17.4156, "lng": 78.4350, "category": "area"},
    {"name": "Financial District", "address": "Nanakramguda, Gachibowli, Hyderabad", "lat": 17.4178, "lng": 78.3400, "category": "area"},
    {"name": "Kondapur", "address": "Near Botanical Garden, Hyderabad, Telangana", "lat": 17.4699, "lng": 78.3578, "category": "area"},
    {"name": "Begumpet", "address": "Airport Road, Hyderabad, Telangana", "lat": 17.4447, "lng": 78.4664, "category": "area"},
    {"name": "Secunderabad", "address": "Railway Station Road, Secunderabad, Telangana", "lat": 17.4399, "lng": 78.4983, "category": "area"},
    {"name": "Charminar", "address": "Old City, Hyderabad, Telangana", "lat": 17.3616, "lng": 78.4747, "category": "landmark"},
    {"name": "Durgam Cheruvu", "address": "Cable Bridge, Jubilee Hills / Madhapur, Hyderabad", "lat": 17.4363, "lng": 78.3892, "category": "landmark"},
    {"name": "KPHB Colony", "address": "Kukatpally Housing Board, Hyderabad, Telangana", "lat": 17.4933, "lng": 78.3989, "category": "area"},
    {"name": "Kukatpally", "address": "Main Road, Hyderabad, Telangana", "lat": 17.4849, "lng": 78.4138, "category": "area"},
    {"name": "Miyapur", "address": "Metro Terminal, Hyderabad, Telangana", "lat": 17.4968, "lng": 78.3614, "category": "area"},
    {"name": "Ameerpet", "address": "Metro Interchange, Hyderabad, Telangana", "lat": 17.4375, "lng": 78.4483, "category": "area"},
    {"name": "Somajiguda", "address": "Raj Bhavan Rd, Hyderabad, Telangana", "lat": 17.4265, "lng": 78.4593, "category": "area"},
    {"name": "Mehdipatnam", "address": "P.V. Narasimha Rao Expressway, Hyderabad", "lat": 17.3916, "lng": 78.4402, "category": "area"},
    {"name": "Uppal", "address": "Inner Ring Road, Hyderabad, Telangana", "lat": 17.4018, "lng": 78.5602, "category": "area"},
    {"name": "LB Nagar", "address": "Vijayawada Highway Junction, Hyderabad", "lat": 17.3457, "lng": 78.5522, "category": "area"},
    {"name": "Shamshabad RGIA Airport", "address": "Rajiv Gandhi International Airport, Hyderabad", "lat": 17.2403, "lng": 78.4294, "category": "landmark"},

    # Andhra Pradesh / Amaravati / Vijayawada
    {"name": "PVP Square Mall", "address": "MG Road, Governor Peta, Vijayawada, Andhra Pradesh", "lat": 16.5058, "lng": 80.6480, "category": "landmark"},
    {"name": "Trendset Mall", "address": "Benz Circle, MG Road, Vijayawada, Andhra Pradesh", "lat": 16.5003, "lng": 80.6508, "category": "landmark"},
    {"name": "Krishna Lanka", "address": "NH-16, Krishna Lanka, Vijayawada, Andhra Pradesh", "lat": 16.5050, "lng": 80.6270, "category": "area"},
    {"name": "VIT-AP University", "address": "Beside Inavolu, Amaravati, Andhra Pradesh 522237", "lat": 16.4965, "lng": 80.4992, "category": "landmark"},
    {"name": "SRM University AP", "address": "Neerukonda, Amaravati, Andhra Pradesh 522240", "lat": 16.4673, "lng": 80.5085, "category": "landmark"},
    {"name": "Benz Circle", "address": "MG Road, Benz Circle, Vijayawada, Andhra Pradesh", "lat": 16.5003, "lng": 80.6508, "category": "landmark"},
    {"name": "MG Road Vijayawada", "address": "Bandar Rd, Governor Peta, Vijayawada, Andhra Pradesh", "lat": 16.5085, "lng": 80.6432, "category": "area"},
    {"name": "Vijayawada Railway Station", "address": "Station Rd, Tarapet, Vijayawada, Andhra Pradesh", "lat": 16.5186, "lng": 80.6201, "category": "landmark"},
    {"name": "Kanaka Durga Temple", "address": "Indrakeeladri, Vijayawada, Andhra Pradesh", "lat": 16.5152, "lng": 80.6074, "category": "landmark"},
    {"name": "PNBS Bus Station Vijayawada", "address": "Pandit Nehru Bus Station, Vijayawada, AP", "lat": 16.5098, "lng": 80.6185, "category": "landmark"},
    {"name": "Guntur", "address": "Guntur, Andhra Pradesh", "lat": 16.3067, "lng": 80.4365, "category": "area"},
    {"name": "Amaravati", "address": "Capital City, Andhra Pradesh", "lat": 16.5131, "lng": 80.5165, "category": "area"},
    {"name": "Mangalagiri", "address": "Guntur District, Andhra Pradesh", "lat": 16.4326, "lng": 80.5604, "category": "area"},
    {"name": "Visakhapatnam", "address": "Beach Road, Vizag, Andhra Pradesh", "lat": 17.6868, "lng": 83.2185, "category": "area"},
    {"name": "Tirupati", "address": "Tirupati, Andhra Pradesh", "lat": 13.6288, "lng": 79.4192, "category": "area"},

    # Karnataka / Bengaluru (Bangalore)
    {"name": "Phoenix Marketcity Bangalore", "address": "Whitefield Main Rd, Mahadevapura, Bengaluru", "lat": 12.9959, "lng": 77.6964, "category": "landmark"},
    {"name": "Nexus Koramangala", "address": "Hosur Rd, Koramangala, Bengaluru", "lat": 12.9352, "lng": 77.6138, "category": "landmark"},
    {"name": "Forum Mall Koramangala", "address": "Hosur Rd, Koramangala, Bengaluru", "lat": 12.9352, "lng": 77.6138, "category": "landmark"},
    {"name": "Orion Mall", "address": "Dr Rajkumar Rd, Malleshwaram, Bengaluru", "lat": 13.0112, "lng": 77.5549, "category": "landmark"},
    {"name": "UB City", "address": "Vittal Mallya Rd, Ashok Nagar, Bengaluru", "lat": 12.9719, "lng": 77.5958, "category": "landmark"},
    {"name": "Koramangala", "address": "4th & 5th Block, Koramangala, Bengaluru, Karnataka", "lat": 12.9352, "lng": 77.6245, "category": "area"},
    {"name": "Indiranagar", "address": "100ft Rd, HAL 2nd Stage, Indiranagar, Bengaluru", "lat": 12.9719, "lng": 77.6412, "category": "area"},
    {"name": "MG Road Bangalore", "address": "Ashok Nagar, MG Road, Bengaluru, Karnataka", "lat": 12.9738, "lng": 77.6070, "category": "area"},
    {"name": "Brigade Road", "address": "Shanthala Nagar, Ashok Nagar, Bengaluru, Karnataka", "lat": 12.9723, "lng": 77.6074, "category": "area"},
    {"name": "Whitefield", "address": "ITPL Main Rd, Whitefield, Bengaluru, Karnataka", "lat": 12.9855, "lng": 77.7289, "category": "area"},
    {"name": "HSR Layout", "address": "27th Main Rd, HSR Layout, Bengaluru, Karnataka", "lat": 12.9116, "lng": 77.6389, "category": "area"},
    {"name": "Electronic City", "address": "Phase 1, Hosur Rd, Bengaluru, Karnataka", "lat": 12.8452, "lng": 77.6602, "category": "area"},
    {"name": "Jayanagar", "address": "4th Block, Jayanagar, Bengaluru, Karnataka", "lat": 12.9308, "lng": 77.5838, "category": "area"},
    {"name": "Malleshwaram", "address": "Sampige Rd, Malleshwaram, Bengaluru, Karnataka", "lat": 12.9982, "lng": 77.5704, "category": "area"},
    {"name": "Majestic Bangalore", "address": "Kempegowda Bus Station & Railway, Bengaluru", "lat": 12.9767, "lng": 77.5713, "category": "landmark"},
    {"name": "BTM Layout", "address": "Outer Ring Road, BTM Layout, Bengaluru, Karnataka", "lat": 12.9166, "lng": 77.6101, "category": "area"},
    {"name": "Marathahalli", "address": "ORR Junction, Marathahalli, Bengaluru, Karnataka", "lat": 12.9591, "lng": 77.6974, "category": "area"},
    {"name": "Bellandur", "address": "Outer Ring Rd, Bellandur, Bengaluru, Karnataka", "lat": 12.9304, "lng": 77.6784, "category": "area"},

    # Maharashtra / Mumbai & Pune
    {"name": "Phoenix Palladium Mall", "address": "High Street Phoenix, Senapati Bapat Marg, Lower Parel, Mumbai", "lat": 18.9953, "lng": 72.8258, "category": "landmark"},
    {"name": "Jio World Drive", "address": "Bandra Kurla Complex, Bandra East, Mumbai", "lat": 19.0657, "lng": 72.8687, "category": "landmark"},
    {"name": "Inorbit Mall Malad", "address": "Link Rd, Malad West, Mumbai", "lat": 19.1728, "lng": 72.8359, "category": "landmark"},
    {"name": "CR2 Mall Nariman Point", "address": "Barrister Rajni Patel Marg, Nariman Point, Mumbai", "lat": 18.9284, "lng": 72.8229, "category": "landmark"},
    {"name": "Nariman Point", "address": "Marine Drive, Nariman Point, Mumbai, Maharashtra", "lat": 18.9284, "lng": 72.8229, "category": "area"},
    {"name": "Marine Drive", "address": "Netaji Subhash Chandra Bose Rd, Mumbai, Maharashtra", "lat": 18.9432, "lng": 72.8235, "category": "area"},
    {"name": "Bandra Kurla Complex (BKC)", "address": "G Block, BKC, Bandra East, Mumbai, Maharashtra", "lat": 19.0657, "lng": 72.8687, "category": "area"},
    {"name": "Bandra West", "address": "Linking Rd & Hill Rd, Bandra West, Mumbai", "lat": 19.0607, "lng": 72.8362, "category": "area"},
    {"name": "Lower Parel", "address": "Senapati Bapat Marg, Lower Parel, Mumbai", "lat": 18.9953, "lng": 72.8258, "category": "area"},
    {"name": "Colaba", "address": "Colaba Causeway, Mumbai, Maharashtra", "lat": 18.9067, "lng": 72.8147, "category": "area"},
    {"name": "Andheri West", "address": "Link Road, Andheri West, Mumbai, Maharashtra", "lat": 19.1136, "lng": 72.8697, "category": "area"},
    {"name": "Dadar", "address": "Dadar West, Mumbai, Maharashtra", "lat": 19.0178, "lng": 72.8478, "category": "area"},
    {"name": "Juhu Beach", "address": "Juhu Tara Rd, Juhu, Mumbai, Maharashtra", "lat": 19.0988, "lng": 72.8264, "category": "landmark"},
    {"name": "Powai", "address": "Hiranandani Gardens, Powai, Mumbai, Maharashtra", "lat": 19.1176, "lng": 72.9060, "category": "area"},
    {"name": "FC Road Pune", "address": "Fergusson College Rd, Shivajinagar, Pune, Maharashtra", "lat": 18.5222, "lng": 73.8415, "category": "area"},
    {"name": "Koregaon Park Pune", "address": "North Main Rd, Koregaon Park, Pune, Maharashtra", "lat": 18.5362, "lng": 73.8940, "category": "area"},
    {"name": "Hinjewadi Pune", "address": "Rajiv Gandhi Infotech Park, Hinjewadi, Pune", "lat": 18.5913, "lng": 73.7389, "category": "area"},
    {"name": "Phoenix Marketcity Pune", "address": "Viman Nagar, Pune, Maharashtra", "lat": 18.5620, "lng": 73.9168, "category": "landmark"},
    {"name": "Viman Nagar Pune", "address": "Phoenix Marketcity, Viman Nagar, Pune", "lat": 18.5679, "lng": 73.9143, "category": "area"},

    # Delhi / NCR
    {"name": "Select CITYWALK", "address": "Saket District Centre, New Delhi", "lat": 28.5284, "lng": 77.2185, "category": "landmark"},
    {"name": "DLF Mall of India", "address": "Sector 18, Noida, Uttar Pradesh", "lat": 28.5678, "lng": 77.3210, "category": "landmark"},
    {"name": "Ambience Mall Gurgaon", "address": "NH-8, Gurugram, Haryana", "lat": 28.5042, "lng": 77.0967, "category": "landmark"},
    {"name": "Connaught Place", "address": "Inner Circle, Connaught Place, New Delhi, Delhi", "lat": 28.6315, "lng": 77.2167, "category": "area"},
    {"name": "Palika Bazar", "address": "Inner Circle, Connaught Place, New Delhi", "lat": 28.6315, "lng": 77.2167, "category": "landmark"},
    {"name": "Cyber Hub Gurgaon", "address": "DLF Phase 2, Sector 24, Gurugram, Haryana", "lat": 28.4950, "lng": 77.0890, "category": "landmark"},
    {"name": "Khan Market", "address": "Rabindra Nagar, New Delhi, Delhi", "lat": 28.6003, "lng": 77.2270, "category": "area"},
    {"name": "Hauz Khas Village", "address": "Deer Park, Hauz Khas, New Delhi, Delhi", "lat": 28.5534, "lng": 77.1945, "category": "area"},
    {"name": "Sector 18 Noida", "address": "Atta Market, Sector 18, Noida, Uttar Pradesh", "lat": 28.5708, "lng": 77.3218, "category": "area"},
    {"name": "Chandni Chowk", "address": "Old Delhi, New Delhi, Delhi", "lat": 28.6506, "lng": 77.2303, "category": "area"},
    {"name": "India Gate", "address": "Rajpath, India Gate, New Delhi, Delhi", "lat": 28.6129, "lng": 77.2295, "category": "landmark"},
    {"name": "Karol Bagh", "address": "Ghaffar Market, Karol Bagh, New Delhi, Delhi", "lat": 28.6514, "lng": 77.1907, "category": "area"},
    {"name": "Saket", "address": "Select Citywalk, Saket District Centre, New Delhi", "lat": 28.5284, "lng": 77.2185, "category": "area"},
    {"name": "Aerocity Delhi", "address": "Near IGI Airport, Aerocity, New Delhi, Delhi", "lat": 28.5535, "lng": 77.1218, "category": "area"},

    # Tamil Nadu / Chennai
    {"name": "T. Nagar Chennai", "address": "Pondy Bazaar, T. Nagar, Chennai, Tamil Nadu", "lat": 13.0418, "lng": 80.2341, "category": "area"},
    {"name": "Anna Nagar Chennai", "address": "Tower Park, Anna Nagar West, Chennai, Tamil Nadu", "lat": 13.0850, "lng": 80.2105, "category": "area"},
    {"name": "Marina Beach Chennai", "address": "Kamarajar Salai, Triplicane, Chennai, Tamil Nadu", "lat": 13.0500, "lng": 80.2824, "category": "landmark"},
    {"name": "Nungambakkam Chennai", "address": "Khader Nawaz Khan Rd, Nungambakkam, Chennai", "lat": 13.0604, "lng": 80.2428, "category": "area"},
    {"name": "Velachery Chennai", "address": "Phoenix Marketcity, Velachery, Chennai, Tamil Nadu", "lat": 12.9815, "lng": 80.2180, "category": "area"},

    # West Bengal / Kolkata
    {"name": "Park Street Kolkata", "address": "Park Street, Mullick Bazar, Kolkata, West Bengal", "lat": 22.5488, "lng": 88.3582, "category": "area"},
    {"name": "Salt Lake Sector V", "address": "IT Hub, Sector V, Bidhannagar, Kolkata, West Bengal", "lat": 22.5786, "lng": 88.4328, "category": "area"},
    {"name": "Howrah Station", "address": "Howrah Railway Station, Howrah, West Bengal", "lat": 22.5839, "lng": 88.3426, "category": "landmark"},
]

# ── Geocoding Engine (Registry -> DB -> Photon -> Nominatim) ─────────────────
async def geocode_place_name(place_name: str) -> Optional[Tuple[float, float]]:
    clean = place_name.strip()
    if not clean:
        return None

    clean_lower = clean.lower()
    cache_key = f"geo:{clean_lower}"
    cached = await get_cache(cache_key)
    if cached and isinstance(cached, dict) and "lat" in cached and "lng" in cached:
        return float(cached["lat"]), float(cached["lng"])

    # 1. Match in local Indian Metro Registry (exact first, then specific substring)
    for item in KNOWN_LOCATIONS:
        if clean_lower == item["name"].lower():
            coords = (item["lat"], item["lng"])
            await set_cache(cache_key, {"lat": coords[0], "lng": coords[1]}, 86400)
            return coords

    for item in sorted(KNOWN_LOCATIONS, key=lambda x: len(x["name"]), reverse=True):
        n_lower = item["name"].lower()
        if clean_lower in n_lower or n_lower in clean_lower:
            coords = (item["lat"], item["lng"])
            await set_cache(cache_key, {"lat": coords[0], "lng": coords[1]}, 86400)
            return coords

    # 2. Match approved parking location in database
    like_pat = f"%{clean}%"
    db_loc = await fetch_one(
        "SELECT lat, lng FROM parking_locations WHERE status = 'APPROVED' AND (name LIKE %s OR address LIKE %s) LIMIT 1",
        (like_pat, like_pat),
    )
    if db_loc:
        coords = (float(db_loc["lat"]), float(db_loc["lng"]))
        await set_cache(cache_key, {"lat": coords[0], "lng": coords[1]}, 86400)
        return coords

    # 3. Query Photon Geocoder (OSM-based, fast, no rate-limit blocking)
    try:
        photon_url = f"https://photon.komoot.io/api/?q={clean}&limit=1"
        async with httpx.AsyncClient(timeout=3.5) as client:
            resp = await client.get(photon_url, headers={"User-Agent": "SmartParking/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if features:
                    lon, lat = features[0]["geometry"]["coordinates"]
                    await set_cache(cache_key, {"lat": lat, "lng": lon}, 86400)
                    return float(lat), float(lon)
    except Exception as e:
        logger.debug(f"Photon geocode lookup failed: {e}")

    # 4. Fallback to OpenStreetMap Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "SmartParkingApp/1.0 (admin@smartparking.local)"}
        params = {"q": clean, "format": "json", "limit": 1}
        async with httpx.AsyncClient(timeout=3.5) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    lat, lng = float(data[0]["lat"]), float(data[0]["lon"])
                    await set_cache(cache_key, {"lat": lat, "lng": lng}, 86400)
                    return lat, lng
    except Exception as e:
        logger.debug(f"Nominatim geocode lookup failed: {e}")

    return None

# ── Autocomplete Suggestions (DB -> Registry -> Photon) ──────────────────────
async def get_location_suggestions(query: str) -> List[Dict[str, Any]]:
    clean = query.strip()
    if len(clean) < 2:
        return []

    cache_key = f"suggest:{clean.lower()}"
    cached = await get_cache(cache_key)
    if cached is not None and isinstance(cached, list) and len(cached) > 0:
        return cached

    results: List[Dict[str, Any]] = []
    seen = set()

    def add_result(res_id: str, name: str, address: str, lat: float, lng: float, cat: str):
        key = (round(lat, 3), round(lng, 3))
        if key not in seen and len(results) < 8:
            seen.add(key)
            results.append({
                "id": res_id,
                "name": name,
                "address": address,
                "lat": round(lat, 5),
                "lng": round(lng, 5),
                "category": cat,
            })

    # 1. Approved parking locations in database
    like_pat = f"%{clean}%"
    db_locs = await fetch_all(
        """
        SELECT id, name, address, lat, lng
        FROM parking_locations
        WHERE status = 'APPROVED'
          AND (name LIKE %s OR address LIKE %s)
        LIMIT 4
        """,
        (like_pat, like_pat),
    )
    for loc in db_locs:
        add_result(
            f"loc-{loc['id']}",
            loc["name"],
            loc["address"],
            float(loc["lat"]),
            float(loc["lng"]),
            "parking",
        )

    # 2. Match known areas and landmarks
    q_lower = clean.lower()
    for item in KNOWN_LOCATIONS:
        if q_lower in item["name"].lower() or q_lower in item["address"].lower():
            add_result(
                f"reg-{item['name'].lower().replace(' ', '-')}",
                item["name"],
                item["address"],
                item["lat"],
                item["lng"],
                item["category"],
            )

    # 3. If fewer than 5 results, query Photon Geocoder
    if len(results) < 5:
        try:
            url = f"https://photon.komoot.io/api/?q={clean}&limit=6"
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url, headers={"User-Agent": "SmartParking/1.0"})
                if resp.status_code == 200:
                    data = resp.json()
                    for feat in data.get("features", []):
                        coords = feat["geometry"]["coordinates"]
                        props = feat["properties"]
                        p_name = props.get("name") or clean.title()
                        city = props.get("city") or props.get("district") or props.get("state") or ""
                        country = props.get("country", "")
                        addr_parts = [p_name]
                        if city and city != p_name:
                            addr_parts.append(city)
                        if country:
                            addr_parts.append(country)
                        full_addr = ", ".join(addr_parts)
                        add_result(
                            f"osm-{props.get('osm_id', len(results))}",
                            p_name,
                            full_addr,
                            float(coords[1]),
                            float(coords[0]),
                            "area",
                        )
        except Exception as e:
            logger.debug(f"Photon suggestion query failed: {e}")

    if results:
        await set_cache(cache_key, results, 3600)
    return results

# ── Reverse Geocoding (DB Proximity -> Photon -> Nominatim) ───────────────────
async def reverse_geocode_coords(lat: float, lng: float) -> Dict[str, Any]:
    cache_key = f"revgeo:{round(lat, 4)}:{round(lng, 4)}"
    cached = await get_cache(cache_key)
    if cached and isinstance(cached, dict):
        return cached

    # 1. Check if close to an approved parking station
    db_locs = await fetch_all(
        "SELECT id, name, address, lat, lng FROM parking_locations WHERE status = 'APPROVED'"
    )
    closest_loc = None
    min_dist = float("inf")
    for loc in db_locs:
        dist = haversine_distance_m(lat, lng, float(loc["lat"]), float(loc["lng"]))
        if dist < min_dist:
            min_dist = dist
            closest_loc = loc

    if closest_loc and min_dist <= 200:
        result = {
            "display_name": closest_loc["name"],
            "area": closest_loc["address"],
            "lat": lat,
            "lng": lng,
        }
        await set_cache(cache_key, result, 86400)
        return result

    # 2. Try Photon reverse geocoding
    try:
        photon_url = f"https://photon.komoot.io/reverse?lat={lat}&lon={lng}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(photon_url, headers={"User-Agent": "SmartParking/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                feats = data.get("features", [])
                if feats:
                    props = feats[0]["properties"]
                    name = props.get("name") or props.get("street") or "Selected Location"
                    city = props.get("city") or props.get("district") or props.get("state") or ""
                    full = f"{name}, {city}" if (city and city != name) else name
                    result = {
                        "display_name": name,
                        "area": full,
                        "lat": lat,
                        "lng": lng,
                    }
                    await set_cache(cache_key, result, 86400)
                    return result
    except Exception as e:
        logger.debug(f"Photon reverse geocode error: {e}")

    # 3. Try Nominatim reverse geocode
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        headers = {"User-Agent": "SmartParkingApp/1.0 (admin@smartparking.local)"}
        params = {"lat": lat, "lon": lng, "format": "json"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get("address", {})
                road = addr.get("road") or addr.get("suburb") or addr.get("neighbourhood") or ""
                city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("state_district") or ""
                name = road or data.get("name") or "Selected Location"
                full_display = f"{name}, {city}" if (road and city) else (data.get("display_name", "Selected Location"))
                result = {
                    "display_name": name,
                    "area": full_display,
                    "lat": lat,
                    "lng": lng,
                }
                await set_cache(cache_key, result, 86400)
                return result
    except Exception as e:
        logger.debug(f"Nominatim reverse geocode error: {e}")

    # 4. Fallback to nearest registry location
    nearest_landmark = None
    nearest_d = float("inf")
    for lm in KNOWN_LOCATIONS:
        d = haversine_distance_m(lat, lng, lm["lat"], lm["lng"])
        if d < nearest_d:
            nearest_d = d
            nearest_landmark = lm

    if nearest_landmark and nearest_d < 5000:
        label = f"Near {nearest_landmark['name']}"
        area = nearest_landmark["address"]
    else:
        label = f"Location ({lat:.4f}, {lng:.4f})"
        area = f"Coordinates: {lat:.4f}, {lng:.4f}"

    result = {
        "display_name": label,
        "area": area,
        "lat": lat,
        "lng": lng,
    }
    await set_cache(cache_key, result, 86400)
    return result

# ── Main Deterministic Parking Search ─────────────────────────────────────────
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
    resolved_place_name = (place_name or "").strip()

    if (target_lat is None or target_lng is None) and resolved_place_name:
        coords = await geocode_place_name(resolved_place_name)
        if coords:
            target_lat, target_lng = coords

    # Parse time window
    start_at, end_at = parse_time_window(
        date_text=date_text,
        start_time_text=start_time_text,
        duration_mins=duration_minutes or 120,
        end_time_text=end_time_text,
    )

    # If coordinates could not be resolved from place_name
    if target_lat is None or target_lng is None:
        if resolved_place_name:
            return {
                "locations": [],
                "total_locations": 0,
                "ranking_type": "none",
                "start_at": start_at,
                "end_at": end_at,
                "target_lat": None,
                "target_lng": None,
                "place_name": resolved_place_name,
                "message": f"Could not find coordinates for '{resolved_place_name}'. Please select from suggestions or click a point on the map.",
            }
        else:
            # Default to Hitech City, Hyderabad if completely blank
            target_lat, target_lng = 17.4435, 78.3772
            resolved_place_name = "Hitech City, Hyderabad"

    # Auto-reverse geocode display name if missing
    if not resolved_place_name:
        try:
            rev = await reverse_geocode_coords(target_lat, target_lng)
            resolved_place_name = rev.get("display_name", f"Location ({target_lat:.3f}, {target_lng:.3f})")
        except Exception:
            resolved_place_name = f"Location ({target_lat:.3f}, {target_lng:.3f})"

    veh_type = vehicle_type or user_preferences.get("default_vehicle_type") or "CAR"
    required_facilities = set(facilities or [])

    # 2. Query all approved parking locations
    locations = await fetch_all(
        """
        SELECT id, owner_id, name, address, lat, lng, operating_hours,
               facilities, base_rate_paise, min_rate_paise, max_rate_paise,
               pay_at_venue, status, total_slots
        FROM parking_locations
        WHERE status = 'APPROVED'
        """
    )

    # 3. Filter locations within strictly 5 km (5000 meters)
    search_radius_m = max_distance_m or 5000
    candidate_slots = []
    location_results = {}

    blocks = generate_blocks(start_at, end_at, settings.BOOKING_GRANULARITY_MINUTES)
    if not blocks:
        return {
            "locations": [],
            "total_locations": 0,
            "ranking_type": "none",
            "start_at": start_at,
            "end_at": end_at,
            "target_lat": target_lat,
            "target_lng": target_lng,
            "place_name": resolved_place_name,
            "message": "Invalid time window or zero duration.",
        }
    block_placeholders = ",".join(["%s"] * len(blocks))

    # Keep track of nearest overall location in database for helpful feedback
    nearest_loc_overall = None
    min_dist_overall = float("inf")

    for loc in locations:
        loc_id = loc["id"]
        dist = haversine_distance_m(target_lat, target_lng, float(loc["lat"]), float(loc["lng"]))

        if dist < min_dist_overall:
            min_dist_overall = dist
            nearest_loc_overall = loc

        # Strictly show parking spaces within 5 km of destination
        if dist > search_radius_m:
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

    # If no parking stations found within 5 km: Return 0 locations honestly (NO FAKE PARKINGS)
    if not candidate_slots:
        nearest_info = None
        if nearest_loc_overall:
            nearest_info = {
                "id": nearest_loc_overall["id"],
                "name": nearest_loc_overall["name"],
                "address": nearest_loc_overall["address"],
                "distance_m": round(min_dist_overall, 1),
                "distance_km": round(min_dist_overall / 1000, 1),
                "lat": float(nearest_loc_overall["lat"]),
                "lng": float(nearest_loc_overall["lng"]),
            }

        return {
            "locations": [],
            "total_locations": 0,
            "ranking_type": "none",
            "start_at": start_at,
            "end_at": end_at,
            "target_lat": target_lat,
            "target_lng": target_lng,
            "place_name": resolved_place_name,
            "nearest_location": nearest_info,
            "message": f"No parking stations found within 5 km of {resolved_place_name}.",
        }

    # 4. Score candidates with AI ranker or fallback to basic sorting
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

    # 5. Group back into location results
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

    # Sort locations: Proximity to destination is primary; combine slot score and distance
    res_list = [v for v in location_results.values() if v["slots"]]
    def location_sort_key(loc):
        best_slot_score = loc["slots"][0]["score"] if ranking_type == "weighted" else 1.0
        # Distance penalty: each kilometer reduces rank score by 0.12 so closer venues rank higher
        effective_score = best_slot_score - ((loc["distance_m"] / 1000.0) * 0.12)
        return effective_score

    res_list.sort(key=location_sort_key, reverse=True)

    return {
        "locations": res_list,
        "total_locations": len(res_list),
        "ranking_type": ranking_type,
        "start_at": start_at,
        "end_at": end_at,
        "target_lat": target_lat,
        "target_lng": target_lng,
        "place_name": resolved_place_name,
        "nearest_location": None,
    }
