"""Audit logging service."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import AuditLog
from app.repositories.system import AuditLogRepository


class AuditService:
    """Service for audit logging."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditLogRepository(db)

    async def log_action(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        request: Optional[Request] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """Log an action to the audit log."""
        ip_address = None
        user_agent = None

        if request:
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent")

        log_entry = await self.audit_repo.create(
            {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "status": status,
                "error_message": error_message,
            },
        )

        return log_entry

    async def log_order_created(
        self,
        user_id: int,
        order_id: int,
        symbol: str,
        side: str,
        quantity: float,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log order creation."""
        return await self.log_action(
            action="order_created",
            resource_type="order",
            user_id=user_id,
            resource_id=str(order_id),
            details=f"{side} {quantity} {symbol}",
            request=request,
        )

    async def log_order_cancelled(
        self,
        user_id: int,
        order_id: int,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log order cancellation."""
        return await self.log_action(
            action="order_cancelled",
            resource_type="order",
            user_id=user_id,
            resource_id=str(order_id),
            request=request,
        )

    async def log_position_closed(
        self,
        user_id: int,
        position_id: int,
        symbol: str,
        pnl: float,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log position closure."""
        return await self.log_action(
            action="position_closed",
            resource_type="position",
            user_id=user_id,
            resource_id=str(position_id),
            details=f"Closed {symbol} with P&L: {pnl}",
            request=request,
        )

    async def log_user_login(
        self,
        user_id: int,
        request: Optional[Request] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """Log user login."""
        return await self.log_action(
            action="user_login",
            resource_type="user",
            user_id=user_id,
            request=request,
            status=status,
            error_message=error_message,
        )

    async def log_user_logout(
        self,
        user_id: int,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log user logout."""
        return await self.log_action(
            action="user_logout",
            resource_type="user",
            user_id=user_id,
            request=request,
        )

    async def log_strategy_action(
        self,
        user_id: int,
        strategy_id: int,
        action: str,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log strategy action."""
        return await self.log_action(
            action=f"strategy_{action}",
            resource_type="strategy",
            user_id=user_id,
            resource_id=str(strategy_id),
            request=request,
        )

    async def log_risk_config_change(
        self,
        user_id: int,
        changes: Dict,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log risk configuration change."""
        return await self.log_action(
            action="risk_config_updated",
            resource_type="risk_config",
            user_id=user_id,
            details=str(changes),
            request=request,
        )

    async def log_kill_switch(
        self,
        user_id: int,
        activated: bool,
        reason: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log kill switch activation/deactivation."""
        action = "kill_switch_activated" if activated else "kill_switch_deactivated"
        return await self.log_action(
            action=action,
            resource_type="system",
            user_id=user_id,
            details=reason,
            request=request,
        )

    async def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLog]:
        """Get audit logs with filters."""
        return await self.audit_repo.get_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            status=status,
            limit=limit,
            offset=offset,
        )

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
