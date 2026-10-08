"""Portfolio endpoints."""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.trading import PortfolioRepository
from app.schemas.trading import PortfolioResponse, PositionResponse, TradeResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    """Get current portfolio overview."""
    portfolio_service = PortfolioService(db)
    portfolio = await portfolio_service.get_portfolio(current_user.id)
    return portfolio


@router.get("/performance")
async def get_performance(
    period: str = Query("30d", description="Performance period (7d, 30d, 90d, 1y)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get portfolio performance metrics."""
    portfolio_service = PortfolioService(db)
    performance = await portfolio_service.get_performance(
        user_id=current_user.id,
        period=period,
    )
    return performance


@router.get("/history")
async def get_portfolio_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """Get portfolio value history."""
    portfolio_service = PortfolioService(db)
    history = await portfolio_service.get_portfolio_history(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
    return history


@router.get("/positions", response_model=List[PositionResponse])
async def get_portfolio_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[PositionResponse]:
    """Get all positions in portfolio."""
    portfolio_service = PortfolioService(db)
    positions = await portfolio_service.get_positions(current_user.id)
    return positions


@router.get("/trades", response_model=List[TradeResponse])
async def get_portfolio_trades(
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TradeResponse]:
    """Get recent trades in portfolio."""
    portfolio_service = PortfolioService(db)
    trades = await portfolio_service.get_trades(current_user.id, limit=limit)
    return trades


@router.post("/snapshot")
async def create_portfolio_snapshot(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create a portfolio snapshot."""
    portfolio_service = PortfolioService(db)
    snapshot = await portfolio_service.create_snapshot(current_user.id)
    return {"message": "Portfolio snapshot created", "snapshot_id": snapshot.id}
