"""
BARAKA AI - Backtesting Engine
==============================

Core backtesting engine that simulates strategy execution with realistic
fee and slippage modeling. Generates equity curves, trade lists,
monthly returns, and performance statistics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Union

import numpy as np
import pandas as pd

from .data_loader import DataLoader, DataConfig
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""

    # Symbol and data
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Capital and risk
    starting_balance: float = 100_000.0
    risk_per_trade: float = 0.01  # 1% risk per trade
    max_position_pct: float = 1.0  # Max position as fraction of equity
    allow_short: bool = True

    # Fees (as decimals, e.g., 0.001 = 0.1%)
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    slippage_model: str = "fixed"  # "fixed", "percentage", "volume_based"
    slippage_value: float = 0.0005  # 0.05% default slippage

    # Strategy
    strategy_name: str = "sma_crossover"
    strategy_params: dict = field(default_factory=dict)

    # AI Model
    ai_model: Optional[Any] = None  # Pre-trained model for signal generation
    ai_confidence_threshold: float = 0.55

    # Execution
    allow_partial_fills: bool = False
    fill_price_model: str = "next_bar"  # "next_bar", "same_bar", "vwap"

    # Metrics
    risk_free_rate: float = 0.0
    periods_per_year: int = 365 * 24  # Default for hourly crypto


@dataclass
class BacktestResult:
    """Container for backtest results."""

    equity_curve: pd.Series
    drawdown_series: pd.Series
    cumulative_return_series: pd.Series
    trades: pd.DataFrame
    monthly_returns: pd.DataFrame
    metrics: dict
    config: BacktestConfig
    signals: Optional[pd.DataFrame] = None
    positions: Optional[pd.DataFrame] = None

    def summary(self) -> str:
        """Print a formatted summary of the backtest."""
        lines = [
            "=" * 70,
            f"BARAKA AI - Backtest Result: {self.config.strategy_name}",
            "=" * 70,
            f"  Symbol:              {self.config.symbol}",
            f"  Timeframe:           {self.config.timeframe}",
            f"  Period:              {self.equity_curve.index[0]} to {self.equity_curve.index[-1]}",
            f"  Starting Balance:    {self.config.starting_balance:>14,.2f}",
            f"  Final Balance:       {self.equity_curve.iloc[-1]:>14,.2f}",
            "",
            self._metrics_summary(),
            "=" * 70,
        ]
        return "\n".join(lines)

    def _metrics_summary(self) -> str:
        m = self.metrics
        lines = [
            f"  Total Return:        {m.get('total_return', 0):>12.2%}",
            f"  Annualized Return:   {m.get('annualized_return', 0):>12.2%}",
            f"  Sharpe Ratio:        {m.get('sharpe_ratio', 0):>12.2f}",
            f"  Sortino Ratio:       {m.get('sortino_ratio', 0):>12.2f}",
            f"  Max Drawdown:        {m.get('max_drawdown', 0):>12.2%}",
            f"  Win Rate:            {m.get('win_rate', 0):>12.2%}",
            f"  Profit Factor:       {m.get('profit_factor', 0):>12.2f}",
            f"  Total Trades:        {m.get('total_trades', 0):>12d}",
        ]
        return "\n".join(lines)


class BacktestEngine:
    """
    Production-grade backtesting engine for BARAKA AI.

    Simulates realistic trade execution with configurable fees,
    slippage, and position sizing. Supports both rule-based and
    AI-driven signal generation.
    """

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.data: Optional[pd.DataFrame] = None
        self.data_loader: Optional[DataLoader] = None

    def load_data(
        self,
        data: Optional[Union[str, Path, pd.DataFrame]] = None,
        data_config: Optional[DataConfig] = None,
    ) -> pd.DataFrame:
        """
        Load historical data for backtesting.

        Parameters
        ----------
        data : str, Path, pd.DataFrame, or None
            Data source. If None, must provide data_config with data_path.
        data_config : DataConfig, optional
            Data loading configuration.

        Returns
        -------
        pd.DataFrame
            Loaded OHLCV data.
        """
        if data_config is None:
            data_config = DataConfig(
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
                start_date=self.config.start_date,
                end_date=self.config.end_date,
            )
        if isinstance(data, (str, Path)) and data_config.data_path is None:
            data_config.data_path = data

        self.data_loader = DataLoader(data_config)
        self.data = self.data_loader.load(data)
        return self.data

    def run(self, data: Optional[pd.DataFrame] = None) -> BacktestResult:
        """
        Execute the backtest.

        Parameters
        ----------
        data : pd.DataFrame, optional
            OHLCV data. If None, uses previously loaded data.

        Returns
        -------
        BacktestResult
            Complete backtest results.
        """
        if data is not None:
            self.data = data
        if self.data is None:
            self.load_data()

        df = self.data.copy()
        logger.info(
            "Starting backtest: %s [%s] from %s to %s",
            self.config.strategy_name,
            self.config.symbol,
            df.index[0],
            df.index[-1],
        )

        # Generate signals
        signals = self._generate_signals(df)
        df["signal"] = signals["signal"] if isinstance(signals, pd.DataFrame) else signals

        # Simulate trades
        trades, equity_curve, positions = self._simulate_trades(df, signals)

        # Calculate drawdown
        drawdown_series = self._calculate_drawdown(equity_curve)
        cumulative_return_series = self._calculate_cumulative_return(equity_curve)

        # Monthly returns
        monthly_returns = self._calculate_monthly_returns(equity_curve)

        # Performance metrics
        metrics_calculator = PerformanceMetrics(
            equity_curve=equity_curve,
            trades=trades,
            risk_free_rate=self.config.risk_free_rate,
            periods_per_year=self.config.periods_per_year,
        )
        metrics = metrics_calculator.results

        result = BacktestResult(
            equity_curve=equity_curve,
            drawdown_series=drawdown_series,
            cumulative_return_series=cumulative_return_series,
            trades=trades,
            monthly_returns=monthly_returns,
            metrics=metrics,
            config=self.config,
            signals=signals if isinstance(signals, pd.DataFrame) else None,
            positions=positions,
        )

        logger.info(
            "Backtest complete. Total Return: %.2f%%, Trades: %d, Sharpe: %.2f",
            metrics["total_return"] * 100,
            metrics["total_trades"],
            metrics["sharpe_ratio"],
        )
        return result

    def _generate_signals(self, df: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        Generate trading signals from strategy or AI model.

        Returns signal series: 1 (buy), -1 (sell/short), 0 (hold).
        """
        if self.config.ai_model is not None:
            return self._generate_ai_signals(df)
        return self._generate_strategy_signals(df)

    def _generate_strategy_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate signals from the configured strategy."""
        strategy = self.config.strategy_name.lower()
        params = self.config.strategy_params

        if strategy == "sma_crossover":
            return self._sma_crossover_signals(
                df,
                fast_period=params.get("fast_period", 10),
                slow_period=params.get("slow_period", 30),
            )
        elif strategy == "ema_crossover":
            return self._ema_crossover_signals(
                df,
                fast_period=params.get("fast_period", 12),
                slow_period=params.get("slow_period", 26),
            )
        elif strategy == "rsi_reversal":
            return self._rsi_reversal_signals(
                df,
                period=params.get("period", 14),
                oversold=params.get("oversold", 30),
                overbought=params.get("overbought", 70),
            )
        elif strategy == "macd":
            return self._macd_signals(
                df,
                fast=params.get("fast", 12),
                slow=params.get("slow", 26),
                signal=params.get("signal", 9),
            )
        elif strategy == "bollinger_bands":
            return self._bollinger_signals(
                df,
                period=params.get("period", 20),
                num_std=params.get("num_std", 2.0),
            )
        elif strategy == "buy_and_hold":
            return self._buy_and_hold_signal(df)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _generate_ai_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals from an AI model.

        The AI model should have a predict() or predict_proba() method
        that returns trade signals with confidence scores.
        """
        model = self.config.ai_model
        signals = pd.DataFrame(index=df.index)
        signals["signal"] = 0
        signals["confidence"] = 0.0

        # Try different model interfaces
        if hasattr(model, "predict_proba"):
            # Classification model with probabilities
            features = self._extract_features(df)
            probs = model.predict_proba(features)
            if probs.ndim == 2 and probs.shape[1] >= 2:
                # Binary classification: [prob_sell, prob_buy]
                signals["confidence"] = np.abs(probs[:, 1] - 0.5) * 2
                buy_mask = probs[:, 1] > self.config.ai_confidence_threshold
                sell_mask = probs[:, 0] > self.config.ai_confidence_threshold
                signals.loc[buy_mask, "signal"] = 1
                signals.loc[sell_mask, "signal"] = -1
        elif hasattr(model, "predict"):
            # Direct prediction model
            features = self._extract_features(df)
            predictions = model.predict(features)
            signals["signal"] = predictions
            signals["confidence"] = 1.0
        else:
            raise ValueError(
                "AI model must have predict() or predict_proba() method"
            )

        return signals

    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for AI model from OHLCV data."""
        features = pd.DataFrame(index=df.index)

        # Price-based features
        features["returns"] = df["close"].pct_change()
        features["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # Moving averages
        for period in [5, 10, 20, 50]:
            features[f"sma_{period}"] = df["close"].rolling(period).mean()
            features[f"ema_{period}"] = df["close"].ewm(span=period).mean()

        # Volatility
        features["volatility"] = features["returns"].rolling(20).std()

        # RSI
        features["rsi"] = self._calculate_rsi(df["close"], 14)

        # MACD
        ema_12 = df["close"].ewm(span=12).mean()
        ema_26 = df["close"].ewm(span=26).mean()
        features["macd"] = ema_12 - ema_26
        features["macd_signal"] = features["macd"].ewm(span=9).mean()

        # Volume features
        features["volume_sma"] = df["volume"].rolling(20).mean()
        features["volume_ratio"] = df["volume"] / features["volume_sma"]

        # Price position
        features["close_to_sma20"] = df["close"] / features["sma_20"] - 1

        return features.dropna().values

    def _simulate_trades(
        self, df: pd.DataFrame, signals: Union[pd.Series, pd.DataFrame]
    ) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """
        Simulate trade execution with fees and slippage.

        Returns
        -------
        trades : pd.DataFrame
            Completed trades.
        equity_curve : pd.Series
            Portfolio equity over time.
        positions : pd.DataFrame
            Position tracking over time.
        """
        if isinstance(signals, pd.DataFrame):
            signal_series = signals["signal"]
        else:
            signal_series = signals

        n = len(df)
        equity = self.config.starting_balance
        position = 0  # Current position size in units
        entry_price = 0.0
        entry_time = None
        entry_equity = equity

        # Tracking
        equity_curve = pd.Series(index=df.index, dtype=float)
        positions = pd.DataFrame(
            index=df.index,
            columns=["position", "cash", "holdings", "equity"],
            dtype=float,
        )

        trades = []
        position_size = 0

        for i in range(n):
            timestamp = df.index[i]
            row = df.iloc[i]
            signal = signal_series.iloc[i] if i < len(signal_series) else 0

            current_price = row["close"]

            # Execute signal
            if signal == 1 and position <= 0:
                # Buy signal - close any short, then go long
                if position < 0:
                    # Close short
                    pnl = self._close_short(
                        entry_price, current_price, abs(position), timestamp, trades
                    )
                    equity += pnl
                    position = 0

                # Open long
                if position == 0:
                    position_size = self._calculate_position_size(equity, current_price)
                    if position_size > 0:
                        fill_price = self._apply_slippage(current_price, "buy")
                        fee = position_size * fill_price * self.config.taker_fee
                        cost = position_size * fill_price + fee
                        if cost <= equity:
                            position = position_size
                            entry_price = fill_price
                            entry_time = timestamp
                            entry_equity = equity
                            equity -= cost

            elif signal == -1 and position >= 0:
                # Sell signal - close any long, then go short
                if position > 0:
                    # Close long
                    pnl = self._close_long(
                        entry_price, current_price, position, timestamp, trades
                    )
                    equity += pnl
                    position = 0

                # Open short if allowed
                if position == 0 and self.config.allow_short:
                    position_size = self._calculate_position_size(equity, current_price)
                    if position_size > 0:
                        fill_price = self._apply_slippage(current_price, "sell")
                        fee = position_size * fill_price * self.config.taker_fee
                        # For shorts, we receive cash minus fee
                        proceeds = position_size * fill_price - fee
                        position = -position_size
                        entry_price = fill_price
                        entry_time = timestamp
                        entry_equity = equity
                        equity += proceeds

            # Mark-to-market equity
            if position > 0:
                holdings_value = position * current_price
            elif position < 0:
                # Short: profit from price decrease
                holdings_value = position * (2 * entry_price - current_price)
            else:
                holdings_value = 0.0

            total_equity = equity + holdings_value
            equity_curve.iloc[i] = total_equity
            positions.iloc[i] = [position, equity, holdings_value, total_equity]

        # Close any open position at the end
        if position != 0:
            final_price = df["close"].iloc[-1]
            final_time = df.index[-1]
            if position > 0:
                self._close_long(
                    entry_price, final_price, position, final_time, trades
                )
            else:
                self._close_short(
                    entry_price, final_price, abs(position), final_time, trades
                )
            equity_curve.iloc[-1] = equity

        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame(
            columns=[
                "entry_time", "exit_time", "side", "entry_price",
                "exit_price", "quantity", "pnl", "return_pct", "holding_time",
            ]
        )

        return trades_df, equity_curve, positions

    def _calculate_position_size(self, equity: float, price: float) -> float:
        """Calculate position size based on risk settings."""
        if price <= 0:
            return 0.0
        max_value = equity * self.config.max_position_pct
        position_size = max_value / price
        return position_size

    def _apply_slippage(self, price: float, side: str) -> float:
        """Apply slippage to the fill price."""
        model = self.config.slippage_model
        value = self.config.slippage_value

        if model == "fixed":
            slippage = value
        elif model == "percentage":
            slippage = price * value
        elif model == "volume_based":
            # Higher slippage for larger orders (simplified)
            slippage = price * value * 1.5
        else:
            slippage = price * 0.0005  # Default 0.05%

        if side == "buy":
            return price + slippage
        else:
            return price - slippage

    def _close_long(
        self,
        entry_price: float,
        exit_price: float,
        quantity: float,
        exit_time: Any,
        trades: list,
    ) -> float:
        """Close a long position and record the trade."""
        gross_pnl = (exit_price - entry_price) * quantity
        exit_fee = exit_price * quantity * self.config.taker_fee
        net_pnl = gross_pnl - exit_fee

        entry_time = None
        if trades:
            # Find matching entry
            for t in reversed(trades):
                if t.get("side") == "long" and t.get("exit_time") is None:
                    entry_time = t["entry_time"]
                    break

        trade = {
            "entry_time": entry_time,
            "exit_time": exit_time,
            "side": "long",
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl": net_pnl,
            "return_pct": (exit_price - entry_price) / entry_price if entry_price > 0 else 0,
            "holding_time": None,
        }
        trades.append(trade)
        return net_pnl

    def _close_short(
        self,
        entry_price: float,
        exit_price: float,
        quantity: float,
        exit_time: Any,
        trades: list,
    ) -> float:
        """Close a short position and record the trade."""
        gross_pnl = (entry_price - exit_price) * quantity
        exit_fee = exit_price * quantity * self.config.taker_fee
        net_pnl = gross_pnl - exit_fee

        entry_time = None
        if trades:
            for t in reversed(trades):
                if t.get("side") == "short" and t.get("exit_time") is None:
                    entry_time = t["entry_time"]
                    break

        trade = {
            "entry_time": entry_time,
            "exit_time": exit_time,
            "side": "short",
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl": net_pnl,
            "return_pct": (entry_price - exit_price) / entry_price if entry_price > 0 else 0,
            "holding_time": None,
        }
        trades.append(trade)
        return net_pnl

    def _calculate_drawdown(self, equity_curve: pd.Series) -> pd.Series:
        """Calculate drawdown series."""
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        return drawdown

    def _calculate_cumulative_return(self, equity_curve: pd.Series) -> pd.Series:
        """Calculate cumulative return series."""
        return equity_curve / equity_curve.iloc[0] - 1.0

    def _calculate_monthly_returns(self, equity_curve: pd.Series) -> pd.DataFrame:
        """Calculate monthly returns from equity curve."""
        monthly = equity_curve.resample("ME").last()
        monthly_returns = monthly.pct_change().dropna()

        df = pd.DataFrame({
            "month": monthly_returns.index.strftime("%Y-%m"),
            "return": monthly_returns.values,
            "equity": monthly.loc[monthly_returns.index].values,
        })
        return df

    # ---- Strategy Signal Generators ----

    @staticmethod
    def _sma_crossover_signals(
        df: pd.DataFrame, fast_period: int = 10, slow_period: int = 30
    ) -> pd.DataFrame:
        """Generate SMA crossover signals."""
        signals = pd.DataFrame(index=df.index)
        sma_fast = df["close"].rolling(fast_period).mean()
        sma_slow = df["close"].rolling(slow_period).mean()

        signals["signal"] = 0
        signals.loc[sma_fast > sma_slow, "signal"] = 1
        signals.loc[sma_fast < sma_slow, "signal"] = -1

        # Only trade on crossovers
        signals["signal"] = signals["signal"].diff().fillna(0)
        signals.loc[signals["signal"] > 0, "signal"] = 1
        signals.loc[signals["signal"] < 0, "signal"] = -1
        signals.loc[signals["signal"].abs() > 1, "signal"] = 0

        signals["sma_fast"] = sma_fast
        signals["sma_slow"] = sma_slow
        return signals

    @staticmethod
    def _ema_crossover_signals(
        df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26
    ) -> pd.DataFrame:
        """Generate EMA crossover signals."""
        signals = pd.DataFrame(index=df.index)
        ema_fast = df["close"].ewm(span=fast_period).mean()
        ema_slow = df["close"].ewm(span=slow_period).mean()

        signals["signal"] = 0
        signals.loc[ema_fast > ema_slow, "signal"] = 1
        signals.loc[ema_fast < ema_slow, "signal"] = -1

        signals["ema_fast"] = ema_fast
        signals["ema_slow"] = ema_slow
        return signals

    @staticmethod
    def _rsi_reversal_signals(
        df: pd.DataFrame, period: int = 14, oversold: float = 30, overbought: float = 70
    ) -> pd.DataFrame:
        """Generate RSI mean-reversion signals."""
        signals = pd.DataFrame(index=df.index)
        rsi = BacktestEngine._calculate_rsi(df["close"], period)

        signals["signal"] = 0
        signals.loc[rsi < oversold, "signal"] = 1  # Buy at oversold
        signals.loc[rsi > overbought, "signal"] = -1  # Sell at overbought

        signals["rsi"] = rsi
        return signals

    @staticmethod
    def _macd_signals(
        df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> pd.DataFrame:
        """Generate MACD signals."""
        signals = pd.DataFrame(index=df.index)
        ema_fast = df["close"].ewm(span=fast).mean()
        ema_slow = df["close"].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        signals["signal"] = 0
        signals.loc[macd_line > signal_line, "signal"] = 1
        signals.loc[macd_line < signal_line, "signal"] = -1

        signals["macd"] = macd_line
        signals["signal_line"] = signal_line
        signals["histogram"] = histogram
        return signals

    @staticmethod
    def _bollinger_signals(
        df: pd.DataFrame, period: int = 20, num_std: float = 2.0
    ) -> pd.DataFrame:
        """Generate Bollinger Bands mean-reversion signals."""
        signals = pd.DataFrame(index=df.index)
        sma = df["close"].rolling(period).mean()
        std = df["close"].rolling(period).std()
        upper = sma + num_std * std
        lower = sma - num_std * std

        signals["signal"] = 0
        signals.loc[df["close"] < lower, "signal"] = 1  # Buy at lower band
        signals.loc[df["close"] > upper, "signal"] = -1  # Sell at upper band

        signals["bb_middle"] = sma
        signals["bb_upper"] = upper
        signals["bb_lower"] = lower
        return signals

    @staticmethod
    def _buy_and_hold_signal(df: pd.DataFrame) -> pd.DataFrame:
        """Generate a simple buy-and-hold signal."""
        signals = pd.DataFrame(index=df.index)
        signals["signal"] = 1
        signals.iloc[0] = 0  # No trade on first bar
        return signals

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
