"""
Risk Management Engine
======================

Provides comprehensive risk management for the trading system:
- Risk per trade limits (0.5% default, 1% max)
- Daily/weekly loss limits
- Maximum drawdown protection
- Position limits (total, per symbol, portfolio exposure)
- Leverage constraints
- Consecutive loss tracking
- Never uses Martingale or averaging down
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RiskStatus(Enum):
    """Risk check status."""
    APPROVED = "APPROVED"
    REJECTED = "REjected"
    WARNING = "WARNING"


@dataclass
class RiskParameters:
    """Risk management parameters."""
    # Risk per trade
    risk_per_trade: float = 0.005  # 0.5% of equity per trade
    max_risk_per_trade: float = 0.01  # 1% maximum risk per trade

    # Loss limits
    max_daily_loss: float = 0.03  # 3% max daily loss
    max_weekly_loss: float = 0.07  # 7% max weekly loss
    max_drawdown: float = 0.15  # 15% max drawdown from peak

    # Position limits
    max_open_positions: int = 5
    max_portfolio_exposure: float = 0.50  # 50% max portfolio exposure
    max_symbol_exposure: float = 0.25  # 25% max single symbol exposure

    # Leverage
    max_leverage: float = 3.0

    # Consecutive losses
    max_consecutive_losses: int = 5

    # Cooldown after max consecutive losses (minutes)
    cooldown_minutes: int = 60


@dataclass
class RiskCheckResult:
    """Result of a risk check."""
    status: RiskStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_approved(self) -> bool:
        """Check if the risk check passed."""
        return self.status == RiskStatus.APPROVED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class TradeRisk:
    """Risk assessment for a specific trade."""
    symbol: str
    action: str
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    risk_amount: float
    risk_percentage: float
    potential_loss: float
    potential_profit: float
    risk_reward_ratio: float
    leverage: float = 1.0


class RiskEngine:
    """
    Comprehensive risk management engine.

    Validates all trades against risk parameters and tracks
    portfolio-level risk metrics.
    """

    def __init__(self, params: Optional[RiskParameters] = None):
        self.params = params or RiskParameters()

        # State tracking
        self._equity: float = 0.0
        self._peak_equity: float = 0.0
        self._current_drawdown: float = 0.0
        self._daily_pnl: float = 0.0
        self._weekly_pnl: float = 0.0
        self._daily_start_equity: float = 0.0
        self._weekly_start_equity: float = 0.0
        self._consecutive_losses: int = 0
        self._last_trade_result: Optional[str] = None
        self._cooldown_until: Optional[datetime] = None

        # Tracking
        self._open_positions: Dict[str, Dict[str, Any]] = {}
        self._trade_history: List[Dict[str, Any]] = []
        self._last_reset_date: datetime = datetime.now(timezone.utc).date()
        self._last_reset_week: int = datetime.now(timezone.utc).isocalendar()[1]

    @property
    def equity(self) -> float:
        """Current account equity."""
        return self._equity

    @equity.setter
    def equity(self, value: float) -> None:
        """Update equity and track peak/drawdown."""
        self._equity = value
        if value > self._peak_equity:
            self._peak_equity = value
        if self._peak_equity > 0:
            self._current_drawdown = (self._peak_equity - value) / self._peak_equity

    @property
    def current_drawdown(self) -> float:
        """Current drawdown from peak."""
        return self._current_drawdown

    @property
    def consecutive_losses(self) -> int:
        """Number of consecutive losses."""
        return self._consecutive_losses

    @property
    def is_in_cooldown(self) -> bool:
        """Check if trading is in cooldown period."""
        if self._cooldown_until is None:
            return False
        return datetime.now(timezone.utc) < self._cooldown_until

    def validate_trade(
        self,
        symbol: str,
        action: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        current_equity: Optional[float] = None,
    ) -> RiskCheckResult:
        """
        Validate a trade against all risk parameters.

        Args:
            symbol: Trading symbol
            action: BUY or SELL
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            position_size: Position size in base asset
            current_equity: Current equity (uses internal if None)

        Returns:
            RiskCheckResult with approval status and details
        """
        if current_equity is not None:
            self.equity = current_equity

        details: Dict[str, Any] = {}

        # Check cooldown
        if self.is_in_cooldown:
            remaining = (self._cooldown_until - datetime.now(timezone.utc)).total_seconds() / 60
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Trading in cooldown for {remaining:.1f} more minutes",
                details={"cooldown_remaining_minutes": remaining},
            )

        # Check consecutive losses
        if self._consecutive_losses >= self.params.max_consecutive_losses:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Max consecutive losses reached ({self._consecutive_losses})",
                details={"consecutive_losses": self._consecutive_losses},
            )

        # Check drawdown
        if self._current_drawdown >= self.params.max_drawdown:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Max drawdown exceeded ({self._current_drawdown:.2%})",
                details={"current_drawdown": self._current_drawdown},
            )

        # Check daily loss
        if self._daily_start_equity > 0:
            daily_loss = (self._daily_start_equity - self._equity) / self._daily_start_equity
            if daily_loss >= self.params.max_daily_loss:
                return RiskCheckResult(
                    status=RiskStatus.REJECTED,
                    message=f"Daily loss limit reached ({daily_loss:.2%})",
                    details={"daily_loss": daily_loss},
                )

        # Check weekly loss
        if self._weekly_start_equity > 0:
            weekly_loss = (self._weekly_start_equity - self._equity) / self._weekly_start_equity
            if weekly_loss >= self.params.max_weekly_loss:
                return RiskCheckResult(
                    status=RiskStatus.REJECTED,
                    message=f"Weekly loss limit reached ({weekly_loss:.2%})",
                    details={"weekly_loss": weekly_loss},
                )

        # Check open positions
        if len(self._open_positions) >= self.params.max_open_positions:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Max open positions reached ({len(self._open_positions)})",
                details={"open_positions": len(self._open_positions)},
            )

        # Calculate risk
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit == 0:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message="Stop loss cannot equal entry price",
            )

        risk_amount = position_size * risk_per_unit
        risk_percentage = risk_amount / self._equity if self._equity > 0 else 1.0

        # Check risk per trade
        if risk_percentage > self.params.max_risk_per_trade:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Risk per trade too high ({risk_percentage:.2%} > {self.params.max_risk_per_trade:.2%})",
                details={"risk_percentage": risk_percentage},
            )

        # Check symbol exposure
        symbol_exposure = self._calculate_symbol_exposure(symbol)
        new_exposure = (position_size * entry_price) / self._equity if self._equity > 0 else 0
        if symbol_exposure + new_exposure > self.params.max_symbol_exposure:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Symbol exposure would exceed limit ({self.params.max_symbol_exposure:.2%})",
                details={"current_symbol_exposure": symbol_exposure, "new_exposure": new_exposure},
            )

        # Check portfolio exposure
        total_exposure = self._calculate_total_exposure()
        if total_exposure + new_exposure > self.params.max_portfolio_exposure:
            return RiskCheckResult(
                status=RiskStatus.REJECTED,
                message=f"Portfolio exposure would exceed limit ({self.params.max_portfolio_exposure:.2%})",
                details={"current_exposure": total_exposure, "new_exposure": new_exposure},
            )

        # Calculate risk/reward
        potential_profit = abs(take_profit - entry_price) * position_size
        potential_loss = risk_amount
        risk_reward = potential_profit / potential_loss if potential_loss > 0 else 0

        details = {
            "risk_amount": risk_amount,
            "risk_percentage": risk_percentage,
            "potential_loss": potential_loss,
            "potential_profit": potential_profit,
            "risk_reward_ratio": risk_reward,
            "position_size": position_size,
        }

        return RiskCheckResult(
            status=RiskStatus.APPROVED,
            message="Trade approved",
            details=details,
        )

    def calculate_position_size(
        self,
        equity: float,
        entry_price: float,
        stop_loss: float,
        risk_percentage: Optional[float] = None,
    ) -> TradeRisk:
        """
        Calculate position size based on risk parameters.

        Risk Amount = Equity * Risk%
        Position Size = Risk Amount / Stop-Loss Distance

        Args:
            equity: Current equity
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_percentage: Risk percentage (uses default if None)

        Returns:
            TradeRisk with position sizing details
        """
        risk_pct = risk_percentage or self.params.risk_per_trade

        # Calculate risk amount
        risk_amount = equity * risk_pct

        # Calculate stop-loss distance
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance == 0:
            raise ValueError("Stop loss cannot equal entry price")

        # Calculate position size
        position_size = risk_amount / stop_distance

        # Calculate potential profit/loss
        potential_loss = position_size * stop_distance

        return TradeRisk(
            symbol="",
            action="",
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=0.0,
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=risk_pct,
            potential_loss=potential_loss,
            potential_profit=0.0,
            risk_reward_ratio=0.0,
        )

    def update_after_trade(
        self,
        symbol: str,
        action: str,
        entry_price: float,
        exit_price: float,
        position_size: float,
        pnl: float,
    ) -> None:
        """Update risk state after a trade is closed."""
        # Update P&L tracking
        self._daily_pnl += pnl
        self._weekly_pnl += pnl
        self.equity += pnl

        # Update consecutive losses
        if pnl < 0:
            self._consecutive_losses += 1
            self._last_trade_result = "loss"
        else:
            self._consecutive_losses = 0
            self._last_trade_result = "win"

        # Check if cooldown needed
        if self._consecutive_losses >= self.params.max_consecutive_losses:
            self._cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=self.params.cooldown_minutes)
            logger.warning(f"Cooldown activated for {self.params.cooldown_minutes} minutes")

        # Record trade
        self._trade_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "action": action,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "position_size": position_size,
            "pnl": pnl,
        })

        # Remove from open positions
        if symbol in self._open_positions:
            del self._open_positions[symbol]

    def open_position(self, symbol: str, details: Dict[str, Any]) -> None:
        """Record an open position."""
        self._open_positions[symbol] = details

    def close_position(self, symbol: str) -> None:
        """Remove a position from tracking."""
        if symbol in self._open_positions:
            del self._open_positions[symbol]

    def reset_daily(self) -> None:
        """Reset daily tracking."""
        self._daily_pnl = 0.0
        self._daily_start_equity = self._equity
        self._last_reset_date = datetime.now(timezone.utc).date()

    def reset_weekly(self) -> None:
        """Reset weekly tracking."""
        self._weekly_pnl = 0.0
        self._weekly_start_equity = self._equity
        self._last_reset_week = datetime.now(timezone.utc).isocalendar()[1]

    def _calculate_symbol_exposure(self, symbol: str) -> float:
        """Calculate current exposure for a symbol."""
        if symbol not in self._open_positions:
            return 0.0
        position = self._open_positions[symbol]
        return (position.get("size", 0) * position.get("price", 0)) / self._equity if self._equity > 0 else 0

    def _calculate_total_exposure(self) -> float:
        """Calculate total portfolio exposure."""
        total = 0.0
        for symbol in self._open_positions:
            total += self._calculate_symbol_exposure(symbol)
        return total

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get a summary of current risk state."""
        return {
            "equity": self._equity,
            "peak_equity": self._peak_equity,
            "current_drawdown": self._current_drawdown,
            "daily_pnl": self._daily_pnl,
            "weekly_pnl": self._weekly_pnl,
            "consecutive_losses": self._consecutive_losses,
            "open_positions": len(self._open_positions),
            "is_in_cooldown": self.is_in_cooldown,
            "cooldown_until": self._cooldown_until.isoformat() if self._cooldown_until else None,
            "total_exposure": self._calculate_total_exposure(),
        }

    def reset(self) -> None:
        """Reset all risk state."""
        self._equity = 0.0
        self._peak_equity = 0.0
        self._current_drawdown = 0.0
        self._daily_pnl = 0.0
        self._weekly_pnl = 0.0
        self._daily_start_equity = 0.0
        self._weekly_start_equity = 0.0
        self._consecutive_losses = 0
        self._last_trade_result = None
        self._cooldown_until = None
        self._open_positions.clear()
        self._trade_history.clear()
