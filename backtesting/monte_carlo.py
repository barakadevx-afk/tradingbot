"""
BARAKA AI - Monte Carlo Analysis
=================================

Monte Carlo simulation for backtest robustness assessment.
Performs randomized trade-order simulations, expected drawdown analysis,
probability of severe drawdown, equity distribution, and risk-of-ruin
approximation.

 DISCLAIMER: Monte Carlo analysis is a statistical tool, not a guarantee
of future performance. Past performance does not guarantee future results.
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo analysis."""

    n_simulations: int = 1000
    confidence_level: float = 0.95
    random_seed: Optional[int] = 42
    ruin_threshold: float = 0.5  # 50% drawdown = ruin
    severe_drawdown_threshold: float = 0.30  # 30% drawdown
    bootstrap_method: str = "trade"  # "trade", "return", "block"
    block_size: int = 20  # For block bootstrap


@dataclass
class MonteCarloResult:
    """Container for Monte Carlo analysis results."""

    # Simulation results
    simulated_equity_curves: np.ndarray  # Shape: (n_simulations, n_periods)
    final_equities: np.ndarray
    max_drawdowns: np.ndarray
    total_returns: np.ndarray

    # Statistics
    expected_return: float
    expected_drawdown: float
    probability_of_ruin: float
    probability_of_severe_drawdown: float
    value_at_risk: dict  # VaR at different confidence levels
    expected_shortfall: dict  # CVaR at different confidence levels

    # Distribution percentiles
    return_percentiles: dict
    drawdown_percentiles: dict

    # Original backtest reference
    original_return: float
    original_max_drawdown: float

    config: MonteCarloConfig

    def summary(self) -> str:
        """Print a formatted summary."""
        lines = [
            "=" * 70,
            "BARAKA AI - Monte Carlo Analysis Results",
            "=" * 70,
            f"  Simulations:            {self.config.n_simulations}",
            f"  Confidence Level:       {self.config.confidence_level:.0%}",
            "",
            "  Original Backtest:",
            f"    Total Return:         {self.original_return:>12.2%}",
            f"    Max Drawdown:         {self.original_max_drawdown:>12.2%}",
            "",
            "  Monte Carlo Estimates:",
            f"    Expected Return:      {self.expected_return:>12.2%}",
            f"    Expected Drawdown:    {self.expected_drawdown:>12.2%}",
            f"    P(Ruin):              {self.probability_of_ruin:>12.2%}",
            f"    P(Severe DD):         {self.probability_of_severe_drawdown:>12.2%}",
            "",
            "  Value at Risk (VaR):",
        ]
        for level, var in self.value_at_risk.items():
            lines.append(f"    VaR {level}: {var:>12.2%}")

        lines.extend([
            "",
            "  Expected Shortfall (CVaR):",
        ])
        for level, es in self.expected_shortfall.items():
            lines.append(f"    ES {level}: {es:>12.2%}")

        lines.extend([
            "",
            "  Return Percentiles:",
        ])
        for p, val in self.return_percentiles.items():
            lines.append(f"    {p}: {val:>12.2%}")

        lines.extend([
            "",
            "  Drawdown Percentiles:",
        ])
        for p, val in self.drawdown_percentiles.items():
            lines.append(f"    {p}: {val:>12.2%}")

        lines.extend([
            "",
            "-" * 70,
            "  DISCLAIMER: Monte Carlo analysis is a statistical tool, not a",
            "  guarantee of future performance. Past performance does not",
            "  guarantee future results.",
            "=" * 70,
        ])
        return "\n".join(lines)


