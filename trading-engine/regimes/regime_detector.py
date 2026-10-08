"""
Market Regime Detection
=======================

Classifies the current market regime based on multiple factors:
- Trend direction and strength
- Volatility levels
- Price structure
- Momentum conditions

Regimes: TREND_UP, TREND_DOWN, RANGE, BREAKOUT, BREAKDOWN,
         HIGH_VOLATILITY, LOW_VOLATILITY, UNCERTAIN
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime classifications."""
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class RegimeResult:
    """Container for regime detection results."""
    regime: MarketRegime
    confidence: float  # 0-1
    factors: Dict[str, float] = None
    description: str = ""

    def __post_init__(self):
        if self.factors is None:
            self.factors = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "regime": self.regime.value,
            "confidence": self.confidence,
            "factors": self.factors,
            "description": self.description,
        }


class RegimeDetector:
    """
    Market regime classification engine.

    Analyzes multiple market dimensions to classify the current regime
    and provide confidence scoring.
    """

    # Thresholds for regime classification
    ADX_TREND_THRESHOLD: float = 25.0
    ADX_STRONG_TREND: float = 40.0
    VOLATILITY_HIGH_THRESHOLD: float = 0.8  # Annualized HV
    VOLATILITY_LOW_THRESHOLD: float = 0.3
    RANGE_BB_WIDTH: float = 3.0
    BREAKOUT_CONFIRMATION: float = 0.5  # Percentage beyond level

    def __init__(self):
        self._regime_history: List[MarketRegime] = []
        self._max_history = 100

    def detect_regime(
        self,
        df: pd.DataFrame,
        trend_result=None,
        momentum_result=None,
        volatility_result=None,
        structure_result=None,
    ) -> RegimeResult:
        """
        Detect the current market regime.

        Args:
            df: OHLCV DataFrame
            trend_result: Pre-calculated trend indicators
            momentum_result: Pre-calculated momentum indicators
            volatility_result: Pre-calculated volatility indicators
            structure_result: Pre-calculated structure indicators

        Returns:
            RegimeResult with regime classification and confidence
        """
        if df.empty or len(df) < 20:
            return RegimeResult(
                regime=MarketRegime.UNCERTAIN,
                confidence=0.0,
                description="Insufficient data for regime detection",
            )

        factors = {}

        # Calculate factors if not provided
        if trend_result is None:
            from trading_engine.indicators.trend import TrendIndicators
            trend_result = TrendIndicators().calculate_all(df)

        if momentum_result is None:
            from trading_engine.indicators.momentum import MomentumIndicators
            momentum_result = MomentumIndicators().calculate_all(df)

        if volatility_result is None:
            from trading_engine.indicators.volatility import VolatilityIndicators
            volatility_result = VolatilityIndicators().calculate_all(df)

        if structure_result is None:
            from trading_engine.indicators.structure import StructureIndicators
            structure_result = StructureIndicators().calculate_all(df)

        # Extract key metrics
        adx = trend_result.adx or 0
        trend_direction = trend_result.trend_direction
        trend_strength = trend_result.trend_strength

        bb_width = volatility_result.bb_width or 0
        hv_annualized = volatility_result.hv_annualized or 0
        volatility_regime = volatility_result.volatility_regime

        is_consolidating = structure_result.is_consolidating
        consolidation_range = structure_result.consolidation_range
        breakout_level = structure_result.breakout_level
        breakdown_level = structure_result.breakdown_level

        current_price = df["close"].iloc[-1]

        # Calculate factor scores
        factors["adx"] = adx / 100  # Normalize to 0-1
        factors["trend_bullish"] = 1.0 if trend_direction == "bullish" else 0.0
        factors["trend_bearish"] = 1.0 if trend_direction == "bearish" else 0.0
        factors["bb_width"] = min(bb_width / 10, 1.0)  # Normalize
        factors["hv"] = min(hv_annualized / 2.0, 1.0)  # Normalize
        factors["consolidation"] = 1.0 if is_consolidating else 0.0

        # Regime classification logic
        regime, confidence, description = self._classify_regime(
            adx=adx,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            bb_width=bb_width,
            hv_annualized=hv_annualized,
            volatility_regime=volatility_regime,
            is_consolidating=is_consolidating,
            consolidation_range=consolidation_range,
            breakout_level=breakout_level,
            breakdown_level=breakdown_level,
            current_price=current_price,
            df=df,
        )

        # Update history
        self._regime_history.append(regime)
        if len(self._regime_history) > self._max_history:
            self._regime_history = self._regime_history[-self._max_history:]

        return RegimeResult(
            regime=regime,
            confidence=confidence,
            factors=factors,
            description=description,
        )

    def _classify_regime(
        self,
        adx: float,
        trend_direction: str,
        trend_strength: str,
        bb_width: float,
        hv_annualized: float,
        volatility_regime: str,
        is_consolidating: bool,
        consolidation_range: Optional[tuple],
        breakout_level: Optional[float],
        breakdown_level: Optional[float],
        current_price: float,
        df: pd.DataFrame,
    ) -> tuple:
        """Classify the market regime based on all factors."""

        # Check for breakout/breakdown first (highest priority)
        if breakout_level and is_consolidating:
            threshold = breakout_level * (self.BREAKOUT_CONFIRMATION / 100)
            if current_price > breakout_level + threshold:
                return (
                    MarketRegime.BREAKOUT,
                    0.8,
                    f"Price broke above resistance at {breakout_level:.4f}",
                )

        if breakdown_level and is_consolidating:
            threshold = breakdown_level * (self.BREAKOUT_CONFIRMATION / 100)
            if current_price < breakdown_level - threshold:
                return (
                    MarketRegime.BREAKDOWN,
                    0.8,
                    f"Price broke below support at {breakdown_level:.4f}",
                )

        # Check for high/low volatility
        if hv_annualized > self.VOLATILITY_HIGH_THRESHOLD or volatility_regime == "high":
            return (
                MarketRegime.HIGH_VOLATILITY,
                0.7,
                f"High volatility environment (HV: {hv_annualized:.2f})",
            )

        if hv_annualized < self.VOLATILITY_LOW_THRESHOLD or volatility_regime == "low":
            return (
                MarketRegime.LOW_VOLATILITY,
                0.7,
                f"Low volatility environment (HV: {hv_annualized:.2f})",
            )

        # Check for trending regimes
        if adx >= self.ADX_TREND_THRESHOLD:
            if trend_direction == "bullish":
                confidence = min(1.0, adx / 50) * (1.2 if trend_strength in ["strong", "very_strong"] else 1.0)
                return (
                    MarketRegime.TREND_UP,
                    min(1.0, confidence),
                    f"Strong uptrend (ADX: {adx:.1f})",
                )
            elif trend_direction == "bearish":
                confidence = min(1.0, adx / 50) * (1.2 if trend_strength in ["strong", "very_strong"] else 1.0)
                return (
                    MarketRegime.TREND_DOWN,
                    min(1.0, confidence),
                    f"Strong downtrend (ADX: {adx:.1f})",
                )

        # Check for range regime
        if is_consolidating or bb_width < self.RANGE_BB_WIDTH:
            return (
                MarketRegime.RANGE,
                0.6,
                f"Range-bound market (BB Width: {bb_width:.2f}%)",
            )

        # Default to uncertain
        return (
            MarketRegime.UNCERTAIN,
            0.3,
            "Market regime unclear - mixed signals",
        )

    def get_regime_stability(self) -> float:
        """
        Calculate regime stability based on recent history.

        Returns:
            Stability score (0-1), higher means more stable
        """
        if len(self._regime_history) < 5:
            return 0.0

        recent = self._regime_history[-10:]
        if not recent:
            return 0.0

        # Count regime changes
        changes = sum(1 for i in range(1, len(recent)) if recent[i] != recent[i - 1])
        stability = 1.0 - (changes / len(recent))
        return stability

    def get_dominant_regime(self, lookback: int = 20) -> Optional[MarketRegime]:
        """
        Get the most common regime over the lookback period.

        Args:
            lookback: Number of recent regimes to consider

        Returns:
            Most common regime or None
        """
        if not self._regime_history:
            return None

        recent = self._regime_history[-lookback:]
        regime_counts = {}
        for regime in recent:
            regime_counts[regime] = regime_counts.get(regime, 0) + 1

        return max(regime_counts, key=regime_counts.get)

    def reset(self) -> None:
        """Reset regime history."""
        self._regime_history.clear()
