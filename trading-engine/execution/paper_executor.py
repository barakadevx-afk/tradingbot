"""
Paper Trading Executor
======================

Simulates realistic trading execution with:
- Order simulation (market, limit, stop orders)
- Fill simulation with slippage and fees
- Position tracking
- P&L calculation (realized and unrealized)
- Equity tracking
- Drawdown calculation
- Starting balance: $10,000
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order types."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderSide(Enum):
    """Order sides."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PositionSide(Enum):
    """Position sides."""
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Fill:
    """Represents a single fill."""
    fill_id: str
    order_id: str
    timestamp: datetime
    price: float
    quantity: float
    fee: float
    fee_asset: str = "USDT"

    @property
    def value(self) -> float:
        """Total value of the fill."""
        return self.price * self.quantity


@dataclass
class Order:
    """Represents a trading order."""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    fee: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    fills: List[Fill] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def remaining_quantity(self) -> float:
        """Remaining quantity to fill."""
        return self.quantity - self.filled_quantity

    @property
    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.filled_quantity >= self.quantity

    @property
    def is_active(self) -> bool:
        """Check if order is still active."""
        return self.status in [OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]


@dataclass
class Position:
    """Represents an open position."""
    position_id: str
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    fee_paid: float = 0.0
    leverage: float = 1.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def notional_value(self) -> float:
        """Current notional value."""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """Total cost basis."""
        return self.quantity * self.entry_price

    def update_price(self, new_price: float) -> None:
        """Update position with new market price."""
        self.current_price = new_price
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (new_price - self.entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.entry_price - new_price) * self.quantity
        self.updated_at = datetime.now(timezone.utc)

    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)."""
        return self.realized_pnl + self.unrealized_pnl


@dataclass
class EquitySnapshot:
    """Snapshot of account equity at a point in time."""
    timestamp: datetime
    equity: float
    available_balance: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    drawdown: float
    open_positions: int


class PaperExecutor:
    """
    Paper trading execution engine.

    Simulates realistic trading with:
    - Market order fills with slippage
    - Limit order fills
    - Trading fees
    - Position tracking
    - P&L calculation
    """

    STARTING_BALANCE: float = 10000.0
    DEFAULT_FEE_RATE: float = 0.001  # 0.1% taker fee
    DEFAULT_SLIPPAGE_PCT: float = 0.02  # 0.02% slippage

    def __init__(
        self,
        starting_balance: float = STARTING_BALANCE,
        fee_rate: float = DEFAULT_FEE_RATE,
        slippage_pct: float = DEFAULT_SLIPPAGE_PCT,
    ):
        self.starting_balance = starting_balance
        self.fee_rate = fee_rate
        self.slippage_pct = slippage_pct

        # Account state
        self._balance: float = starting_balance
        self._equity: float = starting_balance
        self._peak_equity: float = starting_balance
        self._current_drawdown: float = 0.0
        self._realized_pnl: float = 0.0
        self._unrealized_pnl: float = 0.0
        self._total_fees: float = 0.0

        # Tracking
        self._orders: Dict[str, Order] = {}
        self._positions: Dict[str, Position] = {}
        self._fills: List[Fill] = []
        self._equity_history: List[EquitySnapshot] = []
        self._trade_history: List[Dict[str, Any]] = []

        logger.info(f"PaperExecutor initialized with ${starting_balance:,.2f}")

    @property
    def balance(self) -> float:
        """Available balance."""
        return self._balance

    @property
    def equity(self) -> float:
        """Total equity (balance + unrealized P&L)."""
        return self._equity

    @property
    def available_balance(self) -> float:
        """Available balance for new positions."""
        return self._balance

    @property
    def unrealized_pnl(self) -> float:
        """Total unrealized P&L."""
        return self._unrealized_pnl

    @property
    def realized_pnl(self) -> float:
        """Total realized P&L."""
        return self._realized_pnl

    @property
    def total_pnl(self) -> float:
        """Total P&L."""
        return self._realized_pnl + self._unrealized_pnl

    @property
    def total_fees(self) -> float:
        """Total fees paid."""
        return self._total_fees

    @property
    def current_drawdown(self) -> float:
        """Current drawdown from peak."""
        return self._current_drawdown

    @property
    def open_positions(self) -> Dict[str, Position]:
        """Open positions."""
        return self._positions.copy()

    @property
    def open_orders(self) -> Dict[str, Order]:
        """Open orders."""
        return {k: v for k, v in self._orders.items() if v.is_active}

    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        current_price: float,
        leverage: float = 1.0,
    ) -> Order:
        """
        Place a market order.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            current_price: Current market price
            leverage: Leverage

        Returns:
            Order object
        """
        order_id = str(uuid.uuid4())[:12]

        # Apply slippage
        if side == OrderSide.BUY:
            fill_price = current_price * (1 + self.slippage_pct / 100)
        else:
            fill_price = current_price * (1 - self.slippage_pct / 100)

        # Calculate fee
        notional = fill_price * quantity
        fee = notional * self.fee_rate

        # Create order
        order = Order(
            order_id=order_id,
            symbol=symbol,
            order_type=OrderType.MARKET,
            side=side,
            quantity=quantity,
            price=fill_price,
            status=OrderStatus.FILLED,
            filled_quantity=quantity,
            average_fill_price=fill_price,
            fee=fee,
        )

        # Create fill record
        fill = Fill(
            fill_id=str(uuid.uuid4())[:12],
            order_id=order_id,
            timestamp=datetime.now(timezone.utc),
            price=fill_price,
            quantity=quantity,
            fee=fee,
        )
        order.fills.append(fill)
        self._fills.append(fill)

        # Update balance
        self._balance -= fee
        self._total_fees += fee

        # Update or create position
        self._update_position(symbol, side, quantity, fill_price, leverage)

        # Store order
        self._orders[order_id] = order

        # Update equity
        self._update_equity()

        logger.info(f"Market {side.value} {quantity} {symbol} @ {fill_price:.4f} (fee: {fee:.4f})")
        return order

    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        limit_price: float,
        leverage: float = 1.0,
    ) -> Order:
        """
        Place a limit order.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            limit_price: Limit price
            leverage: Leverage

        Returns:
            Order object
        """
        order_id = str(uuid.uuid4())[:12]

        order = Order(
            order_id=order_id,
            symbol=symbol,
            order_type=OrderType.LIMIT,
            side=side,
            quantity=quantity,
            price=limit_price,
            status=OrderStatus.OPEN,
        )

        self._orders[order_id] = order
        logger.info(f"Limit {side.value} {quantity} {symbol} @ {limit_price:.4f}")
        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        if order_id not in self._orders:
            return False

        order = self._orders[order_id]
        if not order.is_active:
            return False

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        logger.info(f"Order {order_id} cancelled")
        return True

    def update_market_price(self, symbol: str, price: float) -> None:
        """Update market price for a symbol and check stops."""
        # Update positions
        if symbol in self._positions:
            position = self._positions[symbol]
            position.update_price(price)

            # Check stop loss
            if position.stop_loss:
                if position.side == PositionSide.LONG and price <= position.stop_loss:
                    self._close_position(symbol, position.stop_loss, "stop_loss")
                elif position.side == PositionSide.SHORT and price >= position.stop_loss:
                    self._close_position(symbol, position.stop_loss, "stop_loss")

            # Check take profit
            if position.take_profit:
                if position.side == PositionSide.LONG and price >= position.take_profit:
                    self._close_position(symbol, position.take_profit, "take_profit")
                elif position.side == PositionSide.SHORT and price <= position.take_profit:
                    self._close_position(symbol, position.take_profit, "take_profit")

        # Check limit orders
        for order in self._orders.values():
            if order.symbol != symbol or not order.is_active:
                continue
            if order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and price <= order.price:
                    self._fill_limit_order(order, price)
                elif order.side == OrderSide.SELL and price >= order.price:
                    self._fill_limit_order(order, price)

        # Update equity
        self._update_equity()

    def _update_position(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        leverage: float,
    ) -> None:
        """Update or create a position."""
        position_side = PositionSide.LONG if side == OrderSide.BUY else PositionSide.SHORT

        if symbol in self._positions:
            position = self._positions[symbol]

            if position.side == position_side:
                # Adding to position
                total_qty = position.quantity + quantity
                avg_price = ((position.entry_price * position.quantity) + (price * quantity)) / total_qty
                position.entry_price = avg_price
                position.quantity = total_qty
                position.fee_paid += quantity * price * self.fee_rate
            else:
                # Reducing or closing position
                if quantity < position.quantity:
                    # Partial close
                    if position.side == PositionSide.LONG:
                        pnl = (price - position.entry_price) * quantity
                    else:
                        pnl = (position.entry_price - price) * quantity
                    position.realized_pnl += pnl
                    self._realized_pnl += pnl
                    position.quantity -= quantity
                elif quantity == position.quantity:
                    # Full close
                    if position.side == PositionSide.LONG:
                        pnl = (price - position.entry_price) * quantity
                    else:
                        pnl = (position.entry_price - price) * quantity
                    position.realized_pnl += pnl
                    self._realized_pnl += pnl
                    del self._positions[symbol]
                else:
                    # Flip position
                    if position.side == PositionSide.LONG:
                        pnl = (price - position.entry_price) * position.quantity
                    else:
                        pnl = (position.entry_price - price) * position.quantity
                    position.realized_pnl += pnl
                    self._realized_pnl += pnl

                    new_qty = quantity - position.quantity
                    position.side = position_side
                    position.entry_price = price
                    position.quantity = new_qty
        else:
            # New position
            position_id = str(uuid.uuid4())[:12]
            self._positions[symbol] = Position(
                position_id=position_id,
                symbol=symbol,
                side=position_side,
                quantity=quantity,
                entry_price=price,
                current_price=price,
                leverage=leverage,
            )

    def _close_position(self, symbol: str, exit_price: float, reason: str) -> None:
        """Close a position."""
        if symbol not in self._positions:
            return

        position = self._positions[symbol]

        # Calculate P&L
        if position.side == PositionSide.LONG:
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity

        # Deduct fees
        fee = position.quantity * exit_price * self.fee_rate
        pnl -= fee
        self._total_fees += fee

        # Update balance
        self._balance += pnl
        self._realized_pnl += pnl

        # Record trade
        self._trade_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "side": position.side.value,
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "pnl": pnl,
            "fee": fee,
            "reason": reason,
        })

        del self._positions[symbol]
        logger.info(f"Position closed: {symbol} @ {exit_price:.4f}, P&L: ${pnl:.2f} ({reason})")

    def _fill_limit_order(self, order: Order, current_price: float) -> None:
        """Fill a limit order."""
        fill_price = order.price
        fee = fill_price * order.quantity * self.fee_rate

        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_fill_price = fill_price
        order.fee = fee
        order.updated_at = datetime.now(timezone.utc)

        fill = Fill(
            fill_id=str(uuid.uuid4())[:12],
            order_id=order.order_id,
            timestamp=datetime.now(timezone.utc),
            price=fill_price,
            quantity=order.quantity,
            fee=fee,
        )
        order.fills.append(fill)
        self._fills.append(fill)

        self._balance -= fee
        self._total_fees += fee

        self._update_position(order.symbol, order.side, order.quantity, fill_price, 1.0)
        self._update_equity()

    def _update_equity(self) -> None:
        """Update total equity and drawdown."""
        self._unrealized_pnl = sum(p.unrealized_pnl for p in self._positions.values())
        self._equity = self._balance + self._unrealized_pnl

        if self._equity > self._peak_equity:
            self._peak_equity = self._equity

        if self._peak_equity > 0:
            self._current_drawdown = (self._peak_equity - self._equity) / self._peak_equity

        # Record snapshot
        self._equity_history.append(EquitySnapshot(
            timestamp=datetime.now(timezone.utc),
            equity=self._equity,
            available_balance=self._balance,
            unrealized_pnl=self._unrealized_pnl,
            realized_pnl=self._realized_pnl,
            total_pnl=self.total_pnl,
            drawdown=self._current_drawdown,
            open_positions=len(self._positions),
        ))

    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        if not self._equity_history:
            return pd.DataFrame()
        return pd.DataFrame([{
            "timestamp": s.timestamp,
            "equity": s.equity,
            "available_balance": s.available_balance,
            "unrealized_pnl": s.unrealized_pnl,
            "realized_pnl": s.realized_pnl,
            "total_pnl": s.total_pnl,
            "drawdown": s.drawdown,
            "open_positions": s.open_positions,
        } for s in self._equity_history])

    def get_trade_history(self) -> pd.DataFrame:
        """Get trade history as DataFrame."""
        if not self._trade_history:
            return pd.DataFrame()
        return pd.DataFrame(self._trade_history)

    def get_position_summary(self) -> pd.DataFrame:
        """Get position summary as DataFrame."""
        if not self._positions:
            return pd.DataFrame()
        return pd.DataFrame([{
            "symbol": p.symbol,
            "side": p.side.value,
            "quantity": p.quantity,
            "entry_price": p.entry_price,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "notional_value": p.notional_value,
            "leverage": p.leverage,
        } for p in self._positions.values()])

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self._trade_history:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "average_pnl": 0.0,
                "max_drawdown": 0.0,
                "total_fees": 0.0,
                "net_pnl": 0.0,
            }

        trades = pd.DataFrame(self._trade_history)
        winning_trades = trades[trades["pnl"] > 0]
        losing_trades = trades[trades["pnl"] <= 0]

        return {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(trades) * 100,
            "average_pnl": trades["pnl"].mean(),
            "average_win": winning_trades["pnl"].mean() if len(winning_trades) > 0 else 0,
            "average_loss": losing_trades["pnl"].mean() if len(losing_trades) > 0 else 0,
            "largest_win": trades["pnl"].max(),
            "largest_loss": trades["pnl"].min(),
            "max_drawdown": self._current_drawdown,
            "total_fees": self._total_fees,
            "net_pnl": self.total_pnl,
            "return_pct": (self.total_pnl / self.starting_balance) * 100,
        }

    def reset(self) -> None:
        """Reset the executor to initial state."""
        self._balance = self.starting_balance
        self._equity = self.starting_balance
        self._peak_equity = self.starting_balance
        self._current_drawdown = 0.0
        self._realized_pnl = 0.0
        self._unrealized_pnl = 0.0
        self._total_fees = 0.0
        self._orders.clear()
        self._positions.clear()
        self._fills.clear()
        self._equity_history.clear()
        self._trade_history.clear()
        logger.info("PaperExecutor reset to initial state")
