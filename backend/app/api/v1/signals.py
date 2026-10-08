"""Trading signals endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.trading import SignalRepository
from app.schemas.trading import SignalCreate, SignalResponse

router = APIRouter()


@router.get("", response_model=List[SignalResponse])
async def get_signals(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    signal_type: Optional[str] = Query(None, description="Filter by signal type"),
    source: Optional[str] = Query(None, description="Filter by source"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SignalResponse]:
    """Get trading signals with optional filters."""
    signal_repo = SignalRepository(db)
    signals = await signal_repo.get_signals(
        symbol=symbol,
        signal_type=signal_type,
        source=source,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return signals


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal_by_id(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SignalResponse:
    """Get a specific signal by ID."""
    signal_repo = SignalRepository(db)
    signal = await signal_repo.get_by_id(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.post("", response_model=SignalResponse, status_code=201)
async def create_signal(
    signal_data: SignalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SignalResponse:
    """Create a new trading signal."""
    signal_repo = SignalRepository(db)
    signal = await signal_repo.create(signal_data.model_dump())
    return signal


@router.post("/{signal_id}/execute")
async def execute_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Execute a trading signal."""
    signal_repo = SignalRepository(db)
    signal = await signal_repo.get_by_id(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    # Mark signal as executed
    await signal_repo.update(signal_id, {"executed_at": "now()", "is_active": False})

    return {"message": f"Signal {signal_id} executed successfully"}


@router.delete("/{signal_id}")
async def delete_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a trading signal."""
    signal_repo = SignalRepository(db)
    signal = await signal_repo.get_by_id(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    await signal_repo.delete(signal_id)
    return {"message": f"Signal {signal_id} deleted successfully"}
