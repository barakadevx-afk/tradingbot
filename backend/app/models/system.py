"""System models: AuditLog, SystemEvent, RiskConfig, ExchangeAccount, Strategy, ModelVersion, Alert."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(TimestampMixin, Base):
    """Audit log for tracking all system actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # order, position, user, etc.
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="success", nullable=False
    )  # success, failure
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class SystemEvent(TimestampMixin, Base):
    """System events for monitoring and alerting."""

    __tablename__ = "system_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # error, warning, info, critical
    source: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # service name
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), default="info", nullable=False
    )  # low, medium, high, critical
    is_resolved: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    def __repr__(self) -> str:
        return f"<SystemEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"


class RiskConfig(TimestampMixin, Base):
    """Risk configuration per user."""

    __tablename__ = "risk_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    max_position_size: Mapped[float] = mapped_column(
        Float, default=0.1, nullable=False, server_default="0.1"
    )
    max_daily_loss: Mapped[float] = mapped_column(
        Float, default=0.03, nullable=False, server_default="0.03"
    )
    max_total_loss: Mapped[float] = mapped_column(
        Float, default=0.1, nullable=False, server_default="0.1"
    )
    max_leverage: Mapped[float] = mapped_column(
        Float, default=1.0, nullable=False, server_default="1.0"
    )
    max_open_positions: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False, server_default="5"
    )
    risk_per_trade: Mapped[float] = mapped_column(
        Float, default=0.01, nullable=False, server_default="0.01"
    )
    max_drawdown: Mapped[float] = mapped_column(
        Float, default=0.15, nullable=False, server_default="0.15"
    )
    stop_loss_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )
    take_profit_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )
    trailing_stop_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    trailing_stop_pct: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    kill_switch_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    daily_loss_limit: Mapped[float] = mapped_column(
        Float, default=1000.0, nullable=False, server_default="1000.0"
    )
    max_trades_per_day: Mapped[int] = mapped_column(
        Integer, default=20, nullable=False, server_default="20"
    )

    def __repr__(self) -> str:
        return f"<RiskConfig(id={self.id}, user_id={self.user_id})>"


class ExchangeAccount(TimestampMixin, Base):
    """Exchange account credentials and settings."""

    __tablename__ = "exchange_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    exchange: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    passphrase: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_sandbox: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )
    label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_synced: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="exchange_accounts")

    def __repr__(self) -> str:
        return f"<ExchangeAccount(id={self.id}, exchange={self.exchange}, user_id={self.user_id})>"


class Strategy(TimestampMixin, Base):
    """Trading strategy configuration."""

    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strategy_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ai, manual, copy_trading
    symbols: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # comma-separated
    timeframe: Mapped[str] = mapped_column(
        String(20), default="1h", nullable=False
    )
    parameters: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON string
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    is_paper: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )
    performance_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    total_trades: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, server_default="0"
    )
    win_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    profit_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="strategies")

    def __repr__(self) -> str:
        return f"<Strategy(id={self.id}, name={self.name}, type={self.strategy_type})>"


class ModelVersion(TimestampMixin, Base):
    """AI model version tracking."""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # xgboost, lightgbm, lstm, ensemble
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    is_approved: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    training_data_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_data_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    features_used: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON array
    hyperparameters: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON object
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<ModelVersion(id={self.id}, name={self.model_name}, version={self.version})>"


class Alert(TimestampMixin, Base):
    """Alert model for notifications."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # price, signal, risk, system
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), default="info", nullable=False
    )  # info, warning, critical
    symbol: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    is_dismissed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type}, title={self.title})>"
