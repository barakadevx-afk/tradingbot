"""Admin API endpoints."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.trading import Order, Position, Signal, Trade
from app.models.user import User

router = APIRouter()

ADMIN_ROLES = {"SUPER_ADMIN", "ADMIN"}
ASSIGNABLE_ROLES = {"TRADER", "ANALYST", "VIEWER"}


def require_admin(user: User) -> None:
    if user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


def require_super_admin(user: User) -> None:
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super administrator access required",
        )


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_signals: int
    total_trades: int
    total_orders: int
    open_positions: int
    system_status: str


class UserManagement(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


@router.get("/admin/stats", response_model=AdminStats)
def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get admin dashboard statistics."""
    require_admin(current_user)

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_signals=db.query(Signal).count(),
        total_trades=db.query(Trade).count(),
        total_orders=db.query(Order).count(),
        open_positions=db.query(Position).filter(Position.is_open.is_(True)).count(),
        system_status="healthy",
    )


@router.get("/admin/users", response_model=list[UserManagement])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all users (admin only)."""
    require_admin(current_user)

    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [
        UserManagement(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a user's non-administrator role."""
    require_super_admin(current_user)
    normalized_role = role.upper()
    if normalized_role not in ASSIGNABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role must be TRADER, ANALYST, or VIEWER",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    user.role = normalized_role
    db.commit()
    return {"message": "User role updated"}


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a user without allowing removal of an administrator account."""
    require_super_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id or user.role in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrator accounts cannot be deleted through this endpoint",
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.get("/admin/system/health")
def get_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed system health (admin only)."""
    require_admin(current_user)

    db.execute(text("SELECT 1"))
    return {
        "services": {
            "backend": {"status": "healthy"},
            "database": {"status": "healthy"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
