"""BARAKA AI Trading Platform - Main Application."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.admin import provision_admin_user
from app.core.config import settings
from app.db.base import SessionLocal, create_tables, engine
from app.services.market_data import MarketDataService

logger = logging.getLogger(__name__)

# Global state
redis_client: redis.Redis | None = None
market_data_service: MarketDataService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager for startup/shutdown events."""
    global redis_client, market_data_service

    # Startup
    # Create database tables
    create_tables()
    with SessionLocal() as db:
        provision_admin_user(db)

    # Initialize Redis
    try:
        redis_client = redis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
    except Exception:
        redis_client = None

    # Initialize market data service
    market_data_service = MarketDataService()

    # Start background tasks
    simulation_task = asyncio.create_task(_run_market_simulation())

    yield

    # Shutdown
    simulation_task.cancel()
    try:
        await simulation_task
    except asyncio.CancelledError:
        pass

    if redis_client:
        await redis_client.close()

    engine.dispose()


async def _run_market_simulation() -> None:
    """Run market data simulation in background."""
    global market_data_service
    if market_data_service:
        try:
            await market_data_service.start_simulation()
        except asyncio.CancelledError:
            if market_data_service:
                market_data_service.stop_simulation()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered trading platform with paper trading, risk management, and portfolio analytics",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Trusted host middleware (production)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.baraka.ai", "*.onrender.com", "localhost", "*.localhost"],
    )


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "type": "internal_error"},
    )


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# WebSocket endpoint for real-time market data
@app.websocket("/ws/market/{symbol}")
async def market_websocket(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time market data."""
    await websocket.accept()

    if not market_data_service:
        await websocket.close(code=1011, reason="Service unavailable")
        return

    async def send_update(data: dict):
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    try:
        await market_data_service.start_websocket(symbol.upper(), send_update)

        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await market_data_service.stop_websocket(symbol.upper(), send_update)


# WebSocket endpoint for portfolio updates
@app.websocket("/ws/portfolio/{user_id}")
async def portfolio_websocket(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time portfolio updates."""
    await websocket.accept()

    try:
        while True:
            # Send portfolio updates every 5 seconds
            await websocket.send_json({
                "type": "portfolio_update",
                "user_id": user_id,
                "timestamp": str(asyncio.get_event_loop().time()),
            })
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
    )
