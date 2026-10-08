"""
Portfolio Manager
=================

Provides comprehensive portfolio tracking and analytics:
- Total equity and available balance
- Open exposure tracking
- Realized and unrealized P&L
- Leverage monitoring
- Drawdown calculation
- Daily/Weekly/Monthly P&L tracking
- Asset correlation analysis
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PortfolioSnapshot:
    """Snapshot of portfolio state at a point in time."""
    timestamp: datetime
    total_equity: float
    available_balance: float
    open_exposure: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    leverage: float
    drawdown: float
    open_positions: int
    margin_used: float
    margin_level: Optional[float] = None


@dataclass
class AssetPosition:
    """Position in a single asset."""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    weight: float  # Percentage of portfolio


@dataclass
class CorrelationMatrix:
    """Asset correlation analysis."""
    symbols: List[str]
    matrix: pd.DataFrame
    average_correlation: float
    max_correlation: float
    min_correlation: float
    diversification_score: float  # 0-1, higher is more diversified


class PortfolioManager:
    """
    Comprehensive portfolio tracking and analytics.

    Tracks all positions, P&L, exposure, and risk metrics
    across the entire portfolio.
    """

    def __init__(self, starting_balance: float = 10000.0):
        self.starting_balance = starting_balance

        # Current state
        self._total_equity: float = starting_balance
        self._available_balance: float = starting_balance
        self._open_exposure: float = 0.0
        self._unrealized_pnl: float = 0.0
        self._realized_pnl: float = 0.0
        self._margin_used: float = 0.0
        self._peak_equity: float = starting_balance
        self._current_drawdown: float = 0.0

        # Positions
        self._positions: Dict[str, AssetPosition] = {}
        self._position_history: List[Dict[str, Any]] = []

        # P&L tracking
        self._daily_pnl: float = 0.0
        self._weekly_pnl: float = 0.0
        self._monthly_pnl: float = 0.0
        self._daily_start_equity: float = starting_balance
        self._weekly_start_equity: float = starting_balance
        self._monthly_start_equity: float = starting_balance

        # History
        self._equity_history: List[PortfolioSnapshot] = []
        self._pnl_history: List[Dict[str, Any]] = []

        # Price history for correlation
        self._price_history: Dict[str, List[float]] = {}

        logger.info(f"PortfolioManager initialized with ${starting_balance:,.2f}")

    @property
    def total_equity(self) -> float:
        """Total portfolio equity."""
        return self._total_equity

    @property
    def available_balance(self) -> float:
        """Available balance for new positions."""
        return self._available_balance

    @property
    def open_exposure(self) -> float:
        """Total open exposure."""
        return self._open_exposure

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
        """Total P&L (realized + unrealized)."""
        return self._realized_pnl + self._unrealized_pnl

    @property
    def leverage(self) -> float:
        """Current portfolio leverage."""
        if self._total_equity > 0:
            return self._open_exposure / self._total_equity
        return 0.0

    @property
    def drawdown(self) -> float:
        """Current drawdown from peak."""
        return self._current_drawdown

    @property
    def margin_level(self) -> Optional[float]:
        """Current margin level."""
        if self._margin_used > 0:
            return self._total_equity / self._margin_used
        return None

    @property
    def positions(self) -> Dict[str, AssetPosition]:
        """Current positions."""
        return self._positions.copy()

    def update_equity(self, new_equity: float) -> None:
        """Update total equity and track drawdown."""
        self._total_equity = new_equity
        if new_equity > self._peak_equity:
            self._peak_equity = new_equity
        if self._peak_equity > 0:
            self._current_drawdown = (self._peak_equity - new_equity) / self._peak_equity

    def update_position(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        current_price: float,
    ) -> None:
        """Update or add a position."""
        unrealized_pnl = (current_price - entry_price) * quantity

        self._positions[symbol] = AssetPosition(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            current_price=current_price,
            unrealized_pnl=unrealized_pnl,
            weight=0.0,  # Will be recalculated
        )

        self._recalculate_weights()
        self._update_totals()

    def close_position(self, symbol: str, exit_price: float) -> float:
        """Close a position and return realized P&L."""
        if symbol not in self._positions:
            return 0.0

        position = self._positions[symbol]
        realized_pnl = (exit_price - position.entry_price) * position.quantity

        self._realized_pnl += realized_pnl
        self._daily_pnl += realized_pnl
        self._weekly_pnl += realized_pnl
        self._monthly_pnl += realized_pnl

        # Record in history
        self._position_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "realized_pnl": realized_pnl,
        })

        del self._positions[symbol]
        self._recalculate_weights()
        self._update_totals()

        return realized_pnl

    def update_market_prices(self, prices: Dict[str, float]) -> None:
        """Update market prices for all positions."""
        for symbol, price in prices.items():
            if symbol in self._positions:
                position = self._positions[symbol]
                position.current_price = price
                position.unrealized_pnl = (price - position.entry_price) * position.quantity

            # Update price history for correlation
            if symbol not in self._price_history:
                self._price_history[symbol] = []
            self._price_history[symbol].append(price)
            if len(self._price_history[symbol]) > 1000:
                self._price_history[symbol] = self._price_history[symbol][-1000:]

        self._recalculate_weights()
        self._update_totals()

    def _recalculate_weights(self) -> None:
        """Recalculate position weights."""
        total_value = sum(
            abs(p.quantity * p.current_price) for p in self._positions.values()
        )
        if total_value > 0:
            for position in self._positions.values():
                position.weight = (position.quantity * position.current_price) / total_value

    def _update_totals(self) -> None:
        """Update total exposure and unrealized P&L."""
        self._open_exposure = sum(
            abs(p.quantity * p.current_price) for p in self._positions.values()
        )
        self._unrealized_pnl = sum(p.unrealized_pnl for p in self._positions.values())
        self._total_equity = self._available_balance + self._unrealized_pnl

    def get_correlation_matrix(self, lookback: int = 100) -> Optional[CorrelationMatrix]:
        """
        Calculate asset correlation matrix.

        Args:
            lookback: Number of periods for correlation calculation

        Returns:
            CorrelationMatrix or None if insufficient data
        """
        if len(self._positions) < 2:
            return None

        # Build price DataFrame
        price_data = {}
        for symbol in self._positions.keys():
            if symbol in self._price_history and len(self._price_history[symbol]) >= lookback:
                price_data[symbol] = self._price_history[symbol][-lookback:]

        if len(price_data) < 2:
            return None

        df = pd.DataFrame(price_data)
        returns = df.pct_change().dropna()

        if returns.empty:
            return None

        corr_matrix = returns.corr()

        # Calculate average correlation (excluding diagonal)
        symbols = list(corr_matrix.columns)
        n = len(symbols)
        if n < 2:
            return None

        correlations = []
        for i in range(n):
            for j in range(i + 1, n):
                correlations.append(corr_matrix.iloc[i, j])

        avg_corr = np.mean(correlations) if correlations else 0.0
        max_corr = np.max(correlations) if correlations else 0.0
        min_corr = np.min(correlations) if correlations else 0.0

        # Diversification score: 1 - average correlation
        diversification = 1 - abs(avg_corr)

        return CorrelationMatrix(
            symbols=symbols,
            matrix=corr_matrix,
            average_correlation=avg_corr,
            max_correlation=max_corr,
            min_correlation=min_corr,
            diversification_score=diversification,
        )

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary."""
        return {
            "total_equity": self._total_equity,
            "available_balance": self._available_balance,
            "open_exposure": self._open_exposure,
            "unrealized_pnl": self._unrealized_pnl,
            "realized_pnl": self._realized_pnl,
            "total_pnl": self.total_pnl,
            "return_pct": (self.total_pnl / self.starting_balance) * 100,
            "leverage": self.leverage,
            "drawdown": self._current_drawdown,
            "open_positions": len(self._positions),
            "margin_used": self._margin_used,
            "margin_level": self.margin_level,
            "daily_pnl": self._daily_pnl,
            "weekly_pnl": self._weekly_pnl,
            "monthly_pnl": self._monthly_pnl,
        }

    def get_position_breakdown(self) -> pd.DataFrame:
        """Get position breakdown as DataFrame."""
        if not self._positions:
            return pd.DataFrame()

        data = []
        for symbol, pos in self._positions.items():
            data.append({
                "symbol": symbol,
                "quantity": pos.quantity,
                "entry_price": pos.entry_price,
                "current_price": pos.current_price,
                "unrealized_pnl": pos.unrealized_pnl,
                "weight": pos.weight * 100,
                "notional": pos.quantity * pos.current_price,
            })

        return pd.DataFrame(data)

    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        if not self._equity_history:
            return pd.DataFrame()

        return pd.DataFrame([{
            "timestamp": s.timestamp,
            "total_equity": s.total_equity,
            "available_balance": s.available_balance,
            "open_exposure": s.open_exposure,
            "unrealized_pnl": s.unrealized_pnl,
            "realized_pnl": s.realized_pnl,
            "total_pnl": s.total_pnl,
            "leverage": s.leverage,
            "drawdown": s.drawdown,
            "open_positions": s.open_positions,
        } for s in self._equity_history])

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self._equity_history:
            return {}

        equity_df = self.get_equity_curve()
        returns = equity_df["total_equity"].pct_change().dropna()

        if returns.empty:
            return {}

        # Calculate metrics
        total_return = (self._total_equity - self.starting_balance) / self.starting_balance
        volatility = returns.std() * np.sqrt(365 * 24)  # Annualized (hourly data)
        sharpe_ratio = (returns.mean() * 365 * 24) / volatility if volatility > 0 else 0

        # Max drawdown
        cummax = equity_df["total_equity"].cummax()
        drawdown = (equity_df["total_equity"] - cummax) / cummax
        max_drawdown = drawdown.min()

        # Win rate from position history
        if self._position_history:
            pnls = [p["realized_pnl"] for p in self._position_history]
            wins = sum(1 for p in pnls if p > 0)
            win_rate = wins / len(pnls) * 100
        else:
            win_rate = 0.0

        return {
            "total_return": total_return * 100,
            "annualized_volatility": volatility * 100,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown * 100,
            "win_rate": win_rate,
            "total_trades": len(self._position_history),
            "profit_factor": self._calculate_profit_factor(),
        }

    def _calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        if not self._position_history:
            return 0.0

        pnls = [p["realized_pnl"] for p in self._position_history]
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def reset_daily(self) -> None:
        """Reset daily P&L tracking."""
        self._daily_pnl = 0.0
        self._daily_start_equity = self._total_equity

    def reset_weekly(self) -> None:
        """Reset weekly P&L tracking."""
        self._weekly_pnl = 0.0
        self._weekly_start_equity = self._total_equity

    def reset_monthly(self) -> None:
        """Reset monthly P&L tracking."""
        self._monthly_pnl = 0.0
        self._monthly_start_equity = self._total_equity

    def record_snapshot(self) -> None:
        """Record a portfolio snapshot."""
        self._equity_history.append(PortfolioSnapshot(
            timestamp=datetime.now(timezone.utc),
            total_equity=self._total_equity,
            available_balance=self._available_balance,
            open_exposure=self._open_exposure,
            unrealized_pnl=self._unrealized_pnl,
            realized_pnl=self._realized_pnl,
            total_pnl=self.total_pnl,
            leverage=self.leverage,
            drawdown=self._current_drawdown,
            open_positions=len(self._positions),
            margin_used=self._margin_used,
            margin_level=self.margin_level,
        ))

    def reset(self) -> None:
        """Reset portfolio to initial state."""
        self._total_equity = self.starting_balance
        self._available_balance = self.starting_balance
        self._open_exposure = 0.0
        self._unrealized_pnl = 0.0
        self._realized_pnl = 0.0
        self._margin_used = 0.0
        self._peak_equity = self.starting_balance
        self._current_drawdown = 0.0
        self._positions.clear()
        self._position_history.clear()
        self._daily_pnl = 0.0
        self._weekly_pnl = 0.0
        self._monthly_pnl = 0.0
        self._daily_start_equity = self.starting_balance
        self._weekly_start_equity = self.starting_balance
        self._monthly_start_equity = self.starting_balance
        self._equity_history.clear()
        self._pnl_history.clear()
        self._price_history.clear()
        logger.info("PortfolioManager reset to initial state")
