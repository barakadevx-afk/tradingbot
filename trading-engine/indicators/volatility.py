"""
Volatility Indicators
=====================

Provides volatility-based technical indicators:
- Bollinger Bands
- Average True Range (ATR)
- Standard Deviation
- Volatility Percentile
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class VolatilityIndicators:
    """
    Volatility-based technical indicators.
    
    Calculates indicators that measure price volatility
    for identifying potential breakouts and reversals.
    """

    BB_PERIOD: int = 20
    BB_STD_DEV: float = 2.0
    ATR_PERIOD: int = 14

    def calculate_all(self, df) -> Dict[str, Optional[float]]:
        """
        Calculate all volatility indicators.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with indicator values
        """
        if df.empty or len(df) < self.BB_PERIOD:
            return {
                "bb_upper": None,
                "bb_middle": None,
                "bb_lower": None,
                "bb_width": None,
                "bb_position": None,
                "atr": None,
                "atr_percentage": None,
                "std_dev": None,
                "volatility_regime": "unknown",
            }

        result = {}

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.bollinger_bands(df["close"])
        result["bb_upper"] = round(bb_upper, 8) if bb_upper else None
        result["bb_middle"] = round(bb_middle, 8) if bb_middle else None
        result["bb_lower"] = round(bb_lower, 8) if bb_lower else None

        # Bollinger Band Width
        if bb_upper and bb_lower and bb_middle:
            bb_width = (bb_upper - bb_lower) / bb_middle
            result["bb_width"] = round(bb_width, 4)
        else:
            result["bb_width"] = None

        # Bollinger Band Position (%B)
        current_price = df["close"].iloc[-1]
        if bb_upper and bb_lower and bb_upper != bb_lower:
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            result["bb_position"] = round(bb_position, 4)
        else:
            result["bb_position"] = None

        # ATR
        atr = self.average_true_range(df)
        result["atr"] = round(atr, 8) if atr else None

        # ATR as percentage of price
        if atr and current_price > 0:
            atr_pct = (atr / current_price) * 100
            result["atr_percentage"] = round(atr_pct, 4)
        else:
            result["atr_percentage"] = None

        # Standard Deviation
        std_dev = self.standard_deviation(df["close"])
        result["std_dev"] = round(std_dev, 8) if std_dev else None

        # Volatility Regime
        result["volatility_regime"] = self._classify_volatility(result)

        return result

    def bollinger_bands(
        self, series, period: int = 20, num_std: float = 2.0
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            series: Price series
            period: Moving average period
            num_std: Number of standard deviations
            
        Returns:
            Tuple of (upper, middle, lower) bands
        """
        if len(series) < period:
            return None, None, None

        middle = series.rolling(window=period).mean().iloc[-1]
        std = series.rolling(window=period).std().iloc[-1]

        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return upper, middle, lower

    def average_true_range(self, df, period: int = 14) -> Optional[float]:
        """
        Calculate Average True Range.
        
        ATR measures market volatility by decomposing the entire
        range of an asset price for that period.
        
        Args:
            df: DataFrame with OHLCV data
            period: ATR period
            
        Returns:
            Current ATR value or None
        """
        if len(df) < period + 1:
            return None

        high = df["high"].values
        low = df["low"].values
        close = df["close"].values

        # True Range calculation
        trs = []
        for i in range(1, len(df)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )
            trs.append(tr)

        if len(trs) < period:
            return None

        # Simple average of True Range
        atr = np.mean(trs[-period:])
        return atr

    def standard_deviation(self, series, period: int = 20) -> Optional[float]:
        """
        Calculate standard deviation of price.
        
        Args:
            series: Price series
            period: Calculation period
            
        Returns:
            Standard deviation or None
        """
        if len(series) < period:
            return None

        return series.rolling(window=period).std().iloc[-1]

    def _classify_volatility(self, result: Dict) -> str:
        """Classify current volatility regime."""
        bb_width = result.get("bb_width")
        atr_pct = result.get("atr_percentage")

        if bb_width is None or atr_pct is None:
            return "unknown"

        # Low volatility: narrow bands, low ATR%
        if bb_width < 0.05 and atr_pct < 2.0:
            return "low"

        # High volatility: wide bands, high ATR%
        if bb_width > 0.15 or atr_pct > 5.0:
            return "high"

        return "normal"
