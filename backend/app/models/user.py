"""User model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.trading import Order, Position, Trade, PortfolioSnapshot
    from app.models.system import AuditLog, ExchangeAccount, Strategy


class User(TimestampMixin, Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50), default="trader", nullable=False, server_default="trader"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )
    is_2fa_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    totp_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="user", lazy="selectin"
    )
    positions: Mapped[List["Position"]] = relationship(
        "Position", back_populates="user", lazy="selectin"
    )
    trades: Mapped[List["Trade"]] = relationship(
        "Trade", back_populates="user", lazy="selectin"
    )
    portfolio_snapshots: Mapped[List["PortfolioSnapshot"]] = relationship(
        "PortfolioSnapshot", back_populates="user", lazy="selectin"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user", lazy="selectin"
    )
    exchange_accounts: Mapped[List["ExchangeAccount"]] = relationship(
        "ExchangeAccount", back_populates="user", lazy="selectin"
    )
    strategies: Mapped[List["Strategy"]] = relationship(
        "Strategy", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
