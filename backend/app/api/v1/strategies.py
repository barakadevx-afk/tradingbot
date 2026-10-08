"""Strategy management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.system import StrategyRepository
from app.schemas.system import StrategyCreate, StrategyResponse, StrategyUpdate

router = APIRouter()


@router.get("", response_model=List[StrategyResponse])
async def get_strategies(
    is_active: Optional[bool] = Query(None),
    strategy_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[StrategyResponse]:
    """Get all strategies for current user."""
    strategy_repo = StrategyRepository(db)
    strategies = await strategy_repo.get_strategies(
        user_id=current_user.id,
        is_active=is_active,
        strategy_type=strategy_type,
    )
    return strategies


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Get a specific strategy by ID."""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return strategy


@router.post("", response_model=StrategyResponse, status_code=201)
async def create_strategy(
    strategy_data: StrategyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Create a new strategy."""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.create(
        user_id=current_user.id,
        **strategy_data.model_dump(),
    )
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Update a strategy."""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = strategy_data.model_dump(exclude_unset=True)
    updated_strategy = await strategy_repo.update(strategy_id, update_data)
    return updated_strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a strategy."""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    await strategy_repo.delete(strategy_id)
    return {"message": "Strategy deleted successfully"}


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Activate a strategy."""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = await strategy_repo.update(strategy_id, {"is_active": True})
    return updated


@router.post("/{strategy_id}/deactivate")
async def deactivate_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Deactivate a strategy."""
    strategy_repo = StrategyRepository(db)
    strategy = await strategy_repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = await strategy_repo.update(strategy_id, {"is_active": False})
    return updated
