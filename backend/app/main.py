import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_pool, close_pool
from app.redis_client import init_redis, close_redis
from app.middleware import RequestIdAndLoggingMiddleware
from app.exceptions import AppException

# Import API Routers
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.locations import router as locations_router
from app.api.slots import router as slots_router
from app.api.search import router as search_router
from app.api.quotes import router as quotes_router
from app.api.bookings import router as bookings_router
from app.api.payments import router as payments_router
from app.api.chat import router as chat_router
from app.api.auto_booking import router as auto_booking_router
from app.api.operator import router as operator_router
from app.api.admin import router as admin_router

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("backend_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Smart Parking backend...")
    await init_pool()
    await init_redis()
    yield
    await close_pool()
    await close_redis()
    logger.info("Smart Parking backend shutdown complete.")

app = FastAPI(
    title="Smart Parking API",
    version="1.0.0",
    description="Deterministic backend and booking core using raw MySQL (no SQLAlchemy)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Request ID & logging middleware
app.add_middleware(RequestIdAndLoggingMiddleware)

# CORS Middleware
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:80",
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Exception Handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )

# Mount all /api/v1 routes
api_v1_prefix = "/api/v1"
app.include_router(health_router, prefix=api_v1_prefix)
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(locations_router, prefix=api_v1_prefix)
app.include_router(slots_router, prefix=api_v1_prefix)
app.include_router(search_router, prefix=api_v1_prefix)
app.include_router(quotes_router, prefix=api_v1_prefix)
app.include_router(bookings_router, prefix=api_v1_prefix)
app.include_router(payments_router, prefix=api_v1_prefix)
app.include_router(chat_router, prefix=api_v1_prefix)
app.include_router(auto_booking_router, prefix=api_v1_prefix)
app.include_router(operator_router, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)
