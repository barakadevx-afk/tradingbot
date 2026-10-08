"""Position management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.trading import PositionRepository
from app.schemas.trading import PositionResponse
from app.services.execution_engine import ExecutionEngine

router = APIRouter()


@router.get("", response_model=List[PositionResponse])
async def get_positions(
    symbol: Optional[str] = Query(None),
    is_open: Optional[bool] = Query(True),
    side: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[PositionResponse]:
    """Get positions for current user."""
    position_repo = PositionRepository(db)
    positions = await position_repo.get_positions(
        user_id=current_user.id,
        symbol=symbol,
        is_open=is_open,
        side=side,
    )
    return positions


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PositionResponse:
    """Get a specific position by ID."""
    position_repo = PositionRepository(db)
    position = await position_repo.get_by_id(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    if position.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return position


@router.post("/{position_id}/close")
async def close_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Close a position."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.close_position(
        user_id=current_user.id,
        position_id=position_id,
    )
    return result


@router.post("/close-all")
async def close_all_positions(
    symbol: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Close all positions."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.close_all_positions(
        user_id=current_user.id,
        symbol=symbol,
    )
    return result


@router.put("/{position_id}/update")
async def update_position(
    position_id: int,
    current_price: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PositionResponse:
    """Update position with current price."""
    position_repo = PositionRepository(db)
    position = await position_repo.get_by_id(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    if position.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = await position_repo.update(
        position_id,
        {"current_price": current_price},
    )
    return updated
