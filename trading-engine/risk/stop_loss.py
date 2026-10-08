"""
Stop Loss Calculator
====================

Provides multiple stop loss calculation methods:
- ATR-based stop loss
- Structure-based stop loss (below support/above resistance)
- Volatility-adjusted stop loss
- Percentage-based stop loss
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class StopLossType(Enum):
    """Types of stop loss calculations."""
    ATR = "ATR"
    STRUCTURE = "STRUCTURE"
    VOLATILITY = "VOLATILITY"
    PERCENTAGE = "PERCENTAGE"
    CHANDLE_EXIT = "CHANDLE_EXIT"


@dataclass
class StopLossResult:
    """Result of stop loss calculation."""
    stop_loss: float
    stop_loss_type: StopLossType
    distance: float  # Distance from entry
    distance_percentage: float  # Distance as percentage
    reasoning: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stop_loss": self.stop_loss,
            "stop_loss_type": self.stop_loss_type.value,
            "distance": self.distance,
            "distance_percentage": self.distance_percentage,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }


class StopLossCalculator:
    """
    Calculates stop loss levels using multiple methods.
    """

    # ATR multiplier for stop loss
    ATR_MULTIPLIER: float = 2.0

    # Structure buffer (percentage beyond S/R level)
    STRUCTURE_BUFFER_PCT: float = 0.5

    # Volatility multiplier
    VOLATILITY_MULTIPLIER: float = 1.5

    # Default percentage stop
    DEFAULT_PERCENTAGE_STOP: float = 2.0

    def __init__(self):
        pass

    def calculate_atr_stop(
        self,
        entry_price: float,
        atr: float,
        action: str,
        multiplier: Optional[float] = None,
    ) -> StopLossResult:
        """
        Calculate ATR-based stop loss.

        Args:
            entry_price: Entry price
            atr: Current ATR value
            action: 'BUY' or 'SELL'
            multiplier: ATR multiplier (default 2.0)

        Returns:
            StopLossResult with stop loss level
        """
        mult = multiplier or self.ATR_MULTIPLIER

        if action == "BUY":
            stop_loss = entry_price - (atr * mult)
        else:
            stop_loss = entry_price + (atr * mult)

        distance = abs(entry_price - stop_loss)
        distance_pct = (distance / entry_price) * 100 if entry_price > 0 else 0

        return StopLossResult(
            stop_loss=round(stop_loss, 8),
            stop_loss_type=StopLossType.ATR,
            distance=distance,
            distance_percentage=distance_pct,
            reasoning=f"ATR stop: {mult}x ATR ({atr:.4f})",
            metadata={"atr": atr, "multiplier": mult},
        )

    def calculate_structure_stop(
        self,
        entry_price: float,
        support_levels: List[float],
        resistance_levels: List[float],
        action: str,
        buffer_pct: Optional[float] = None,
    ) -> StopLossResult:
        """
        Calculate structure-based stop loss.

        Places stop loss beyond the nearest support (for buys) or
        resistance (for sells).

        Args:
            entry_price: Entry price
            support_levels: List of support prices
            resistance_levels: List of resistance prices
            action: 'BUY' or 'SELL'
            buffer_pct: Buffer percentage beyond S/R level

        Returns:
            StopLossResult with stop loss level
        """
        buffer_pct = buffer_pct or self.STRUCTURE_BUFFER_PCT

        if action == "BUY":
            # Find nearest support below entry
            valid_supports = [s for s in support_levels if s < entry_price]
            if not valid_supports:
                # Fallback to ATR stop
                return self.calculate_atr_stop(entry_price, entry_price * 0.02, action)

            nearest_support = max(valid_supports)
            buffer = nearest_support * (buffer_pct / 100)
            stop_loss = nearest_support - buffer
            reasoning = f"Structure stop: below support {nearest_support:.4f} with {buffer_pct}% buffer"
        else:
            # Find nearest resistance above entry
            valid_resistances = [r for r in resistance_levels if r > entry_price]
            if not valid_resistances:
                return self.calculate_atr_stop(entry_price, entry_price * 0.02, action)

            nearest_resistance = min(valid_resistances)
            buffer = nearest_resistance * (buffer_pct / 100)
            stop_loss = nearest_resistance + buffer
            reasoning = f"Structure stop: above resistance {nearest_resistance:.4f} with {buffer_pct}% buffer"

        distance = abs(entry_price - stop_loss)
        distance_pct = (distance / entry_price) * 100 if entry_price > 0 else 0

        return StopLossResult(
            stop_loss=round(stop_loss, 8),
            stop_loss_type=StopLossType.STRUCTURE,
            distance=distance,
            distance_percentage=distance_pct,
            reasoning=reasoning,
            metadata={"buffer_pct": buffer_pct},
        )

    def calculate_volatility_stop(
        self,
        entry_price: float,
        atr: float,
        bb_width: float,
        action: str,
        multiplier: Optional[float] = None,
    ) -> StopLossResult:
        """
        Calculate volatility-adjusted stop loss.

        Adjusts stop distance based on current volatility regime.

        Args:
            entry_price: Entry price
            atr: Current ATR value
            bb_width: Bollinger Band width
            action: 'BUY' or 'SELL'
            multiplier: Base multiplier

        Returns:
            StopLossResult with stop loss level
        """
        mult = multiplier or self.VOLATILITY_MULTIPLIER

        # Adjust multiplier based on volatility
        if bb_width > 10:  # High volatility
            adjusted_mult = mult * 1.5
        elif bb_width < 3:  # Low volatility
            adjusted_mult = mult * 0.7
        else:
            adjusted_mult = mult

        if action == "BUY":
            stop_loss = entry_price - (atr * adjusted_mult)
        else:
            stop_loss = entry_price + (atr * adjusted_mult)

        distance = abs(entry_price - stop_loss)
        distance_pct = (distance / entry_price) * 100 if entry_price > 0 else 0

        return StopLossResult(
            stop_loss=round(stop_loss, 8),
            stop_loss_type=StopLossType.VOLATILITY,
            distance=distance,
            distance_percentage=distance_pct,
            reasoning=f"Volatility stop: {adjusted_mult:.2f}x ATR (BB width: {bb_width:.2f}%)",
            metadata={"atr": atr, "multiplier": adjusted_mult, "bb_width": bb_width},
        )

    def calculate_percentage_stop(
        self,
        entry_price: float,
        action: str,
        percentage: Optional[float] = None,
    ) -> StopLossResult:
        """
        Calculate percentage-based stop loss.

        Args:
            entry_price: Entry price
            action: 'BUY' or 'SELL'
            percentage: Stop loss percentage (default 2%)

        Returns:
            StopLossResult with stop loss level
        """
        pct = percentage or self.DEFAULT_PERCENTAGE_STOP

        if action == "BUY":
            stop_loss = entry_price * (1 - pct / 100)
        else:
            stop_loss = entry_price * (1 + pct / 100)

        distance = abs(entry_price - stop_loss)
        distance_pct = pct

        return StopLossResult(
            stop_loss=round(stop_loss, 8),
            stop_loss_type=StopLossType.PERCENTAGE,
            distance=distance,
            distance_percentage=distance_pct,
            reasoning=f"Percentage stop: {pct}%",
            metadata={"percentage": pct},
        )

    def calculate_chandelier_exit(
        self,
        df: pd.DataFrame,
        action: str,
        atr_period: int = 22,
        multiplier: float = 3.0,
    ) -> StopLossResult:
        """
        Calculate Chandelier Exit stop loss.

        Trailing stop based on the highest high (for longs) or
        lowest low (for shorts) minus/plus a multiple of ATR.

        Args:
            df: OHLCV DataFrame
            action: 'BUY' or 'SELL'
            atr_period: ATR lookback period
            multiplier: ATR multiplier

        Returns:
            StopLossResult with stop loss level
        """
        if len(df) < atr_period:
            return self.calculate_percentage_stop(df["close"].iloc[-1], action)

        # Calculate ATR
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values

        tr = np.zeros(len(high))
        tr[0] = high[0] - low[0]
        for i in range(1, len(high)):
            tr[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))

        atr = np.mean(tr[-atr_period:])

        if action == "BUY":
            highest_high = df["high"].iloc[-atr_period:].max()
            stop_loss = highest_high - (atr * multiplier)
        else:
            lowest_low = df["low"].iloc[-atr_period:].min()
            stop_loss = lowest_low + (atr * multiplier)

        entry_price = df["close"].iloc[-1]
        distance = abs(entry_price - stop_loss)
        distance_pct = (distance / entry_price) * 100 if entry_price > 0 else 0

        return StopLossResult(
            stop_loss=round(stop_loss, 8),
            stop_loss_type=StopLossType.CHANDLE_EXIT,
            distance=distance,
            distance_percentage=distance_pct,
            reasoning=f"Chandelier Exit: {multiplier}x ATR from extreme",
            metadata={"atr": atr, "multiplier": multiplier, "atr_period": atr_period},
        )

    def get_optimal_stop(
        self,
        entry_price: float,
        atr: float,
        support_levels: List[float],
        resistance_levels: List[float],
        bb_width: float,
        action: str,
    ) -> StopLossResult:
        """
        Get the optimal stop loss by selecting the tightest valid stop.

        Compares ATR, structure, and volatility stops and selects
        the one closest to entry price (tightest) that is still valid.

        Args:
            entry_price: Entry price
            atr: Current ATR
            support_levels: Support levels
            resistance_levels: Resistance levels
            bb_width: Bollinger Band width
            action: 'BUY' or 'SELL'

        Returns:
            StopLossResult with optimal stop loss
        """
        stops = []

        # ATR stop
        stops.append(self.calculate_atr_stop(entry_price, atr, action))

        # Structure stop
        stops.append(self.calculate_structure_stop(entry_price, support_levels, resistance_levels, action))

        # Volatility stop
        stops.append(self.calculate_volatility_stop(entry_price, atr, bb_width, action))

        # Filter valid stops (must be on correct side of entry)
        if action == "BUY":
            valid_stops = [s for s in stops if s.stop_loss < entry_price]
        else:
            valid_stops = [s for s in stops if s.stop_loss > entry_price]

        if not valid_stops:
            # Fallback to percentage stop
            return self.calculate_percentage_stop(entry_price, action)

        # Select the tightest stop (closest to entry)
        optimal = min(valid_stops, key=lambda s: s.distance)
        optimal.reasoning = f"Optimal stop (tightest): {optimal.reasoning}"

        return optimal
