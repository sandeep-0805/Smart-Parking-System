from typing import List, Dict, Any
from app.schemas.rank import CandidateSlot, ScoredSlot

def min_max_normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    mn, mx = min(values), max(values)
    if mn == mx:
        return [1.0] * len(values)
    return [(v - mn) / (mx - mn) for v in values]

def min_max_normalize_inverted(values: List[float]) -> List[float]:
    if not values:
        return []
    mn, mx = min(values), max(values)
    if mn == mx:
        return [1.0] * len(values)
    return [1.0 - (v - mn) / (mx - mn) for v in values]

def compute_facility_match(slot_facilities: List[str], preferred: List[str]) -> float:
    if not preferred:
        return 1.0
    if not slot_facilities:
        return 0.0
    matched = len(set(preferred) & set(slot_facilities))
    return matched / len(preferred)

def generate_reason_tags(candidate: CandidateSlot, factors: Dict[str, float]) -> List[str]:
    tags: List[str] = []
    
    if factors["distance"] >= 0.95:
        tags.append("Closest option")
    elif factors["distance"] >= 0.80:
        tags.append("Very close")
        
    if factors["price"] >= 0.95:
        tags.append("Lowest total price")
    elif factors["price"] >= 0.80:
        tags.append("Good value")
        
    if factors["availability"] >= 0.90:
        tags.append("High availability")

    facility_map = {
        "ev_charging": "Has EV charging",
        "covered": "Covered parking",
        "cctv": "CCTV monitored",
        "disabled_access": "Disabled access",
        "valet": "Valet service",
    }
    for fac in candidate.facilities:
        clean_fac = fac.lower().strip()
        if clean_fac in facility_map:
            tags.append(facility_map[clean_fac])

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped[:4]

def rank_candidates(
    candidates: List[CandidateSlot],
    preferences: Dict[str, Any],
    weights: Dict[str, float],
) -> List[ScoredSlot]:
    if not candidates:
        return []

    distances = [float(c.distance_m) for c in candidates]
    prices = [float(c.total_price_paise) for c in candidates]
    availabilities = [float(c.availability_confidence) for c in candidates]

    norm_dist = min_max_normalize_inverted(distances)
    norm_price = min_max_normalize_inverted(prices)
    norm_avail = min_max_normalize(availabilities)

    preferred_fac = preferences.get("preferred_facilities") or []
    norm_fac = [compute_facility_match(c.facilities, preferred_fac) for c in candidates]

    w_dist = weights.get("distance", 0.35)
    w_price = weights.get("price", 0.30)
    w_avail = weights.get("availability", 0.15)
    w_fac = weights.get("facilities", 0.20)

    scored_slots: List[ScoredSlot] = []

    for i, c in enumerate(candidates):
        factors = {
            "distance": round(norm_dist[i], 4),
            "price": round(norm_price[i], 4),
            "availability": round(norm_avail[i], 4),
            "facilities": round(norm_fac[i], 4),
        }
        score = (
            w_dist * factors["distance"]
            + w_price * factors["price"]
            + w_avail * factors["availability"]
            + w_fac * factors["facilities"]
        )

        tags = generate_reason_tags(c, factors)

        scored_slots.append(
            ScoredSlot(
                slot_id=c.slot_id,
                location_id=c.location_id,
                score=round(score, 4),
                factors=factors,
                reason_tags=tags,
            )
        )

    # Sort descending by score
    scored_slots.sort(key=lambda s: s.score, reverse=True)
    return scored_slots
