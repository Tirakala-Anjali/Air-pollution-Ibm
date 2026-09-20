"""
AirGuard – FastAPI application entry point.

Start the server:
    cd backend
    uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.config import settings
from app.database.connection import create_tables
from app.api import upload, dashboard, events, air_quality, chatbot, demo

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AirGuard starting up …")
    create_tables()
    yield
    logger.info("AirGuard shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "AirGuard API",
    description = (
        "AI-based Air Pollution Event Detection and Early Warning System. "
        "Built for the 1M1B AI for Sustainability Virtual Internship."
    ),
    version     = "1.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.cors_origins_list,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
API_PREFIX = "/api"

app.include_router(upload.router,       prefix=API_PREFIX, tags=["Upload & Analyze"])
app.include_router(dashboard.router,    prefix=API_PREFIX, tags=["Dashboard"])
app.include_router(events.router,       prefix=API_PREFIX, tags=["Events"])
app.include_router(air_quality.router,  prefix=API_PREFIX, tags=["Air Quality"])
app.include_router(chatbot.router,      prefix=API_PREFIX, tags=["Chatbot"])
app.include_router(demo.router,         prefix=API_PREFIX, tags=["Demo"])


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status":  "ok",
        "app":     settings.APP_NAME,
        "version": "1.0.0",
        "env":     settings.APP_ENV,
    }
