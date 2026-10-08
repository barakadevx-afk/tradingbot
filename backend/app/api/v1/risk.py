"""Risk management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.system import RiskConfigRepository
from app.schemas.system import RiskConfigCreate, RiskConfigResponse, RiskConfigUpdate
from app.services.risk_engine import RiskEngine

router = APIRouter()


@router.get("/config", response_model=RiskConfigResponse)
async def get_risk_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskConfigResponse:
    """Get risk configuration for current user."""
    risk_repo = RiskConfigRepository(db)
    config = await risk_repo.get_by_user_id(current_user.id)
    if not config:
        # Create default config
        config = await risk_repo.create(
            user_id=current_user.id,
            **RiskConfigCreate().model_dump(),
        )
    return config


@router.put("/config", response_model=RiskConfigResponse)
async def update_risk_config(
    config_data: RiskConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskConfigResponse:
    """Update risk configuration."""
    risk_repo = RiskConfigRepository(db)
    config = await risk_repo.get_by_user_id(current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Risk config not found")

    update_data = config_data.model_dump(exclude_unset=True)
    updated_config = await risk_repo.update(config.id, update_data)
    return updated_config


@router.post("/validate")
async def validate_trade_risk(
    symbol: str,
    quantity: float,
    price: float,
    side: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Validate a trade against risk parameters."""
    risk_engine = RiskEngine(db)
    validation_result = await risk_engine.validate_trade(
        user_id=current_user.id,
        symbol=symbol,
        quantity=quantity,
        price=price,
        side=side,
    )
    return validation_result


@router.get("/status")
async def get_risk_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get current risk status and metrics."""
    risk_engine = RiskEngine(db)
    status = await risk_engine.get_risk_status(current_user.id)
    return status


@router.get("/exposure")
async def get_risk_exposure(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get current risk exposure."""
    risk_engine = RiskEngine(db)
    exposure = await risk_engine.get_exposure(current_user.id)
    return exposure
