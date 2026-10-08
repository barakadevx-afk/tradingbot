"""Backtesting endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.strategy_engine import StrategyEngine

router = APIRouter()


@router.post("")
async def create_backtest(
    strategy_id: int = Query(..., description="Strategy ID to backtest"),
    symbol: str = Query(..., description="Symbol to backtest"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    initial_balance: float = Query(10000.0, gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create and run a backtest."""
    strategy_engine = StrategyEngine(db)
    result = await strategy_engine.run_backtest(
        strategy_id=strategy_id,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_balance=initial_balance,
        user_id=current_user.id,
    )
    return result


@router.get("")
async def get_backtests(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """Get backtest history."""
    strategy_engine = StrategyEngine(db)
    backtests = await strategy_engine.get_backtest_history(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return backtests


@router.get("/{backtest_id}")
async def get_backtest_result(
    backtest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get backtest results."""
    strategy_engine = StrategyEngine(db)
    result = await strategy_engine.get_backtest_result(backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return result


@router.delete("/{backtest_id}")
async def delete_backtest(
    backtest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a backtest."""
    strategy_engine = StrategyEngine(db)
    result = await strategy_engine.delete_backtest(
        backtest_id=backtest_id,
        user_id=current_user.id,
    )
    return result
