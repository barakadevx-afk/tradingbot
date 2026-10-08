"""
Trend Indicators
================

Provides trend-following technical indicators:
- Exponential Moving Average (EMA) with periods 9, 20, 50, 100, 200
- Simple Moving Average (SMA) with periods 20, 50, 200
- Average Directional Index (ADX) for trend strength

All calculations use numpy/pandas for performance.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TrendResult:
    """Container for trend indicator results."""
    ema_9: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_100: Optional[float] = None
    ema_200: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None
    trend_direction: str = "neutral"
    trend_strength: str = "weak"

    def to_dict(self) -> Dict[str, Optional[float]]:
        """Convert to dictionary."""
        return {
            "ema_9": self.ema_9,
            "ema_20": self.ema_20,
            "ema_50": self.ema_50,
            "ema_100": self.ema_100,
            "ema_200": self.ema_200,
            "sma_20": self.sma_20,
            "sma_50": self.sma_50,
            "sma_200": self.sma_200,
            "adx": self.adx,
            "plus_di": self.plus_di,
            "minus_di": self.minus_di,
            "trend_direction": self.trend_direction,
            "trend_strength": self.trend_strength,
        }


class TrendIndicators:
    """
    Trend-following technical indicators.

    Calculates EMA, SMA, and ADX for trend identification and strength assessment.
    """

    EMA_PERIODS: List[int] = [9, 20, 50, 100, 200]
    SMA_PERIODS: List[int] = [20, 50, 200]
    ADX_PERIOD: int = 14

    def __init__(self):
        self._cache: Dict[str, pd.Series] = {}

    def calculate_all(self, df: pd.DataFrame) -> TrendResult:
        """
        Calculate all trend indicators on a OHLCV DataFrame.

        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']

        Returns:
            TrendResult with all calculated indicators
        """
        if df.empty or len(df) < 2:
            return TrendResult()

        result = TrendResult()

        # Calculate EMAs
        for period in self.EMA_PERIODS:
            ema = self.ema(df["close"], period)
            setattr(result, f"ema_{period}", float(ema.iloc[-1]) if not ema.empty else None)

        # Calculate SMAs
        for period in self.SMA_PERIODS:
            sma = self.sma(df["close"], period)
            setattr(result, f"sma_{period}", float(sma.iloc[-1]) if not sma.empty else None)

        # Calculate ADX
        adx_result = self.adx(df, self.ADX_PERIOD)
        result.adx = adx_result.get("adx")
        result.plus_di = adx_result.get("plus_di")
        result.minus_di = adx_result.get("minus_di")

        # Determine trend direction and strength
        result.trend_direction = self._determine_trend_direction(result)
        result.trend_strength = self._determine_trend_strength(result)

        return result

    def ema(self, series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.

        Args:
            series: Price series
            period: EMA period

        Returns:
            EMA series
        """
        if len(series) < period:
            return pd.Series(dtype=float)
        return series.ewm(span=period, adjust=False, min_periods=period).mean()

    def sma(self, series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average.

        Args:
            series: Price series
            period: SMA period

        Returns:
            SMA series
        """
        if len(series) < period:
            return pd.Series(dtype=float)
        return series.rolling(window=period, min_periods=period).mean()

    def adx(self, df: pd.DataFrame, period: int = 14) -> Dict[str, Optional[float]]:
        """
        Calculate Average Directional Index (ADX).

        ADX measures trend strength regardless of direction.
        Values above 25 indicate strong trend, below 20 indicate weak trend.

        Args:
            df: OHLCV DataFrame
            period: ADX calculation period

        Returns:
            Dictionary with 'adx', 'plus_di', 'minus_di' values
        """
        if len(df) < period + 1:
            return {"adx": None, "plus_di": None, "minus_di": None}

        high = df["high"].values
        low = df["low"].values
        close = df["close"].values

        # Calculate True Range
        tr = self._true_range(high, low, close)

        # Calculate Directional Movement
        plus_dm, minus_dm = self._directional_movement(high, low)

        # Calculate smoothed values
        atr = self._wilder_smooth(tr, period)
        plus_di = 100 * self._wilder_smooth(plus_dm, period) / atr
        minus_di = 100 * self._wilder_smooth(minus_dm, period) / atr

        # Calculate DX and ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        dx = np.where((plus_di + minus_di) == 0, 0, dx)
        adx = self._wilder_smooth(dx, period)

        return {
            "adx": float(adx[-1]) if len(adx) > 0 else None,
            "plus_di": float(plus_di[-1]) if len(plus_di) > 0 else None,
            "minus_di": float(minus_di[-1]) if len(minus_di) > 0 else None,
        }

    def _true_range(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
        """Calculate True Range."""
        tr = np.zeros(len(high))
        tr[0] = high[0] - low[0]

        for i in range(1, len(high)):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )
        return tr

    def _directional_movement(self, high: np.ndarray, low: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Plus and Minus Directional Movement."""
        plus_dm = np.zeros(len(high))
        minus_dm = np.zeros(len(high))

        for i in range(1, len(high)):
            up_move = high[i] - high[i - 1]
            down_move = low[i - 1] - low[i]

            if up_move > down_move and up_move > 0:
                plus_dm[i] = up_move
            if down_move > up_move and down_move > 0:
                minus_dm[i] = down_move

        return plus_dm, minus_dm

    def _wilder_smooth(self, values: np.ndarray, period: int) -> np.ndarray:
        """
        Apply Wilder's smoothing method.

        This is an exponential smoothing with alpha = 1/period.
        """
        if len(values) < period:
            return np.array([])

        smoothed = np.zeros(len(values))
        # First value is simple average
        smoothed[period - 1] = np.mean(values[:period])

        alpha = 1.0 / period
        for i in range(period, len(values)):
            smoothed[i] = smoothed[i - 1] * (1 - alpha) + values[i] * alpha

        return smoothed[period - 1:]

    def _determine_trend_direction(self, result: TrendResult) -> str:
        """Determine trend direction based on EMA structure."""
        if result.ema_9 is None or result.ema_20 is None or result.ema_50 is None:
            return "neutral"

        # Bullish: EMA9 > EMA20 > EMA50
        if result.ema_9 > result.ema_20 > result.ema_50:
            return "bullish"
        # Bearish: EMA9 < EMA20 < EMA50
        elif result.ema_9 < result.ema_20 < result.ema_50:
            return "bearish"
        # Mixed
        else:
            return "mixed"

    def _determine_trend_strength(self, result: TrendResult) -> str:
        """Determine trend strength based on ADX."""
        if result.adx is None:
            return "weak"

        if result.adx >= 50:
            return "very_strong"
        elif result.adx >= 25:
            return "strong"
        elif result.adx >= 20:
            return "moderate"
        else:
            return "weak"

    def get_ema_crossover(self, df: pd.DataFrame, fast_period: int = 9, slow_period: int = 20) -> Optional[str]:
        """
        Detect EMA crossover signals.

        Returns:
            'golden_cross' if fast crosses above slow
            'death_cross' if fast crosses below slow
            None if no crossover
        """
        if len(df) < slow_period + 1:
            return None

        fast_ema = self.ema(df["close"], fast_period)
        slow_ema = self.ema(df["close"], slow_period)

        if len(fast_ema) < 2 or len(slow_ema) < 2:
            return None

        # Check for crossover on the last candle
        prev_diff = fast_ema.iloc[-2] - slow_ema.iloc[-2]
        curr_diff = fast_ema.iloc[-1] - slow_ema.iloc[-1]

        if prev_diff <= 0 and curr_diff > 0:
            return "golden_cross"
        elif prev_diff >= 0 and curr_diff < 0:
            return "death_cross"

        return None

    def get_price_vs_ema(self, price: float, ema_value: Optional[float]) -> Optional[str]:
        """Determine if price is above or below an EMA."""
        if ema_value is None:
            return None
        if price > ema_value:
            return "above"
        elif price < ema_value:
            return "below"
        return "at"

    def reset(self) -> None:
        """Reset indicator cache."""
        self._cache.clear()
