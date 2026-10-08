"""Trade history endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.trading import TradeRepository
from app.schemas.trading import TradeResponse

router = APIRouter()


@router.get("", response_model=List[TradeResponse])
async def get_trades(
    symbol: Optional[str] = Query(None),
    side: Optional[str] = Query(None),
    is_paper: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le_limit=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TradeResponse]:
    """Get trade history for current user."""
    trade_repo = TradeRepository(db)
    trades = await trade_repo.get_trades(
        user_id=current_user.id,
        symbol=symbol,
        side=side,
        is_paper=is_paper,
        limit=limit,
        offset=offset,
    )
    return trades


@router.get("/stats")
async def get_trade_stats(
    period: str = Query("30d", description="Stats period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get trade statistics."""
    trade_repo = TradeRepository(db)
    stats = await trade_repo.get_trade_stats(
        user_id=current_user.id,
        period=period,
    )
    return stats


@router.get("/pnl")
async def get_pnl_summary(
    period: str = Query("30d", description="P&L period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get P&L summary."""
    trade_repo = TradeRepository(db)
    pnl = await trade_repo.get_pnl_summary(
        user_id=current_user.id,
        period=period,
    )
    return pnl
