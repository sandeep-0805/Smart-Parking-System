from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.dependencies import get_optional_user
from app.schemas.search import SearchResponse, LocationSuggestion, ReverseGeocodeResponse
from app.services.search_service import search_parking, get_location_suggestions, reverse_geocode_coords
from app.services.ai_client import ai_client
from app.redis_client import get_cache, set_cache

router = APIRouter(tags=["Search"])

@router.get("/search/suggestions", response_model=List[LocationSuggestion])
async def search_suggestions_endpoint(
    q: str = Query(..., description="Search query string")
):
    if len(q.strip()) < 3:
        return []
    return await get_location_suggestions(q.strip())

@router.get("/search/reverse-geocode", response_model=ReverseGeocodeResponse)
async def reverse_geocode_endpoint(
    lat: float = Query(...),
    lng: float = Query(...),
):
    return await reverse_geocode_coords(lat, lng)

@router.get("/search", response_model=SearchResponse)
async def search_parking_endpoint(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    place_name: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    duration_minutes: Optional[int] = Query(120),
    vehicle_type: Optional[str] = Query(None),
    max_budget_inr: Optional[float] = Query(None),
    max_distance_m: Optional[int] = Query(None),
    facilities: Optional[List[str]] = Query(None),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    prefs = user.get("preferences", {}) if user else {}
    budget_paise = int(max_budget_inr * 100) if max_budget_inr else None

    # Check 30s cache for fast display (FR-S6)
    cache_key = f"search:{lat}:{lng}:{place_name}:{date}:{start_time}:{duration_minutes}:{vehicle_type}:{budget_paise}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    result = await search_parking(
        user_preferences=prefs,
        lat=lat,
        lng=lng,
        place_name=place_name,
        date_text=date,
        start_time_text=start_time,
        duration_minutes=duration_minutes,
        vehicle_type=vehicle_type,
        max_budget_paise=budget_paise,
        max_distance_m=max_distance_m,
        facilities=facilities,
    )

    # Cache for up to 30 seconds for display only
    await set_cache(cache_key, result, 30)
    return result

@router.get("/locations/{id}/forecast")
async def get_location_forecast(
    id: int,
    target_time: Optional[str] = Query(None),
):
    cache_key = f"forecast:{id}:{target_time}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    from datetime import datetime, timezone, timedelta
    t_time = target_time or (datetime.now(timezone.utc) + timedelta(minutes=45)).isoformat()

    forecast_data = await ai_client.get_forecast(location_id=id, target_time=t_time)
    if not forecast_data:
        # Fallback estimate
        forecast_data = {
            "location_id": id,
            "target_time": t_time,
            "predicted_available": 25.0,
            "predicted_occupied": 25.0,
            "total_slots": 50,
            "occupancy_pct": 0.50,
            "uncertainty_low": 0.35,
            "uncertainty_high": 0.65,
            "model_version": "fallback_baseline",
            "is_estimate": True,
        }

    # FR-F3: Cached in Redis for about 5 minutes
    await set_cache(cache_key, forecast_data, 300)
    return forecast_data
