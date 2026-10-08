"""Kill switch endpoints for emergency trading halt."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.system import RiskConfigRepository
from app.services.risk_engine import RiskEngine

router = APIRouter()


@router.post("/activate")
async def activate_kill_switch(
    reason: str = "Manual activation",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Activate the kill switch to halt all trading."""
    risk_repo = RiskConfigRepository(db)
    config = await risk_repo.get_by_user_id(current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Risk config not found")

    await risk_repo.update(config.id, {"kill_switch_active": True})

    # Close all positions
    risk_engine = RiskEngine(db)
    await risk_engine.emergency_close_all(current_user.id)

    return {
        "message": "Kill switch activated",
        "reason": reason,
        "activated_by": current_user.email,
        "all_positions_closed": True,
    }


@router.post("/deactivate")
async def deactivate_kill_switch(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Deactivate the kill switch."""
    risk_repo = RiskConfigRepository(db)
    config = await risk_repo.get_by_user_id(current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Risk config not found")

    await risk_repo.update(config.id, {"kill_switch_active": False})

    return {
        "message": "Kill switch deactivated",
        "deactivated_by": current_user.email,
    }


@router.get("/status")
async def get_kill_switch_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get kill switch status."""
    risk_repo = RiskConfigRepository(db)
    config = await risk_repo.get_by_user_id(current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Risk config not found")

    return {
        "is_active": config.kill_switch_active,
        "global_kill_switch": settings.KILL_SWITCH_ENABLED,
    }
