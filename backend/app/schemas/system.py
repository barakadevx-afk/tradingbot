"""System-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RiskConfigBase(BaseModel):
    """Base risk config schema."""

    max_position_size: float = Field(default=0.1, ge=0.0, le=1.0)
    max_daily_loss: float = Field(default=0.03, ge=0.0, le=1.0)
    max_total_loss: float = Field(default=0.1, ge=0.0, le=1.0)
    max_leverage: float = Field(default=1.0, ge=1.0, le=100.0)
    max_open_positions: int = Field(default=5, ge=1, le=100)
    risk_per_trade: float = Field(default=0.01, ge=0.0, le=1.0)
    max_drawdown: float = Field(default=0.15, ge=0.0, le=1.0)
    stop_loss_enabled: bool = True
    take_profit_enabled: bool = True
    trailing_stop_enabled: bool = False
    trailing_stop_pct: Optional[float] = Field(None, ge=0.0, le=1.0)
    daily_loss_limit: float = Field(default=1000.0, ge=0.0)
    max_trades_per_day: int = Field(default=20, ge=1, le=1000)


class RiskConfigCreate(RiskConfigBase):
    """Schema for creating risk config."""

    pass


class RiskConfigUpdate(BaseModel):
    """Schema for updating risk config."""

    max_position_size: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_daily_loss: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_total_loss: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_leverage: Optional[float] = Field(None, ge=1.0, le=100.0)
    max_open_positions: Optional[int] = Field(None, ge=1, le=100)
    risk_per_trade: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_drawdown: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop_loss_enabled: Optional[bool] = None
    take_profit_enabled: Optional[bool] = None
    trailing_stop_enabled: Optional[bool] = None
    trailing_stop_pct: Optional[float] = Field(None, ge=0.0, le=1.0)
    daily_loss_limit: Optional[float] = Field(None, ge=0.0)
    max_trades_per_day: Optional[int] = Field(None, ge=1, le=1000)


class RiskConfigResponse(RiskConfigBase):
    """Schema for risk config response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    kill_switch_active: bool
    created_at: datetime
    updated_at: datetime


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime


class StrategyBase(BaseModel):
    """Base strategy schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    strategy_type: str = Field(..., min_length=1, max_length=50)
    symbols: Optional[str] = None
    timeframe: str = Field(default="1h", max_length=20)
    parameters: Optional[Dict[str, Any]] = None
    is_paper: bool = True


class StrategyCreate(StrategyBase):
    """Schema for creating a strategy."""

    pass


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    symbols: Optional[str] = None
    timeframe: Optional[str] = Field(None, max_length=20)
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_paper: Optional[bool] = None


class StrategyResponse(StrategyBase):
    """Schema for strategy response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_active: bool
    performance_score: Optional[float] = None
    total_trades: int
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    max_drawdown: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class ModelResponse(BaseModel):
    """Schema for model version response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    model_name: str
    version: str
    model_type: str
    is_active: bool
    is_approved: bool
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    training_data_start: Optional[datetime] = None
    training_data_end: Optional[datetime] = None
    features_used: Optional[List[str]] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    """Schema for alert response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    alert_type: str
    title: str
    message: str
    severity: str
    symbol: Optional[str] = None
    is_read: bool
    is_dismissed: bool
    triggered_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class HealthCheck(BaseModel):
    """Schema for health check response."""

    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
