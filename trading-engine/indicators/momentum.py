"""
Momentum Indicators
===================

Provides momentum-based technical indicators:
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Stochastic Oscillator
- Rate of Change (ROC)
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class MomentumIndicators:
    """
    Momentum-based technical indicators.
    
    Calculates RSI, MACD, Stochastic, and ROC for
    identifying overbought/oversold conditions and trend strength.
    """

    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    STOCH_K: int = 14
    STOCH_D: int = 3
    ROC_PERIOD: int = 10

    def calculate_all(self, df) -> Dict[str, Optional[float]]:
        """
        Calculate all momentum indicators.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with indicator values
        """
        if df.empty or len(df) < self.MACD_SLOW:
            return {
                "rsi": None,
                "macd": None,
                "macd_signal": None,
                "macd_histogram": None,
                "stoch_k": None,
                "stoch_d": None,
                "roc": None,
            }

        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values

        rsi = self.rsi(closes)
        macd_line, signal_line, histogram = self.macd(closes)
        stoch_k, stoch_d = self.stochastic(highs, lows, closes)
        roc = self.rate_of_change(closes)

        return {
            "rsi": round(rsi, 2) if rsi is not None else None,
            "macd": round(macd_line, 8) if macd_line is not None else None,
            "macd_signal": round(signal_line, 8) if signal_line is not None else None,
            "macd_histogram": round(histogram, 8) if histogram is not None else None,
            "stoch_k": round(stoch_k, 2) if stoch_k is not None else None,
            "stoch_d": round(stoch_d, 2) if stoch_d is not None else None,
            "roc": round(roc, 4) if roc is not None else None,
        }

    def rsi(self, closes: np.ndarray, period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index.
        
        RSI measures speed and change of price movements.
        Values above 70 indicate overbought, below 30 oversold.
        
        Args:
            closes: Array of closing prices
            period: RSI period (default 14)
            
        Returns:
            Current RSI value or None
        """
        if len(closes) < period + 1:
            return None

        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def macd(
        self, closes: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        MACD shows relationship between two EMAs of price.
        
        Args:
            closes: Array of closing prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Tuple of (MACD line, signal line, histogram)
        """
        if len(closes) < slow + signal:
            return None, None, None

        ema_fast = self._ema(closes, fast)
        ema_slow = self._ema(closes, slow)
        macd_line = ema_fast - ema_slow

        # Signal line is EMA of MACD
        macd_history = []
        for i in range(slow, len(closes) + 1):
            macd_history.append(self._ema(closes[:i], fast) - self._ema(closes[:i], slow))

        signal_line = self._ema(np.array(macd_history), signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def stochastic(
        self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, k_period: int = 14, d_period: int = 3
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate Stochastic Oscillator.
        
        Compares closing price to price range over a period.
        %K is fast line, %D is slow line (SMA of %K).
        
        Args:
            highs: Array of high prices
            lows: Array of low prices
            closes: Array of closing prices
            k_period: %K period
            d_period: %D period
            
        Returns:
            Tuple of (%K, %D)
        """
        if len(closes) < k_period + d_period:
            return None, None

        lowest_low = np.min(lows[-k_period:])
        highest_high = np.max(highs[-k_period:])

        if highest_high == lowest_low:
            return 50.0, 50.0

        k = 100 * (closes[-1] - lowest_low) / (highest_high - lowest_low)

        # Calculate %D as SMA of %K values
        k_values = []
        for i in range(k_period, len(closes) + 1):
            ll = np.min(lows[-i:][:k_period])
            hh = np.max(highs[-i:][:k_period])
            if hh != ll:
                k_values.append(100 * (closes[i - 1] - ll) / (hh - ll))

        d = np.mean(k_values[-d_period:]) if len(k_values) >= d_period else np.mean(k_values)

        return k, d

    def rate_of_change(self, closes: np.ndarray, period: int = 10) -> Optional[float]:
        """
        Calculate Rate of Change.
        
        Measures percentage change in price over a period.
        
        Args:
            closes: Array of closing prices
            period: ROC period
            
        Returns:
            ROC value as percentage or None
        """
        if len(closes) < period + 1:
            return return None

        current = closes[-1]
        previous = closes[-period - 1]

        if previous == 0:
            return None

        roc = ((current - previous) / previous) * 100
        return roc

    def _ema(self, data: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(data) < period:
            return float(np.mean(data))

        multiplier = 2 / (period + 1)
        ema = float(np.mean(data[:period]))

        for price in data[period:]:
            ema = (price - ema) * multiplier + ema

        return ema
