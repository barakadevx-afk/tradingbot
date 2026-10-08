"""Order management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.trading import OrderRepository
from app.schemas.trading import OrderCreate, OrderResponse
from app.services.execution_engine import ExecutionEngine

router = APIRouter()


@router.get("", response_model=List[OrderResponse])
async def get_orders(
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    side: Optional[str] = Query(None),
    is_paper: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[OrderResponse]:
    """Get orders for current user."""
    order_repo = OrderRepository(db)
    orders = await order_repo.get_orders(
        user_id=current_user.id,
        symbol=symbol,
        status=status,
        side=side,
        is_paper=is_paper,
        limit=limit,
        offset=offset,
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    """Get a specific order by ID."""
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return order


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    """Create a new order."""
    execution_engine = ExecutionEngine(db)
    order = await execution_engine.place_order(
        user_id=current_user.id,
        order_data=order_data,
    )
    return order


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Cancel an order."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.cancel_order(
        user_id=current_user.id,
        order_id=order_id,
    )
    return result


@router.post("/cancel-all")
async def cancel_all_orders(
    symbol: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Cancel all open orders."""
    execution_engine = ExecutionEngine(db)
    result = await execution_engine.cancel_all_orders(
        user_id=current_user.id,
        symbol=symbol,
    )
    return result
