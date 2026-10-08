"""
Position Sizing Module
======================

Provides risk-based position sizing with exchange precision handling:
- Risk-based position size calculation
- Exchange precision rounding
- Minimum order quantity enforcement
- Minimum notional value checks
- Leverage considerations
- Exposure limit validation
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SizingResult:
    """Result of position sizing calculation."""
    position_size: float
    notional_value: float
    risk_amount: float
    risk_percentage: float
    leverage: float
    is_valid: bool
    message: str
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "position_size": self.position_size,
            "notional_value": self.notional_value,
            "risk_amount": self.risk_amount,
            "risk_percentage": self.risk_percentage,
            "leverage": self.leverage,
            "is_valid": self.is_valid,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class ExchangeConstraints:
    """Exchange-specific trading constraints."""
    symbol: str
    min_qty: float
    max_qty: float
    qty_step: float  # Quantity precision step
    min_notional: float
    max_leverage: float
    price_precision: int  # Decimal places for price
    qty_precision: int  # Decimal places for quantity


class PositionSizer:
    """
    Risk-based position sizing calculator.

    Calculates position size based on:
    - Account equity
    - Risk percentage per trade
    - Stop-loss distance
    - Exchange constraints
    """

    # Default exchange constraints for major pairs
    DEFAULT_CONSTRAINTS: Dict[str, ExchangeConstraints] = {
        "BTCUSDT": ExchangeConstraints("BTCUSDT", 0.00001, 9000, 0.00001, 10.0, 125, 2, 5),
        "ETHUSDT": ExchangeConstraints("ETHUSDT", 0.0001, 9000, 0.0001, 10.0, 100, 2, 4),
        "SOLUSDT": ExchangeConstraints("SOLUSDT", 0.01, 900000, 0.01, 10.0, 50, 2, 2),
        "BNBUSDT": ExchangeConstraints("BNBUSDT", 0.001, 9000, 0.001, 10.0, 100, 2, 3),
        "XRPUSDT": ExchangeConstraints("XRPUSDT", 0.1, 9000000, 0.1, 10.0, 50, 4, 1),
        "ADAUSDT": ExchangeConstraints("ADAUSDT", 0.1, 9000000, 0.1, 10.0, 50, 4, 1),
        "DOGEUSDT": ExchangeConstraints("DOGEUSDT", 1, 900000000, 1, 10.0, 50, 5, 0),
    }

    def __init__(
        self,
        equity: float = 10000.0,
        risk_per_trade: float = 0.005,
        max_leverage: float = 3.0,
    ):
        self.equity = equity
        self.risk_per_trade = risk_per_trade
        self.max_leverage = max_leverage
        self._constraints: Dict[str, ExchangeConstraints] = {}

    def set_constraints(self, symbol: str, constraints: ExchangeConstraints) -> None:
        """Set exchange constraints for a symbol."""
        self._constraints[symbol] = constraints

    def get_constraints(self, symbol: str) -> ExchangeConstraints:
        """Get constraints for a symbol."""
        if symbol in self._constraints:
            return self._constraints[symbol]
        return self.DEFAULT_CONSTRAINTS.get(symbol, ExchangeConstraints(
            symbol=symbol,
            min_qty=0.00001,
            max_qty=9000000,
            qty_step=0.00001,
            min_notional=10.0,
            max_leverage=100,
            price_precision=8,
            qty_precision=5,
        ))

    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        take_profit: Optional[float] = None,
        risk_percentage: Optional[float] = None,
        leverage: float = 1.0,
        current_exposure: float = 0.0,
        max_exposure: float = 0.5,
    ) -> SizingResult:
        """
        Calculate position size based on risk parameters.

        Formula:
            Risk Amount = Equity * Risk%
            Position Size = Risk Amount / |Entry - Stop Loss|

        Args:
            symbol: Trading symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price (optional)
            risk_percentage: Risk percentage (uses default if None)
            leverage: Leverage to use
            current_exposure: Current portfolio exposure
            max_exposure: Maximum allowed exposure

        Returns:
            SizingResult with position size and validation
        """
        risk_pct = risk_percentage or self.risk_per_trade

        # Validate inputs
        if entry_price <= 0:
            return SizingResult(
                position_size=0, notional_value=0, risk_amount=0,
                risk_percentage=0, leverage=leverage, is_valid=False,
                message="Entry price must be positive",
            )

        if stop_loss <= 0:
            return SizingResult(
                position_size=0, notional_value=0, risk_amount=0,
                risk_percentage=0, leverage=leverage, is_valid=False,
                message="Stop loss must be positive",
            )

        if entry_price == stop_loss:
            return SizingResult(
                position_size=0, notional_value=0, risk_amount=0,
                risk_percentage=0, leverage=leverage, is_valid=False,
                message="Entry price cannot equal stop loss",
            )

        # Get constraints
        constraints = self.get_constraints(symbol)

        # Validate leverage
        if leverage > constraints.max_leverage:
            return SizingResult(
                position_size=0, notional_value=0, risk_amount=0,
                risk_percentage=0, leverage=leverage, is_valid=False,
                message=f"Leverage {leverage}x exceeds max {constraints.max_leverage}x for {symbol}",
            )

        if leverage > self.max_leverage:
            return SizingResult(
                position_size=0, notional_value=0, risk_amount=0,
                risk_percentage=0, leverage=leverage, is_valid=False,
                message=f"Leverage {leverage}x exceeds system max {self.max_leverage}x",
            )

        # Calculate risk amount
        risk_amount = self.equity * risk_pct

        # Calculate stop-loss distance
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance == 0:
            return SizingResult(
                position_size=0, notional_value=0, risk_amount=0,
                risk_percentage=0, leverage=leverage, is_valid=False,
                message="Stop loss distance cannot be zero",
            )

        # Calculate raw position size
        raw_position_size = risk_amount / stop_distance

        # Apply leverage
        leveraged_size = raw_position_size * leverage

        # Round to exchange precision
        position_size = self._round_to_precision(leveraged_size, constraints.qty_step, constraints.qty_precision)

        # Validate minimum quantity
        if position_size < constraints.min_qty:
            return SizingResult(
                position_size=position_size, notional_value=0, risk_amount=risk_amount,
                risk_percentage=risk_pct, leverage=leverage, is_valid=False,
                message=f"Position size {position_size} below minimum {constraints.min_qty}",
                details={"min_qty": constraints.min_qty},
            )

        # Validate maximum quantity
        if position_size > constraints.max_qty:
            position_size = self._round_to_precision(constraints.max_qty, constraints.qty_step, constraints.qty_precision)

        # Calculate notional value
        notional_value = position_size * entry_price

        # Validate minimum notional
        if notional_value < constraints.min_notional:
            return SizingResult(
                position_size=position_size, notional_value=notional_value, risk_amount=risk_amount,
                risk_percentage=risk_pct, leverage=leverage, is_valid=False,
                message=f"Notional value {notional_value:.2f} below minimum {constraints.min_notional}",
                details={"min_notional": constraints.min_notional},
            )

        # Check exposure limits
        new_exposure = notional_value / self.equity if self.equity > 0 else 0
        if current_exposure + new_exposure > max_exposure:
            # Reduce position size to fit within exposure limit
            available_exposure = max_exposure - current_exposure
            max_notional = available_exposure * self.equity
            max_position_size = max_notional / entry_price
            position_size = self._round_to_precision(max_position_size, constraints.qty_step, constraints.qty_precision)
            notional_value = position_size * entry_price
            new_exposure = notional_value / self.equity if self.equity > 0 else 0

        # Recalculate actual risk with final position size
        actual_risk = position_size * stop_distance
        actual_risk_pct = actual_risk / self.equity if self.equity > 0 else 0

        # Calculate risk/reward if take profit provided
        risk_reward = 0.0
        if take_profit and take_profit > 0:
            reward = abs(take_profit - entry_price) * position_size
            risk_reward = reward / actual_risk if actual_risk > 0 else 0

        return SizingResult(
            position_size=position_size,
            notional_value=notional_value,
            risk_amount=actual_risk,
            risk_percentage=actual_risk_pct,
            leverage=leverage,
            is_valid=True,
            message="Position size calculated successfully",
            details={
                "raw_position_size": raw_position_size,
                "stop_distance": stop_distance,
                "exposure": new_exposure,
                "risk_reward": risk_reward,
                "constraints": {
                    "min_qty": constraints.min_qty,
                    "max_qty": constraints.max_qty,
                    "min_notional": constraints.min_notional,
                },
            },
        )

    def _round_to_precision(self, value: float, step: float, precision: int) -> float:
        """Round value to exchange precision."""
        # First round to step size
        rounded = round(value / step) * step
        # Then round to decimal places
        return round(rounded, precision)

    def update_equity(self, new_equity: float) -> None:
        """Update account equity."""
        self.equity = new_equity

    def get_max_position_size(
        self,
        symbol: str,
        entry_price: float,
        leverage: float = 1.0,
    ) -> float:
        """Get maximum allowed position size for a symbol."""
        constraints = self.get_constraints(symbol)
        max_notional = self.equity * self.max_leverage * leverage
        max_size = max_notional / entry_price
        return self._round_to_precision(max_size, constraints.qty_step, constraints.qty_precision)
