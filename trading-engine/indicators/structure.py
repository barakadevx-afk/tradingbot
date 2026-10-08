"""
Market Structure Indicators
===========================

Provides market structure analysis:
- Support and resistance levels
- Breakout and breakdown detection
- Trend continuation and reversal patterns
- Consolidation detection
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class StructureIndicators:
    """
    Market structure analysis indicators.
    
    Identifies key structural levels and patterns in price action
    for strategic decision-making.
    """

    def calculate_all(self, df) -> Dict[str, any]:
        """
        Calculate all structure indicators.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with structure analysis results
        """
        if df.empty or len(df) < 20:
            return {
                "support_levels": [],
                "resistance_levels": [],
                "breakout_detected": False,
                "breakdown_detected": False,
                "consolidation": False,
                "structure_type": "unknown",
            }

        result = {}

        # Support and Resistance
        support, resistance = self.find_support_resistance(df)
        result["support_levels"] = [round(s, 8) for s in support]
        result["resistance_levels"] = [round(r, 8) for r in resistance]

        # Breakout/Breakdown
        result["breakout_detected"] = self.detect_breakout(df, resistance)
        result["breakdown_detected"] = self.detect_breakdown(df, support)

        # Consolidation
        result["consolidation"] = self.detect_consolidation(df)

        # Structure Type
        result["structure_type"] = self._classify_structure(df, result)

        return result

    def find_support_resistance(
        self, df, tolerance: float = 0.02, min_touches: int = 2
    ) -> Tuple[List[float], List[float]]:
        """
        Find key support and resistance levels.
        
        Uses swing highs/lows and clusters nearby levels.
        
        Args:
            df: DataFrame with OHLCV data
            tolerance: Percentage tolerance for level clustering
            min_touches: Minimum number of touches to confirm level
            
        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        # Find swing highs and lows
        swing_highs = self._find_swing_highs(df)
        swing_lows = self._find_swing_lows(df)

        # Cluster nearby levels
        resistance = self._cluster_levels(swing_highs, tolerance, min_touches)
        support = self._cluster_levels(swing_lows, tolerance, min_touches)

        return support, resistance

    def detect_breakout(self, df, resistance_levels: List[float]) -> bool:
        """
        Detect if price has broken above resistance.
        
        Args:
            df: DataFrame with OHLCV data
            resistance_levels: List of resistance levels
            
        Returns:
            True if breakout detected
        """
        if not resistance_levels:
            return False

        current_price = df["close"].iloc[-1]
        recent_high = df["high"].tail(5).max()

        # Check if price is above any recent resistance
        for level in resistance_levels:
            if current_price > level and recent_high > level:
                return True

        return False

    def detect_breakdown(self, df, support_levels: List[float]) -> bool:
        """
        Detect if price has broken below support.
        
        Args:
            df: DataFrame with OHLCV data
            support_levels: List of support levels
            
        Returns:
            True if breakdown detected
        """
        if not support_levels:
            return False

        current_price = df["close"].iloc[-1]
        recent_low = df["low"].tail(5).min()

        # Check if price is below any recent support
        for level in support_levels:
            if current_price < level and recent_low < level:
                return True

        return False

    def detect_consolidation(self, df, period: int = 20, threshold: float = 0.03) -> bool:
        """
        Detect if price is in consolidation.
        
        Identifies periods of low volatility and sideways movement.
        
        Args:
            df: DataFrame with OHLCV data
            period: Lookback period
            threshold: Maximum range as percentage of price
            
        Returns:
            True if consolidation detected
        """
        if len(df) < period:
            return False

        recent = df.tail(period)
        price_range = recent["high"].max() - recent["low"].min()
        avg_price = recent["close"].mean()

        if avg_price == 0:
            return False

        range_pct = price_range / avg_price

        # Check if price is moving sideways
        price_change = abs(recent["close"].iloc[-1] - recent["close"].iloc[0])
        change_pct = price_change / avg_price

        return range_pct < threshold and change_pct < threshold

    def _find_swing_highs(self, df, window: int = 5) -> List[float]:
        """Find swing high points."""
        highs = []
        for i in range(window, len(df) - window):
            is_swing = True
            for j in range(1, window + 1):
                if df["high"].iloc[i] <= df["high"].iloc[i - j] or \
                   df["high"].iloc[i] <= df["high"].iloc[i + j]:
                    is_swing = False
                    break
            if is_swing:
                highs.append(df["high"].iloc[i])
        return highs

    def _find_swing_lows(self, df, window: int = 5) -> List[float]:
        """Find swing low points."""
        lows = []
        for i in range(window, len(df) - window):
            is_swing = True
            for j in range(1, window + 1):
                if df["low"].iloc[i] >= df["low"].iloc[i - j] or \
                   df["low"].iloc[i] >= df["low"].iloc[i + j]:
                    is_swing = False
                    break
            if is_swing:
                lows.append(df["low"].iloc[i])
        return lows

    def _cluster_levels(
        self, levels: List[float], tolerance: float, min_touches: int
    ) -> List[float]:
        """Cluster nearby price levels."""
        if not levels:
            return []

        levels.sort()
        clusters = []
        current_cluster = [levels[0]]

        for level in levels[1:]:
            if level - current_cluster[-1] <= tolerance * current_cluster[-1]:
                current_cluster.append(level)
            else:
                if len(current_cluster) >= min_touches:
                    clusters.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]

        if len(current_cluster) >= min_touches:
            clusters.append(sum(current_cluster) / len(current_cluster))

        return clusters

    def _classify_structure(self, df, result: Dict) -> str:
        """Classify the current market structure."""
        if result["breakout_detected"]:
            return "breakout"
        elif result["breakdown_detected"]:
            return "breakdown"
        elif result["consolidation"]:
            return "consolidation"
        else:
            return "trending"
