"""
Signal Generation Module
========================

Generates trading signals with comprehensive metadata including:
- Unique signal ID
- Symbol and timestamp
- Signal direction (BUY/SELL/HOLD)
- Entry, stop loss, and take profit levels
- Risk/reward ratio
- Confidence score
- Market regime context
- Strategy attribution
- Model version tracking
- Reasoning summary
- Signal status tracking
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from trading_engine.indicators.trend import TrendIndicators
from trading_engine.indicators.momentum import MomentumIndicators
from trading_engine.indicators.volatility import VolatilityIndicators
from trading_engine.indicators.structure import StructureIndicators
from trading_engine.regimes.regime_detector import RegimeDetector, MarketRegime, RegimeResult
from trading_engine.strategies.trend_following import TrendFollowingStrategy
from trading_engine.strategies.breakout import BreakoutStrategy
from trading_engine.strategies.pullback import PullbackStrategy
from trading_engine.strategies.mean_reversion import MeanReversionStrategy

logger = logging.getLogger(__name__)


class SignalStatus(Enum):
    """Signal lifecycle status."""
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass
class Signal:
    """
    Complete trading signal with all metadata.
    """
    signal_id: str
    symbol: str
    timestamp: datetime
    timeframe: str
    signal: str  # BUY, SELL, HOLD
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward: Optional[float] = None
    confidence: float = 0.0
    market_regime: Optional[str] = None
    strategy: Optional[str] = None
    model_version: str = "1.0.0"
    reasoning_summary: str = ""
    status: SignalStatus = SignalStatus.GENERATED
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "timeframe": self.timeframe,
            "signal": self.signal,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_reward": self.risk_reward,
            "confidence": self.confidence,
            "market_regime": self.market_regime,
            "strategy": self.strategy,
            "model_version": self.model_version,
            "reasoning_summary": self.reasoning_summary,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update_status(self, status: SignalStatus) -> None:
        """Update signal status."""
        self.status = status
        self.updated_at = datetime.now(timezone.utc)


class SignalGenerator:
    """
    Generates trading signals by combining multiple strategies
    and market analysis.
    """

    MODEL_VERSION: str = "1.0.0"
    MIN_CONFIDENCE_THRESHOLD: float = 0.5
    DEFAULT_TIMEFRAME: str = "1h"

    def __init__(self, timeframe: str = "1h"):
        self.timeframe = timeframe
        self.trend_indicators = TrendIndicators()
        self.momentum_indicators = MomentumIndicators()
        self.volatility_indicators = VolatilityIndicators()
        self.structure_indicators = StructureIndicators()
        self.regime_detector = RegimeDetector()

        # Initialize strategies
        self.strategies = {
            "trend_following": TrendFollowingStrategy(),
            "breakout": BreakoutStrategy(),
            "pullback": PullbackStrategy(),
            "mean_reversion": MeanReversionStrategy(),
        }

        self._signal_history: List[Signal] = []
        self._max_history = 1000

    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Signal:
        """
        Generate a trading signal for the given symbol and data.

        Args:
            df: OHLCV DataFrame
            symbol: Trading symbol

        Returns:
            Signal with complete metadata
        """
        if df.empty or len(df) < 50:
            return self._create_hold_signal(symbol, "Insufficient data")

        # Detect market regime
        trend = self.trend_indicators.calculate_all(df)
        momentum = self.momentum_indicators.calculate_all(df)
        volatility = self.volatility_indicators.calculate_all(df)
        structure = self.structure_indicators.calculate_all(df)
        regime = self.regime_detector.detect_regime(df, trend, momentum, volatility, structure)

        # Collect signals from all strategies
        strategy_signals = []
        for name, strategy in self.strategies.items():
            try:
                if name == "trend_following":
                    sig = strategy.generate_signal(df, symbol)
                elif name == "breakout":
                    sig = strategy.generate_signal(df, symbol)
                elif name == "pullback":
                    sig = strategy.generate_signal(df, symbol)
                elif name == "mean_reversion":
                    sig = strategy.generate_signal(df, symbol)
                else:
                    continue

                if sig.action != "HOLD" and sig.confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    strategy_signals.append((name, sig))
            except Exception as e:
                logger.error(f"Error in strategy {name}: {e}")

        # Select the best signal
        if strategy_signals:
            # Sort by confidence
            strategy_signals.sort(key=lambda x: x[1].confidence, reverse=True)
            best_strategy, best_signal = strategy_signals[0]

            # Create the final signal
            signal = self._create_signal(
                symbol=symbol,
                timeframe=self.timeframe,
                action=best_signal.action,
                entry_price=best_signal.entry_price,
                stop_loss=best_signal.stop_loss,
                take_profit=best_signal.take_profit,
                risk_reward=best_signal.risk_reward,
                confidence=best_signal.confidence,
                regime=regime,
                strategy=best_strategy,
                reasoning=best_signal.reasoning,
                metadata=best_signal.metadata,
            )
        else:
            # No strategy produced a valid signal
            signal = self._create_hold_signal(
                symbol,
                f"No high-confidence signal (regime: {regime.regime.value})",
            )
            signal.market_regime = regime.regime.value
            signal.confidence = regime.confidence

        # Store in history
        self._signal_history.append(signal)
        if len(self._signal_history) > self._max_history:
            self._signal_history = self._signal_history[-self._max_history:]

        return signal

    def _create_signal(
        self,
        symbol: str,
        timeframe: str,
        action: str,
        entry_price: Optional[float],
        stop_loss: Optional[float],
        take_profit: Optional[float],
        risk_reward: Optional[float],
        confidence: float,
        regime: RegimeResult,
        strategy: str,
        reasoning: List[str],
        metadata: Dict[str, Any],
    ) -> Signal:
        """Create a complete signal with all metadata."""

        # Generate unique signal ID
        signal_id = self._generate_signal_id(symbol, action, entry_price)

        # Create reasoning summary
        reasoning_summary = " | ".join(reasoning) if reasoning else "No reasoning provided"

        return Signal(
            signal_id=signal_id,
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            timeframe=timeframe,
            signal=action,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward,
            confidence=confidence,
            market_regime=regime.regime.value,
            strategy=strategy,
            model_version=self.MODEL_VERSION,
            reasoning_summary=reasoning_summary,
            status=SignalStatus.GENERATED,
            metadata={
                **metadata,
                "regime_confidence": regime.confidence,
                "regime_factors": regime.factors,
                "regime_description": regime.description,
            },
        )

    def _create_hold_signal(self, symbol: str, reason: str) -> Signal:
        """Create a HOLD signal."""
        return Signal(
            signal_id=self._generate_signal_id(symbol, "HOLD", None),
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            timeframe=self.timeframe,
            signal="HOLD",
            confidence=0.0,
            reasoning_summary=reason,
            status=SignalStatus.GENERATED,
        )

    def _generate_signal_id(self, symbol: str, action: str, price: Optional[float]) -> str:
        """Generate a unique signal ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        data = f"{symbol}_{action}_{price}_{timestamp}_{uuid.uuid4().hex[:8]}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_signal_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
    ) -> List[Signal]:
        """
        Get signal history, optionally filtered by symbol.

        Args:
            symbol: Filter by symbol
            limit: Maximum number of signals to return

        Returns:
            List of signals
        """
        signals = self._signal_history
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
        return signals[-limit:]

    def get_signal_by_id(self, signal_id: str) -> Optional[Signal]:
        """Get a signal by its ID."""
        for signal in self._signal_history:
            if signal.signal_id == signal_id:
                return signal
        return None

    def get_signal_stats(self) -> Dict[str, Any]:
        """Get statistics about generated signals."""
        if not self._signal_history:
            return {}

        total = len(self._signal_history)
        buy_signals = sum(1 for s in self._signal_history if s.signal == "BUY")
        sell_signals = sum(1 for s in self._signal_history if s.signal == "SELL")
        hold_signals = sum(1 for s in self._signal_history if s.signal == "HOLD")

        avg_confidence = np.mean([s.confidence for s in self._signal_history]) if self._signal_history else 0

        return {
            "total_signals": total,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "hold_signals": hold_signals,
            "buy_percentage": (buy_signals / total * 100) if total > 0 else 0,
            "sell_percentage": (sell_signals / total * 100) if total > 0 else 0,
            "hold_percentage": (hold_signals / total * 100) if total > 0 else 0,
            "average_confidence": float(avg_confidence),
        }

    def reset(self) -> None:
        """Reset signal generator state."""
        self._signal_history.clear()
        self.trend_indicators.reset()
        self.momentum_indicators.reset()
        self.volatility_indicators.reset()
        self.structure_indicators.reset()
        self.regime_detector.reset()
        for strategy in self.strategies.values():
            strategy.reset()
