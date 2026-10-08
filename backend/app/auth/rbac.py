"""Role-based access control (RBAC) system."""

from enum import Enum
from functools import wraps
from typing import Callable, List, Set

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.user import User


class Role(str, Enum):
    """User roles."""

    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permissions for different actions."""

    # User management
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Trading
    TRADE_READ = "trade:read"
    TRADE_CREATE = "trade:create"
    TRADE_UPDATE = "trade:update"
    TRADE_DELETE = "trade:delete"
    TRADE_EXECUTE = "trade:execute"

    # Orders
    ORDER_READ = "order:read"
    ORDER_CREATE = "order:create"
    ORDER_CANCEL = "order:cancel"

    # Positions
    POSITION_READ = "position:read"
    POSITION_CLOSE = "position:close"

    # Portfolio
    PORTFOLIO_READ = "portfolio:read"
    PORTFOLIO_MANAGE = "portfolio:manage"

    # Strategies
    STRATEGY_READ = "strategy:read"
    STRATEGY_CREATE = "strategy:create"
    STRATEGY_UPDATE = "strategy:update"
    STRATEGY_DELETE = "strategy:delete"
    STRATEGY_ACTIVATE = "strategy:activate"

    # Risk
    RISK_READ = "risk:read"
    RISK_UPDATE = "risk:update"
    RISK_MANAGE = "risk:manage"

    # Models
    MODEL_READ = "model:read"
    MODEL_TRAIN = "model:train"
    MODEL_APPROVE = "model:approve"
    MODEL_MANAGE = "model:manage"

    # System
    SYSTEM_READ = "system:read"
    SYSTEM_MANAGE = "system:manage"
    AUDIT_READ = "audit:read"

    # Alerts
    ALERT_READ = "alert:read"
    ALERT_MANAGE = "alert:manage"

    # Backtest
    BACKTEST_READ = "backtest:read"
    BACKTEST_CREATE = "backtest:create"

    # Paper trading
    PAPER_TRADING = "paper:trading"


# Role-permission mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.USER_READ,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.TRADE_READ,
        Permission.TRADE_CREATE,
        Permission.TRADE_UPDATE,
        Permission.TRADE_DELETE,
        Permission.TRADE_EXECUTE,
        Permission.ORDER_READ,
        Permission.ORDER_CREATE,
        Permission.ORDER_CANCEL,
        Permission.POSITION_READ,
        Permission.POSITION_CLOSE,
        Permission.PORTFOLIO_READ,
        Permission.PORTFOLIO_MANAGE,
        Permission.STRATEGY_READ,
        Permission.STRATEGY_CREATE,
        Permission.STRATEGY_UPDATE,
        Permission.STRATEGY_DELETE,
        Permission.STRATEGY_ACTIVATE,
        Permission.RISK_READ,
        Permission.RISK_UPDATE,
        Permission.RISK_MANAGE,
        Permission.MODEL_READ,
        Permission.MODEL_TRAIN,
        Permission.MODEL_APPROVE,
        Permission.MODEL_MANAGE,
        Permission.SYSTEM_READ,
        Permission.SYSTEM_MANAGE,
        Permission.AUDIT_READ,
        Permission.ALERT_READ,
        Permission.ALERT_MANAGE,
        Permission.BACKTEST_READ,
        Permission.BACKTEST_CREATE,
        Permission.PAPER_TRADING,
    },
    Role.TRADER: {
        Permission.TRADE_READ,
        Permission.TRADE_CREATE,
        Permission.TRADE_EXECUTE,
        Permission.ORDER_READ,
        Permission.ORDER_CREATE,
        Permission.ORDER_CANCEL,
        Permission.POSITION_READ,
        Permission.POSITION_CLOSE,
        Permission.PORTFOLIO_READ,
        Permission.STRATEGY_READ,
        Permission.STRATEGY_CREATE,
        Permission.STRATEGY_UPDATE,
        Permission.STRATEGY_DELETE,
        Permission.STRATEGY_ACTIVATE,
        Permission.RISK_READ,
        Permission.RISK_UPDATE,
        Permission.MODEL_READ,
        Permission.ALERT_READ,
        Permission.ALERT_MANAGE,
        Permission.BACKTEST_READ,
        Permission.BACKTEST_CREATE,
        Permission.PAPER_TRADING,
    },
    Role.VIEWER: {
        Permission.TRADE_READ,
        Permission.ORDER_READ,
        Permission.POSITION_READ,
        Permission.PORTFOLIO_READ,
        Permission.STRATEGY_READ,
        Permission.RISK_READ,
        Permission.MODEL_READ,
        Permission.ALERT_READ,
        Permission.BACKTEST_READ,
    },
}


def get_role_permissions(role: str) -> Set[Permission]:
    """Get all permissions for a role."""
    try:
        role_enum = Role(role)
        return ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return set()


def has_permission(user: User, permission: Permission) -> bool:
    """Check if a user has a specific permission."""
    user_permissions = get_role_permissions(user.role)
    return permission in user_permissions


def has_any_permission(user: User, permissions: List[Permission]) -> bool:
    """Check if a user has any of the specified permissions."""
    user_permissions = get_role_permissions(user.role)
    return any(p in user_permissions for p in permissions)


def has_all_permissions(user: User, permissions: List[Permission]) -> bool:
    """Check if a user has all of the specified permissions."""
    user_permissions = get_role_permissions(user.role)
    return all(p in user_permissions for p in permissions)


def require_permissions(*permissions: Permission):
    """Decorator/dependency to require specific permissions."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = get_role_permissions(current_user.role)

        for permission in permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )

        return current_user

    return dependency


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_trader_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require trader or admin role."""
    if current_user.role not in (Role.TRADER, Role.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trader or admin access required",
        )
    return current_user
