"""API v1 routers."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    admin,
    markets,
    signals,
    portfolio,
    risk,
    strategies,
    models,
    system,
    paper,
    orders,
    positions,
    trades,
    backtests,
    kill_switch,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
api_router.include_router(markets.router, prefix="/markets", tags=["Markets"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Management"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(models.router, prefix="/models", tags=["AI Models"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(paper.router, prefix="/paper", tags=["Paper Trading"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(positions.router, prefix="/positions", tags=["Positions"])
api_router.include_router(trades.router, prefix="/trades", tags=["Trades"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["Backtests"])
api_router.include_router(kill_switch.router, prefix="/kill-switch", tags=["Kill Switch"])
