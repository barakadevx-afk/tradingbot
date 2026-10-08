"""
BARAKA AI - Walk-Forward Validation
====================================

Walk-forward validation: Train Window 1 -> Test Window 1,
Train Window 2 -> Test Window 2, etc. Shows performance stability
across different market regimes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from .engine import BacktestEngine, BacktestConfig, BacktestResult
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


@dataclass
class WalkForwardConfig:
    """Configuration for walk-forward validation."""

    # Window settings
    train_window: int = 252  # Training periods (e.g., 252 days for daily)
    test_window: int = 63  # Testing periods (e.g., 63 days ~ 3 months)
    step_size: int = 63  # Step between windows (default: non-overlapping)

    # Validation
    min_train_size: int = 100  # Minimum training data required
    require_positive_sharpe: bool = False  # Only accept windows with positive Sharpe

    # Optimization
    optimize_params: bool = False  # Whether to optimize params on train window
    param_grid: Optional[dict] = None  # Parameter grid for optimization


@dataclass
class WalkForwardResult:
    """Container for walk-forward validation results."""

    fold_results: list[BacktestResult]
    fold_metrics: pd.DataFrame
    aggregate_metrics: dict
    stability_score: float
    config: WalkForwardConfig

    def summary(self) -> str:
        """Print a formatted summary."""
        lines = [
            "=" * 70,
            "BARAKA AI - Walk-Forward Validation Results",
            "=" * 70,
            f"  Number of Folds:      {len(self.fold_results)}",
            f"  Stability Score:      {self.stability_score:.2f}",
            "",
            "  Per-Fold Metrics:",
            "-" * 70,
        ]

        for i, row in self.fold_metrics.iterrows():
            lines.append(
                f"  Fold {i+1}: Return={row['total_return']:.2%}, "
                f"Sharpe={row['sharpe_ratio']:.2f}, "
                f"MaxDD={row['max_drawdown']:.2%}, "
                f"Trades={int(row['total_trades'])}"
            )

        lines.extend([
            "-" * 70,
            "  Aggregate Metrics:",
            "-" * 70,
        ])

        for key, value in self.aggregate_metrics.items():
            if isinstance(value, float):
                lines.append(f"  {key:25s}: {value:>12.4f}")
            else:
                lines.append(f"  {key:25s}: {value:>12}")

        lines.append("=" * 70)
        return "\n".join(lines)


class WalkForwardValidator:
    """
    Walk-forward validation engine.

    Splits data into rolling train/test windows, runs backtests
    on each fold, and evaluates performance stability.
    """

    def __init__(self, config: Optional[WalkForwardConfig] = None):
        self.config = config or WalkForwardConfig()

    def run(
        self,
        data: pd.DataFrame,
        backtest_config: BacktestConfig,
    ) -> WalkForwardResult:
        """
        Run walk-forward validation.

        Parameters
        ----------
        data : pd.DataFrame
            Full historical OHLCV data.
        backtest_config : BacktestConfig
            Base backtest configuration.

        Returns
        -------
        WalkForwardResult
            Complete walk-forward results.
        """
        n = len(data)
        train_size = self.config.train_window
        test_size = self.config.test_window
        step = self.config.step_size

        if n < self.config.min_train_size:
            raise ValueError(
                f"Insufficient data: {n} rows, minimum {self.config.min_train_size} required"
            )

        fold_results = []
        fold_metrics_list = []

        fold_num = 0
        start_idx = 0

        while start_idx + train_size + test_size <= n:
            fold_num += 1
            train_start = start_idx
            train_end = start_idx + train_size
            test_start = train_end
            test_end = min(test_start + test_size, n)

            train_data = data.iloc[train_start:train_end]
            test_data = data.iloc[test_start:test_end]

            logger.info(
                "Fold %d: Train [%s to %s], Test [%s to %s]",
                fold_num,
                train_data.index[0],
                train_data.index[-1],
                test_data.index[0],
                test_data.index[-1],
            )

            # Run backtest on test window
            fold_config = BacktestConfig(
                symbol=backtest_config.symbol,
                timeframe=backtest_config.timeframe,
                starting_balance=backtest_config.starting_balance,
                risk_per_trade=backtest_config.risk_per_trade,
                max_position_pct=backtest_config.max_position_pct,
                allow_short=backtest_config.allow_short,
                maker_fee=backtest_config.maker_fee,
                taker_fee=backtest_config.taker_fee,
                slippage_model=backtest_config.slippage_model,
                slippage_value=backtest_config.slippage_value,
                strategy_name=backtest_config.strategy_name,
                strategy_params=backtest_config.strategy_params,
                ai_model=backtest_config.ai_model,
                ai_confidence_threshold=backtest_config.ai_confidence_threshold,
                risk_free_rate=backtest_config.risk_free_rate,
                periods_per_year=backtest_config.periods_per_year,
            )

            engine = BacktestEngine(fold_config)
            result = engine.run(test_data)

            # Calculate metrics for this fold
            metrics_calc = PerformanceMetrics(
                equity_curve=result.equity_curve,
                trades=result.trades,
                risk_free_rate=backtest_config.risk_free_rate,
                periods_per_year=backtest_config.periods_per_year,
            )

            fold_results.append(result)
            fold_metrics_list.append({
                "fold": fold_num,
                "train_start": train_data.index[0],
                "train_end": train_data.index[-1],
                "test_start": test_data.index[0],
                "test_end": test_data.index[-1],
                **metrics_calc.results,
            })

            start_idx += step

        if not fold_results:
            raise ValueError(
                "No valid folds generated. Reduce train_window or test_window size."
            )

        fold_metrics_df = pd.DataFrame(fold_metrics_list)
        aggregate = self._calculate_aggregate(fold_metrics_df)
        stability = self._calculate_stability(fold_metrics_df)

        return WalkForwardResult(
            fold_results=fold_results,
            fold_metrics=fold_metrics_df,
            aggregate_metrics=aggregate,
            stability_score=stability,
            config=self.config,
        )

    def _calculate_aggregate(self, fold_metrics: pd.DataFrame) -> dict:
        """Calculate aggregate metrics across all folds."""
        numeric_cols = fold_metrics.select_dtypes(include=[np.number]).columns
        numeric_cols = [c for c in numeric_cols if c != "fold"]

        aggregate = {}
        for col in numeric_cols:
            values = fold_metrics[col].dropna()
            if len(values) > 0:
                aggregate[f"mean_{col}"] = float(values.mean())
                aggregate[f"std_{col}"] = float(values.std())
                aggregate[f"min_{col}"] = float(values.min())
                aggregate[f"max_{col}"] = float(values.max())
                aggregate[f"median_{col}"] = float(values.median())

        # Consistency metrics
        if "total_return" in fold_metrics.columns:
            returns = fold_metrics["total_return"]
            aggregate["pct_positive_returns"] = float((returns > 0).mean())
            aggregate["pct_negative_returns"] = float((returns < 0).mean())

        if "sharpe_ratio" in fold_metrics.columns:
            sharpes = fold_metrics["sharpe_ratio"]
            aggregate["pct_positive_sharpe"] = float((sharpes > 0).mean())
            aggregate["pct_sharpe_above_1"] = float((sharpes > 1.0).mean())

        if "max_drawdown" in fold_metrics.columns:
            drawdowns = fold_metrics["max_drawdown"]
            aggregate["worst_drawdown"] = float(drawdowns.min())
            aggregate["avg_drawdown"] = float(drawdowns.mean())

        return aggregate

    def _calculate_stability(self, fold_metrics: pd.DataFrame) -> float:
        """
        Calculate a stability score (0-100).

        Higher score means more consistent performance across folds.
        Based on coefficient of variation of returns and Sharpe ratios.
        """
        if len(fold_metrics) < 2:
            return 0.0

        scores = []

        # Return stability (lower CV = higher score)
        if "total_return" in fold_metrics.columns:
            returns = fold_metrics["total_return"]
            mean_ret = returns.mean()
            std_ret = returns.std()
            if std_ret > 0 and mean_ret != 0:
                cv_returns = abs(std_ret / mean_ret)
                return_score = max(0, 100 - cv_returns * 50)
                scores.append(return_score)

        # Sharpe stability
        if "sharpe_ratio" in fold_metrics.columns:
            sharpes = fold_metrics["sharpe_ratio"]
            mean_sharpe = sharpes.mean()
            std_sharpe = sharpes.std()
            if std_sharpe > 0 and mean_sharpe != 0:
                cv_sharpe = abs(std_sharpe / mean_sharpe)
                sharpe_score = max(0, 100 - cv_sharpe * 50)
                scores.append(sharpe_score)

        # Win rate consistency
        if "win_rate" in fold_metrics.columns:
            win_rates = fold_metrics["win_rate"]
            wr_std = win_rates.std()
            win_rate_score = max(0, 100 - wr_std * 200)
            scores.append(win_rate_score)

        # Drawdown consistency
        if "max_drawdown" in fold_metrics.columns:
            drawdowns = fold_metrics["max_drawdown"]
            dd_range = drawdowns.max() - drawdowns.min()
            dd_score = max(0, 100 - dd_range * 100)
            scores.append(dd_score)

        return float(np.mean(scores)) if scores else 0.0

    def generate_report(self, result: WalkForwardResult) -> pd.DataFrame:
        """Generate a detailed report DataFrame."""
        report = result.fold_metrics.copy()

        # Add consistency flags
        report["consistent_return"] = np.where(
            report["total_return"] > 0, "Positive", "Negative"
        )
        report["consistent_sharpe"] = np.where(
            report["sharpe_ratio"] > 1.0, "Good", "Poor"
        )
        report["severe_drawdown"] = np.where(
            report["max_drawdown"] < -0.20, "Severe", "Normal"
        )

        return report
