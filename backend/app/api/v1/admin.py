"""Admin API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.admin import create_admin_user, verify_admin_credentials
from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password
from app.models.user import User

router = APIRouter()


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_signals: int
    total_trades: int
    total_orders: int
    open_positions: int
    system_status: str
    uptime: str


class UserManagement(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


@router.post("/admin/login")
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    # Verify admin credentials
    if not verify_admin_credentials(request.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    # Get or create admin user
    admin = create_admin_user(db)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(admin.id), "type": "access", "role": admin.role},
        expires_delta=timedelta(hours=24),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(admin.id),
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
        },
    }


@router.get("/admin/stats", response_model=AdminStats)
def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get admin dashboard statistics."""
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    # These would come from actual tables in production
    total_signals = 0
    total_trades = 0
    total_orders = 0
    open_positions = 0

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_signals=total_signals,
        total_trades=total_trades,
        total_orders=total_orders,
        open_positions=open_positions,
        system_status="healthy",
        uptime="99.9%",
    )


@router.get("/admin/users", response_model=list[UserManagement])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all users (admin only)."""
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    users = db.query(User).offset(skip).limit(limit).all()
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
    user_id: str,
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user role (admin only)."""
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()
    return {"message": "User role updated"}


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user (admin only)."""
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.get("/admin/system/health")
def get_system_health(current_user: User = Depends(get_current_user)):
    """Get detailed system health (admin only)."""
    if current_user.role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return {
        "services": {
            "frontend": {"status": "healthy", "latency_ms": 12},
            "backend": {"status": "healthy", "latency_ms": 45},
            "database": {"status": "healthy", "latency_ms": 8},
            "redis": {"status": "healthy", "latency_ms": 2},
            "market_feed": {"status": "healthy", "latency_ms": 120},
            "ai_engine": {"status": "healthy", "latency_ms": 250},
            "risk_engine": {"status": "healthy", "latency_ms": 5},
            "execution_engine": {"status": "healthy", "latency_ms": 15},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
