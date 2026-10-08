"""System repositories for audit logs, risk configs, strategies, models, and alerts."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import (
    AuditLog,
    SystemEvent,
    RiskConfig,
    ExchangeAccount,
    Strategy,
    ModelVersion,
    Alert,
)
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit logs."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditLog)

    async def get_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLog]:
        """Get audit logs with filters."""
        query = select(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if status:
            query = query.where(AuditLog.status == status)

        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class RiskConfigRepository(BaseRepository[RiskConfig]):
    """Repository for risk configurations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, RiskConfig)

    async def get_by_user_id(self, user_id: int) -> Optional[RiskConfig]:
        """Get risk config by user ID."""
        result = await self.db.execute(
            select(RiskConfig).where(RiskConfig.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, **kwargs) -> RiskConfig:
        """Create risk config for a user."""
        config = RiskConfig(user_id=user_id, **kwargs)
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config


class StrategyRepository(BaseRepository[Strategy]):
    """Repository for strategies."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Strategy)

    async def get_strategies(
        self,
        user_id: int,
        is_active: Optional[bool] = None,
        strategy_type: Optional[str] = None,
    ) -> List[Strategy]:
        """Get strategies with filters."""
        query = select(Strategy).where(Strategy.user_id == user_id)

        if is_active is not None:
            query = query.where(Strategy.is_active == is_active)
        if strategy_type:
            query = query.where(Strategy.strategy_type == strategy_type)

        query = query.order_by(Strategy.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_strategies(self) -> List[Strategy]:
        """Get all active strategies."""
        result = await self.db.execute(
            select(Strategy).where(Strategy.is_active == True)
        )
        return list(result.scalars().all())


class ModelRepository(BaseRepository[ModelVersion]):
    """Repository for AI model versions."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ModelVersion)

    async def get_models(
        self,
        model_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_approved: Optional[bool] = None,
    ) -> List[ModelVersion]:
        """Get models with filters."""
        query = select(ModelVersion)

        if model_type:
            query = query.where(ModelVersion.model_type == model_type)
        if is_active is not None:
            query = query.where(ModelVersion.is_active == is_active)
        if is_approved is not None:
            query = query.where(ModelVersion.is_approved == is_approved)

        query = query.order_by(ModelVersion.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_model(self) -> Optional[ModelVersion]:
        """Get the currently active model."""
        result = await self.db.execute(
            select(ModelVersion).where(ModelVersion.is_active == True)
        )
        return result.scalar_one_or_none()

    async def deactivate_all_by_type(self, model_type: str) -> None:
        """Deactivate all models of a specific type."""
        await self.db.execute(
            update(ModelVersion)
            .where(ModelVersion.model_type == model_type)
            .values(is_active=False)
        )
        await self.db.flush()


class SystemEventRepository(BaseRepository[SystemEvent]):
    """Repository for system events."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, SystemEvent)

    async def get_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SystemEvent]:
        """Get system events with filters."""
        query = select(SystemEvent)

        if event_type:
            query = query.where(SystemEvent.event_type == event_type)
        if severity:
            query = query.where(SystemEvent.severity == severity)
        if is_resolved is not None:
            query = query.where(SystemEvent.is_resolved == is_resolved)

        query = query.order_by(SystemEvent.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class SystemEventRepository(BaseRepository[SystemEvent]):
    """Repository for system events."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, SystemEvent)

    async def get_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SystemEvent]:
        """Get system events with filters."""
        query = select(SystemEvent)

        if event_type:
            query = query.where(SystemEvent.event_type == event_type)
        if severity:
            query = query.where(SystemEvent.severity == severity)
        if is_resolved is not None:
            query = query.where(SystemEvent.is_resolved == is_resolved)

        query = query.order_by(SystemEvent.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class AlertRepository(BaseRepository[Alert]):
    """Repository for alerts."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Alert)

    async def get_alerts(
        self,
        user_id: Optional[int] = None,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_read: Optional[bool] = None,
        is_dismissed: Optional[bool] = None,
        symbol: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Alert]:
        """Get alerts with filters."""
        query = select(Alert)

        if user_id:
            query = query.where(Alert.user_id == user_id)
        if alert_type:
            query = query.where(Alert.alert_type == alert_type)
        if severity:
            query = query.where(Alert.severity == severity)
        if is_read is not None:
            query = query.where(Alert.is_read == is_read)
        if is_dismissed is not None:
            query = query.where(Alert.is_dismissed == is_dismissed)
        if symbol:
            query = query.where(Alert.symbol == symbol)

        query = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread alerts for a user."""
        result = await self.db.execute(
            select(func.count(Alert.id)).where(
                Alert.user_id == user_id,
                Alert.is_read == False,
            )
        )
        return result.scalar() or 0

    async def delete_old_alerts(self, cutoff: datetime) -> int:
        """Delete alerts older than cutoff date."""
        result = await self.db.execute(
            delete(Alert).where(
                Alert.is_dismissed == True,
                Alert.dismissed_at < cutoff,
            )
        )
        await self.db.flush()
        return result.rowcount
