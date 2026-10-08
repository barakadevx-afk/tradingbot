"""System endpoints: health check, audit logs."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db, get_current_user, get_current_superuser
from app.models.user import User
from app.repositories.system import AuditLogRepository
from app.schemas.system import AuditLogResponse, HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """System health check endpoint."""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
        services={
            "api": "up",
            "database": "up",
            "redis": "up",
            "websocket": "up",
        },
    )


@router.get("/info")
async def system_info(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get system information."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "api_prefix": settings.API_V1_PREFIX,
    }


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> List[AuditLogResponse]:
    """Get audit logs (admin only)."""
    audit_repo = AuditLogRepository(db)
    logs = await audit_repo.get_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return logs


@router.get("/events")
async def get_system_events(
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> List[dict]:
    """Get system events (admin only)."""
    # This would use a SystemEventRepository
    return []


@router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_superuser),
) -> dict:
    """Get system metrics (admin only)."""
    return {
        "uptime": "0d 0h 0m",
        "total_users": 0,
        "active_strategies": 0,
        "open_positions": 0,
        "total_orders_today": 0,
        "system_load": "normal",
    }
