"""Trading-related Pydantic schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SignalBase(BaseModel):
    """Base signal schema."""

    symbol: str = Field(..., min_length=1, max_length=50)
    signal_type: str = Field(..., pattern="^(buy|sell|hold)$")
    source: str = Field(..., min_length=1, max_length=50)
    confidence: float = Field(..., ge=0.0, le=1.0)
    entry_price: Optional[Decimal] = None
    target_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    timeframe: str = Field(default="1h", max_length=20)


class SignalCreate(SignalBase):
    """Schema for creating a signal."""

    strategy_id: Optional[int] = None
    model_version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SignalResponse(SignalBase):
    """Schema for signal response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    executed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class OrderBase(BaseModel):
    """Base order schema."""

    symbol: str = Field(..., min_length=1, max_length=50)
    order_type: str = Field(default="market", pattern="^(market|limit|stop_limit)$")
    side: str = Field(..., pattern="^(buy|sell)$")
    quantity: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = Field(default="gtc", pattern="^(gtc|ioc|fok)$")


class OrderCreate(OrderBase):
    """Schema for creating an order."""

    is_paper: bool = True
    signal_id: Optional[int] = None
    strategy_id: Optional[int] = None


class OrderResponse(OrderBase):
    """Schema for order response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    exchange_order_id: Optional[str] = None
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal] = None
    status: str
    is_paper: bool
    commission: Optional[Decimal] = None
    commission_asset: Optional[str] = None
    placed_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PositionResponse(BaseModel):
    """Schema for position response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    symbol: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    current_price: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    realized_pnl: Optional[Decimal] = None
    leverage: float
    liquidation_price: Optional[Decimal] = None
    margin: Optional[Decimal] = None
    is_open: bool
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TradeResponse(BaseModel):
    """Schema for trade response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    order_id: Optional[int] = None
    position_id: Optional[int] = None
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    fee: Optional[Decimal] = None
    pnl: Optional[Decimal] = None
    is_paper: bool
    executed_at: Optional[datetime] = None
    created_at: datetime


class PortfolioResponse(BaseModel):
    """Schema for portfolio response."""

    model_config = ConfigDict(from_attributes=True)

    total_value: Decimal
    cash_balance: Decimal
    positions_value: Decimal
    unrealized_pnl: Optional[Decimal] = None
    realized_pnl: Optional[Decimal] = None
    total_pnl: Optional[Decimal] = None
    drawdown: Optional[Decimal] = None
    positions: List[PositionResponse] = []
    recent_trades: List[TradeResponse] = []


class MarketCandle(BaseModel):
    """Schema for market candle data."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketData(BaseModel):
    """Schema for market data."""

    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    timestamp: datetime
