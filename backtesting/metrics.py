"""
BARAKA AI - Performance Metrics
================================

Comprehensive performance metrics for backtest results.
All calculations use numpy/pandas for vectorized operations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """
    Calculate and store all performance metrics for a backtest.

    Parameters
    ----------
    equity_curve : pd.Series
        Time series of portfolio equity values.
    trades : pd.DataFrame
        DataFrame of completed trades with columns:
        [entry_time, exit_time, side, entry_price, exit_price, quantity, pnl, return_pct]
    risk_free_rate : float
        Annualized risk-free rate (default: 0.0 for crypto).
    periods_per_year : int
        Number of periods per year for annualization.
        365*24 for 1h crypto, 252 for daily stocks, etc.
    """

    equity_curve: pd.Series
    trades: pd.DataFrame
    risk_free_rate: float = 0.0
    periods_per_year: int = 365 * 24  # Default: hourly crypto

    # Stored results
    _results: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._validate_inputs()
        self._results = self._calculate_all()

    def _validate_inputs(self):
        if not isinstance(self.equity_curve, pd.Series):
            raise TypeError("equity_curve must be a pandas Series")
        if len(self.equity_curve) == 0:
            raise ValueError("equity_curve cannot be empty")
        if not isinstance(self.trades, pd.DataFrame):
            raise TypeError("trades must be a pandas DataFrame")

    def _calculate_all(self) -> dict:
        """Calculate all metrics and return as dictionary."""
        eq = self.equity_curve
        trades = self.trades

        returns = eq.pct_change().dropna()
        total_return = self._total_return(eq)
        net_profit = self._net_profit(eq)
        annualized_return = self._annualized_return(eq)

        # Trade-based metrics
        total_trades = len(trades)
        winning_trades = trades[trades["pnl"] > 0] if total_trades > 0 else pd.DataFrame()
        losing_trades = trades[trades["pnl"] < 0] if total_trades > 0 else pd.DataFrame()

        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
        loss_rate = 1.0 - win_rate if total_trades > 0 else 0.0

        gross_profit = winning_trades["pnl"].sum() if len(winning_trades) > 0 else 0.0
        gross_loss = abs(losing_trades["pnl"].sum()) if len(losing_trades) > 0 else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

        avg_win = winning_trades["pnl"].mean() if len(winning_trades) > 0 else 0.0
        avg_loss = losing_trades["pnl"].mean() if len(losing_trades) > 0 else 0.0
        largest_win = winning_trades["pnl"].max() if len(winning_trades) > 0 else 0.0
        largest_loss = losing_trades["pnl"].min() if len(losing_trades) > 0 else 0.0

        expectancy = self._expectancy(trades)

        # Risk metrics
        sharpe = self._sharpe_ratio(returns)
        sortino = self._sortino_ratio(returns)
        calmar = self._calmar_ratio(eq, annualized_return)
        max_dd, max_dd_duration = self._max_drawdown(eq)

        # Holding time
        avg_holding_time = self._average_holding_time(trades)

        # Long/Short breakdown
        long_trades = len(trades[trades["side"] == "long"]) if total_trades > 0 else 0
        short_trades = len(trades[trades["side"] == "short"]) if total_trades > 0 else 0

        # Additional metrics
        returns_std = returns.std()
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0.0

        # Consecutive wins/losses
        max_consecutive_wins, max_consecutive_losses = self._consecutive_counts(trades)

        # Return distribution
        skewness = returns.skew()
        kurtosis = returns.kurtosis()

        # VaR (95%, 99%)
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0.0
        var_99 = np.percentile(returns, 1) if len(returns) > 0 else 0.0

        return {
            "total_return": total_return,
            "net_profit": net_profit,
            "annualized_return": annualized_return,
            "win_rate": win_rate,
            "loss_rate": loss_rate,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "max_drawdown": max_dd,
            "max_drawdown_duration": max_dd_duration,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "average_holding_time": avg_holding_time,
            "total_trades": total_trades,
            "long_trades": long_trades,
            "short_trades": short_trades,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "returns_std": returns_std,
            "downside_std": downside_std,
            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "var_95": var_95,
            "var_99": var_99,
            "risk_free_rate": self.risk_free_rate,
            "periods_per_year": self.periods_per_year,
        }

    @staticmethod
    def _total_return(equity: pd.Series) -> float:
        """Calculate total return over the entire period."""
        if len(equity) < 2:
            return 0.0
        return float(equity.iloc[-1] / equity.iloc[0] - 1.0)

    @staticmethod
    def _net_profit(equity: pd.Series) -> float:
        """Calculate net profit in absolute terms."""
        return float(equity.iloc[-1] - equity.iloc[0])

    def _annualized_return(self, equity: pd.Series) -> float:
        """Calculate annualized return (CAGR)."""
        if len(equity) < 2:
            return 0.0
        total_return = equity.iloc[-1] / equity.iloc[0]
        n_periods = len(equity) - 1
        years = n_periods / self.periods_per_year
        if years <= 0:
            return 0.0
        return float(total_return ** (1.0 / years) - 1.0)

    @staticmethod
    def _expectancy(trades: pd.DataFrame) -> float:
        """Calculate expectancy (average PnL per trade)."""
        if len(trades) == 0:
            return 0.0
        return float(trades["pnl"].mean())

    def _sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate annualized Sharpe ratio."""
        if len(returns) < 2 or returns.std() == 0:
            return 0.0
        excess_returns = returns - (self.risk_free_rate / self.periods_per_year)
        return float(np.sqrt(self.periods_per_year) * excess_returns.mean() / returns.std())

    def _sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate annualized Sortino ratio."""
        if len(returns) < 2:
            return 0.0
        excess_returns = returns - (self.risk_free_rate / self.periods_per_year)
        downside = returns[returns < 0]
        if len(downside) < 2 or downside.std() == 0:
            return 0.0
        return float(
            np.sqrt(self.periods_per_year) * excess_returns.mean() / downside.std()
        )

    def _calmar_ratio(self, equity: pd.Series, annualized_return: float) -> float:
        """Calculate Calmar ratio (annualized return / max drawdown)."""
        max_dd = self._max_drawdown(equity)[0]
        if max_dd == 0:
            return 0.0
        return float(annualized_return / abs(max_dd))

    @staticmethod
    def _max_drawdown(equity: pd.Series) -> tuple[float, int]:
        """
        Calculate maximum drawdown and its duration.

        Returns
        -------
        tuple of (max_drawdown, max_drawdown_duration)
            max_drawdown is a negative percentage (e.g., -0.25 for -25%).
            max_drawdown_duration is in number of periods.
        """
        if len(equity) < 2:
            return 0.0, 0

        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        max_dd = float(drawdown.min())

        # Find the duration of the max drawdown
        dd_periods = drawdown < 0
        if not dd_periods.any():
            return 0.0, 0

        # Find longest consecutive drawdown streak
        is_in_drawdown = False
        max_duration = 0
        current_duration = 0

        for val in dd_periods:
            if val:
                if not is_in_drawdown:
                    is_in_drawdown = True
                    current_duration = 1
                else:
                    current_duration += 1
            else:
                if is_in_drawdown:
                    max_duration = max(max_duration, current_duration)
                    is_in_drawdown = False
                    current_duration = 0

        if is_in_drawdown:
            max_duration = max(max_duration, current_duration)

        return max_dd, max_duration

    @staticmethod
    def _average_holding_time(trades: pd.DataFrame) -> float:
        """Calculate average holding time in hours."""
        if len(trades) == 0:
            return 0.0
        if "holding_time" in trades.columns:
            return float(trades["holding_time"].mean())
        if "entry_time" in trades.columns and "exit_time" in trades.columns:
            holding = pd.to_datetime(trades["exit_time"]) - pd.to_datetime(
                trades["entry_time"]
            )
            return float(holding.dt.total_seconds().mean() / 3600.0)
        return 0.0

    @staticmethod
    def _consecutive_counts(trades: pd.DataFrame) -> tuple[int, int]:
        """Calculate max consecutive wins and losses."""
        if len(trades) == 0:
            return 0, 0

        wins = (trades["pnl"] > 0).values
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0

        for is_win in wins:
            if is_win:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)

        return max_wins, max_losses

    @property
    def results(self) -> dict:
        """Return all metrics as a dictionary."""
        return self._results.copy()

    def summary(self) -> str:
        """Return a formatted summary string."""
        r = self._results
        lines = [
            "=" * 60,
            "BARAKA AI - Performance Metrics Summary",
            "=" * 60,
            f"  Total Return:          {r['total_return']:>12.2%}",
            f"  Net Profit:            {r['net_profit']:>12.2f}",
            f"  Annualized Return:     {r['annualized_return']:>12.2%}",
            f"  Sharpe Ratio:          {r['sharpe_ratio']:>12.2f}",
            f"  Sortino Ratio:         {r['sortino_ratio']:>12.2f}",
            f"  Calmar Ratio:          {r['calmar_ratio']:>12.2f}",
            "-" * 60,
            f"  Win Rate:              {r['win_rate']:>12.2%}",
            f"  Loss Rate:             {r['loss_rate']:>12.2%}",
            f"  Profit Factor:         {r['profit_factor']:>12.2f}",
            f"  Expectancy:            {r['expectancy']:>12.2f}",
            "-" * 60,
            f"  Max Drawdown:          {r['max_drawdown']:>12.2%}",
            f"  Max DD Duration:       {r['max_drawdown_duration']:>12d} periods",
            f"  Avg Win:               {r['average_win']:>12.2f}",
            f"  Avg Loss:              {r['average_loss']:>12.2f}",
            f"  Largest Win:           {r['largest_win']:>12.2f}",
            f"  Largest Loss:          {r['largest_loss']:>12.2f}",
            "-" * 60,
            f"  Total Trades:          {r['total_trades']:>12d}",
            f"  Long Trades:           {r['long_trades']:>12d}",
            f"  Short Trades:          {r['short_trades']:>12d}",
            f"  Avg Holding Time:      {r['average_holding_time']:>12.2f} hours",
            f"  Max Cons. Wins:        {r['max_consecutive_wins']:>12d}",
            f"  Max Cons. Losses:      {r['max_consecutive_losses']:>12d}",
            "-" * 60,
            f"  VaR (95%):             {r['var_95']:>12.2%}",
            f"  VaR (99%):             {r['var_99']:>12.2%}",
            f"  Skewness:              {r['skewness']:>12.2f}",
            f"  Kurtosis:              {r['kurtosis']:>12.2f}",
            "=" * 60,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Export all metrics as a flat dictionary."""
        return self._results.copy()

    def to_series(self) -> pd.Series:
        """Export all metrics as a pandas Series."""
        return pd.Series(self._results)
