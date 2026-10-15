import logging
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, Header, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_pool, close_pool, check_db_health, fetch_all, fetch_one
from app.schemas.rank import RankRequest, RankResponse
from app.schemas.intent import IntentRequest, IntentResponse
from app.schemas.forecast import ForecastRequest, ForecastResponse, TrainResponse
from app.rank import rank_candidates
from app.intent import extract_intent
from app.forecast import forecast_manager

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("ai_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Smart Parking AI Service...")
    await init_pool()
    forecast_manager.load_models()
    yield
    await close_pool()
    logger.info("AI Service shutdown complete.")

app = FastAPI(
    title="Smart Parking AI Service",
    version="1.0.0",
    description="Stateless advisory AI/ML microservice for slot ranking, intent extraction, and availability forecasting",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_service_token(
    x_service_token: Optional[str] = Header(None, alias="X-Service-Token"),
    authorization: Optional[str] = Header(None),
):
    token = x_service_token
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    
    if not token or token != settings.AI_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing service token",
        )
    return token

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}

@app.get("/ready")
async def ready():
    db_ok = await check_db_health()
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            ollama_ok = (resp.status_code == 200)
    except Exception:
        ollama_ok = False

    ready_state = {
        "status": "ready" if db_ok else "degraded",
        "database": db_ok,
        "ollama": ollama_ok,
        "models_loaded": len(forecast_manager.models),
    }
    return ready_state

@app.post("/v1/rank", response_model=RankResponse)
async def rank_slots(request: RankRequest, _token: str = Depends(verify_service_token)):
    scored = rank_candidates(request.candidates, request.preferences, request.weights)
    return RankResponse(ranked=scored, ranking_type="weighted")

@app.post("/v1/intent", response_model=IntentResponse)
async def parse_intent(request: IntentRequest, _token: str = Depends(verify_service_token)):
    result = await extract_intent(
        message=request.message,
        collected_fields=request.collected_fields,
        ollama_url=settings.OLLAMA_URL,
        model=settings.OLLAMA_MODEL,
        timeout=settings.OLLAMA_TIMEOUT_SECS,
    )
    return result

@app.post("/v1/forecast", response_model=ForecastResponse)
async def get_forecast(request: ForecastRequest, _token: str = Depends(verify_service_token)):
    # Look up total slots and current occupancy from database if available
    loc_row = await fetch_one(
        "SELECT total_slots FROM parking_locations WHERE id = %s",
        (request.location_id,)
    )
    total_slots = int(loc_row["total_slots"]) if loc_row and loc_row.get("total_slots") else 50

    # Get latest occupancy record for lag feature
    latest_rec = await fetch_one(
        "SELECT occupied, total_slots FROM occupancy_records WHERE location_id = %s ORDER BY ts DESC LIMIT 1",
        (request.location_id,)
    )
    current_occ = None
    if latest_rec and latest_rec.get("total_slots", 0) > 0:
        current_occ = latest_rec["occupied"] / latest_rec["total_slots"]

    prediction = forecast_manager.predict(
        location_id=request.location_id,
        target_time_str=request.target_time,
        current_occ_pct=current_occ,
        total_slots=total_slots,
    )
    return ForecastResponse(**prediction)

@app.post("/v1/models/train", response_model=TrainResponse)
async def train_models(_token: str = Depends(verify_service_token)):
    records = await fetch_all(
        "SELECT location_id, ts, total_slots, occupied, available, synthetic FROM occupancy_records ORDER BY ts ASC"
    )
    if not records:
        # Generate some synthetic sample records for initial cold start training if empty
        logger.info("No records in DB, skipping or using empty")
        return TrainResponse(
            version=forecast_manager.model_version,
            metrics={"status": "No records in database to train on"},
            message="No training data found"
        )
    result = await forecast_manager.train_on_data(records)
    return TrainResponse(
        version=result.get("version", "v_latest"),
        metrics=result.get("metrics", {}),
        message="Model training complete",
    )
