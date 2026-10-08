"""Trading-related database models."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SignalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class PositionSide(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class ExitReason(str, enum.Enum):
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    TRAILING_STOP = "TRAILING_STOP"
    MANUAL = "MANUAL"
    SIGNAL_REVERSAL = "SIGNAL_REVERSAL"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    EXPIRED = "EXPIRED"


class ExchangeAccount(Base):
    __tablename__ = "exchange_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False)  # binance, bybit
    name = Column(String(100), nullable=False)
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text, nullable=False)
    is_testnet = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    trading_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False)  # BTCUSDT
    base_asset = Column(String(10), nullable=False)  # BTC
    quote_asset = Column(String(10), nullable=False)  # USDT
    is_enabled = Column(Boolean, default=True)
    min_quantity = Column(Float, default=0.0001)
    max_quantity = Column(Float, default=1000.0)
    tick_size = Column(Float, default=0.01)
    step_size = Column(Float, default=0.0001)
    min_notional = Column(Float, default=10.0)
    asset_quality_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(String(36), unique=True, nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    signal = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    risk_reward = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False)
    market_regime = Column(String(20), nullable=False)
    strategy = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    status = Column(SQLEnum(SignalStatus), default=SignalStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(36), unique=True, nullable=False)
    client_order_id = Column(String(36), nullable=True)
    exchange_order_id = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signal_id = Column(String(36), nullable=True)
    symbol = Column(String(20), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    type = Column(SQLEnum(OrderType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    filled_quantity = Column(Float, default=0.0)
    average_fill_price = Column(Float, nullable=True)
    fees = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    exchange = Column(String(50), nullable=False)
    is_paper = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(String(36), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(SQLEnum(PositionSide), nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    leverage = Column(Integer, default=1)
    is_open = Column(Boolean, default=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    exit_reason = Column(SQLEnum(ExitReason), nullable=True)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(36), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position_id = Column(String(36), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(SQLEnum(PositionSide), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    strategy = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=True)
    signal_confidence = Column(Float, nullable=True)
    market_regime = Column(String(20), nullable=False)
    fees = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    pnl = Column(Float, nullable=False)
    pnl_percent = Column(Float, nullable=False)
    risk_percent = Column(Float, nullable=False)
    duration_minutes = Column(Float, nullable=True)
    exit_reason = Column(SQLEnum(ExitReason), nullable=False)
    is_paper = Column(Boolean, default=True)
    opened_at = Column(DateTime(timezone=True), nullable=False)
    closed_at = Column(DateTime(timezone=True), server_default=func.now())


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    open_exposure = Column(Float, nullable=False)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    weekly_pnl = Column(Float, default=0.0)
    monthly_pnl = Column(Float, default=0.0)
    drawdown = Column(Float, default=0.0)
    leverage = Column(Float, default=0.0)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now())


class RiskConfig(Base):
    __tablename__ = "risk_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_per_trade = Column(Float, default=0.005)
    max_risk_per_trade = Column(Float, default=0.01)
    max_daily_loss = Column(Float, default=0.03)
    max_weekly_loss = Column(Float, default=0.05)
    max_drawdown = Column(Float, default=0.10)
    max_open_positions = Column(Integer, default=5)
    max_portfolio_exposure = Column(Float, default=0.80)
    max_symbol_exposure = Column(Float, default=0.30)
    max_leverage = Column(Integer, default=1)
    max_consecutive_losses = Column(Integer, default=5)
    min_confidence = Column(Float, default=0.70)
    min_risk_reward = Column(Float, default=1.5)
    kill_switch_active = Column(Boolean, default=False)
    consecutive_losses = Column(Integer, default=0)
    daily_loss_used = Column(Float, default=0.0)
    weekly_loss_used = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DrawdownEvent(Base):
    __tablename__ = "drawdown_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    peak_value = Column(Float, nullable=False)
    trough_value = Column(Float, nullable=False)
    drawdown_percent = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)


class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(36), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    strategy = Column(String(50), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    starting_balance = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    total_trades = Column(Integer, nullable=False)
    parameters = Column(Text, nullable=True)  # JSON string
    status = Column(String(20), default="COMPLETED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(36), ForeignKey("backtests.backtest_id"), nullable=False)
    trade_number = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    pnl = Column(Float, nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="INFO")  # INFO, WARNING, CRITICAL
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TradingSession(Base):
    __tablename__ = "trading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), unique=True, nullable=False)
    mode = Column(String(20), nullable=False)  # PAPER, LIVE
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(36), ForeignKey("trades.trade_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    emotions = Column(String(50), nullable=True)
    lessons_learned = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
