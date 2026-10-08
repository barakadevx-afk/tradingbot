"""Paper trading endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.execution_engine import ExecutionEngine

router = APIRouter()


@router.post("/start")
async def start_paper_trading(
    initial_balance: float = settings.PAPER_TRADING_DEFAULT_BALANCE,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Start paper trading for current user."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.start_paper_trading(
        user_id=current_user.id,
        initial_balance=initial_balance,
    )
    return result


@router.post("/stop")
async def stop_paper_trading(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Stop paper trading for current user."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.stop_paper_trading(current_user.id)
    return result


@router.get("/status")
async def get_paper_trading_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get paper trading status."""
    execution_engine = ExecutionEngine(db)
    status = await execution_engine.get_paper_trading_status(current_user.id)
    return status


@router.get("/balance")
async def get_paper_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get paper trading balance."""
    execution_engine = ExecutionEngine(db)
    balance = await execution_engine.get_paper_balance(current_user.id)
    return balance


@router.post("/reset")
async def reset_paper_trading(
    initial_balance: float = settings.PAPER_TRADING_DEFAULT_BALANCE,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Reset paper trading account."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.reset_paper_trading(
        user_id=current_user.id,
        initial_balance=initial_balance,
    )
    return result