class MonteCarloAnalyzer:
    """
    Monte Carlo simulation analyzer for backtesting.

    Runs randomized simulations to assess strategy robustness,
    estimate expected drawdowns, and calculate risk-of-ruin.
    """

    def __init__(self, config: Optional[MonteCarloConfig] = None):
        self.config = config or MonteCarloConfig()
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

    def run(
        self,
        trades: pd.DataFrame,
        equity_curve: pd.Series,
        starting_balance: float = 100_000.0,
    ) -> MonteCarloResult:
        """
        Run Monte Carlo analysis on backtest results.

        Parameters
        ----------
        trades : pd.DataFrame
            Completed trades from backtest.
        equity_curve : pd.Series
            Original equity curve.
        starting_balance : float
            Starting balance for simulations.

        Returns
        -------
        MonteCarloResult
            Complete Monte Carlo analysis results.
        """
        if len(trades) == 0:
            raise ValueError("No trades available for Monte Carlo analysis")

        logger.info(
            "Running %d Monte Carlo simulations...", self.config.n_simulations
        )

        # Extract trade returns
        trade_returns = self._extract_trade_returns(trades)
        n_trades = len(trade_returns)

        if n_trades < 10:
            warnings.warn(
                f"Only {n_trades} trades available. "
                "Monte Carlo results may be unreliable with few trades.",
                UserWarning,
            )

        # Run simulations
        simulated_curves = np.zeros((self.config.n_simulations, n_trades + 1))
        simulated_curves[:, 0] = starting_balance

        max_drawdowns = np.zeros(self.config.n_simulations)
        final_equities = np.zeros(self.config.n_simulations)
        total_returns = np.zeros(self.config.n_simulations)

        for sim in range(self.config.n_simulations):
            # Randomize trade order
            if self.config.bootstrap_method == "trade":
                sampled_returns = self._bootstrap_trade_returns(trade_returns)
            elif self.config.bootstrap_method == "return":
                sampled_returns = self._bootstrap_period_returns(equity_curve, n_trades)
            elif self.config.bootstrap_method == "block":
                sampled_returns = self._block_bootstrap_returns(trade_returns)
            else:
                sampled_returns = self._bootstrap_trade_returns(trade_returns)

            # Simulate equity curve
            curve = np.zeros(n_trades + 1)
            curve[0] = starting_balance
            for t in range(n_trades):
                curve[t + 1] = curve[t] * (1 + sampled_returns[t])

            simulated_curves[sim] = curve
            final_equities[sim] = curve[-1]
            total_returns[sim] = curve[-1] / curve[0] - 1.0

            # Calculate max drawdown for this simulation
            running_max = np.maximum.accumulate(curve)
            drawdowns = (curve - running_max) / running_max
            max_drawdowns[sim] = drawdowns.min()

        # Calculate statistics
        expected_return = float(np.mean(total_returns))
        expected_drawdown = float(np.mean(max_drawdowns))

        # Probability of ruin and severe drawdown
        ruin_count = np.sum(max_drawdowns <= -self.config.ruin_threshold)
        severe_dd_count = np.sum(max_drawdowns <= -self.config.severe_drawdown_threshold)

        prob_ruin = float(ruin_count / self.config.n_simulations)
        prob_severe_dd = float(severe_dd_count / self.config.n_simulations)

        # VaR and ES
        var_levels = [0.90, 0.95, 0.99]
        value_at_risk = {}
        expected_shortfall = {}

        for level in var_levels:
            alpha = 1 - level
            var_threshold = np.percentile(total_returns, alpha * 100)
            value_at_risk[f"{level:.0%}"] = float(var_threshold)

            # Expected shortfall (CVaR)
            tail_returns = total_returns[total_returns <= var_threshold]
            if len(tail_returns) > 0:
                expected_shortfall[f"{level:.0%}"] = float(np.mean(tail_returns))
            else:
                expected_shortfall[f"{level:.0%}"] = float(var_threshold)

        # Percentiles
        return_percentiles = {
            "1%": float(np.percentile(total_returns, 1)),
            "5%": float(np.percentile(total_returns, 5)),
            "10%": float(np.percentile(total_returns, 10)),
            "25%": float(np.percentile(total_returns, 25)),
            "50%": float(np.percentile(total_returns, 50)),
            "75%": float(np.percentile(total_returns, 75)),
            "90%": float(np.percentile(total_returns, 90)),
            "95%": float(np.percentile(total_returns, 95)),
            "99%": float(np.percentile(total_returns, 99)),
        }

        drawdown_percentiles = {
            "1%": float(np.percentile(max_drawdowns, 1)),
            "5%": float(np.percentile(max_drawdowns, 5)),
            "10%": float(np.percentile(max_drawdowns, 10)),
            "25%": float(np.percentile(max_drawdowns, 25)),
            "50%": float(np.percentile(max_drawdowns, 50)),
            "75%": float(np.percentile(max_drawdowns, 75)),
            "90%": float(np.percentile(max_drawdowns, 90)),
            "95%": float(np.percentile(max_drawdowns, 95)),
            "99%": float(np.percentile(max_drawdowns, 99)),
        }

        # Original backtest reference
        original_return = float(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0)
        running_max = equity_curve.cummax()
        original_dd = float(((equity_curve - running_max) / running_max).min())

        result = MonteCarloResult(
            simulated_equity_curves=simulated_curves,
            final_equities=final_equities,
            max_drawdowns=max_drawdowns,
            total_returns=total_returns,
            expected_return=expected_return,
            expected_drawdown=expected_drawdown,
            probability_of_ruin=prob_ruin,
            probability_of_severe_drawdown=prob_severe_dd,
            value_at_risk=value_at_risk,
            expected_shortfall=expected_shortfall,
            return_percentiles=return_percentiles,
            drawdown_percentiles=drawdown_percentiles,
            original_return=original_return,
            original_max_drawdown=original_dd,
            config=self.config,
        )

        logger.info(
            "Monte Carlo complete. Expected Return: %.2f%%, P(Ruin): %.2f%%",
            expected_return * 100,
            prob_ruin * 100,
        )
        return result

    def _extract_trade_returns(self, trades: pd.DataFrame) -> np.ndarray:
        """Extract trade returns as numpy array."""
        if "return_pct" in trades.columns:
            return trades["return_pct"].values
        elif "pnl" in trades.columns:
            # Calculate return percentage from PnL
            if "entry_price" in trades.columns and "quantity" in trades.columns:
                notional = trades["entry_price"] * trades["quantity"]
                return (trades["pnl"] / notional).values
            else:
                return trades["pnl"].values
        else:
            raise ValueError("Trades must have 'return_pct' or 'pnl' column")

    def _bootstrap_trade_returns(self, trade_returns: np.ndarray) -> np.ndarray:
        """Simple bootstrap: sample trade returns with replacement."""
        n = len(trade_returns)
        indices = np.random.choice(n, size=n, replace=True)
        return trade_returns[indices]

    def _bootstrap_period_returns(
        self, equity_curve: pd.Series, n_samples: int
    ) -> np.ndarray:
        """Bootstrap from period returns instead of trade returns."""
        period_returns = equity_curve.pct_change().dropna().values
        indices = np.random.choice(
            len(period_returns), size=n_samples, replace=True
        )
        return period_returns[indices]

    def _block_bootstrap_returns(self, trade_returns: np.ndarray) -> np.ndarray:
        """Block bootstrap to preserve serial correlation."""
        n = len(trade_returns)
        block_size = min(self.config.block_size, n)
        n_blocks = int(np.ceil(n / block_size))

        blocks = []
        for _ in range(n_blocks):
            start = np.random.randint(0, n - block_size + 1)
            blocks.append(trade_returns[start : start + block_size])

        sampled = np.concatenate(blocks)[:n]
        return sampled

    def calculate_risk_of_ruin(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        risk_per_trade: float = 0.01,
    ) -> float:
        """
        Approximate risk of ruin using the classic formula.

        Risk of Ruin = ((1 - (W - L)) / (1 + (W - L))) ^ (C / R)

        Where:
        - W = win rate
        - L = loss rate
        - C = number of trades
        - R = risk per trade as fraction of capital

        Parameters
        ----------
        win_rate : float
            Probability of winning (0-1).
        avg_win : float
            Average winning trade amount.
        avg_loss : float
            Average losing trade amount (positive value).
        risk_per_trade : float
            Risk per trade as fraction of capital.

        Returns
        -------
        float
            Probability of ruin (0-1).
        """
        if avg_loss == 0:
            return 0.0

        # Edge calculation
        edge = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        if edge <= 0:
            return 1.0  # Guaranteed ruin with no edge

        # Win/loss ratio
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.0

        # Number of trades to simulate
        n_trades = 1000

        # Risk of ruin approximation
        if win_loss_ratio == 1.0:
            # Even odds
            ruin_prob = ((1 - edge) / (1 + edge)) ** (n_trades * risk_per_trade)
        else:
            a = (1 - win_rate) / win_rate
            ruin_prob = ((1 - (win_rate * (1 + win_loss_ratio) - 1)) /
                        (1 + (win_rate * (1 + win_loss_ratio) - 1))) ** (n_trades * risk_per_trade)

        return float(np.clip(ruin_prob, 0.0, 1.0))

    def generate_distribution_plot_data(
        self, result: MonteCarloResult
    ) -> pd.DataFrame:
        """Generate data for distribution plotting."""
        percentiles = np.arange(0, 101, 1)

        return_dist = {
            "percentile": percentiles,
            "return": np.percentile(result.total_returns, percentiles),
        }

        dd_dist = {
            "percentile": percentiles,
            "drawdown": np.percentile(result.max_drawdowns, percentiles),
        }

        return pd.DataFrame(return_dist), pd.DataFrame(dd_dist)
