"""
Model Monitoring Module
=======================
Tracks model performance and health in production.

Monitors:
- Prediction distribution shifts
- Confidence score changes
- Feature drift (PSI - Population Stability Index)
- Performance deterioration
- Live signal outcomes
- Strategy performance

Actions on deterioration:
- Reduce trust level
- Raise warnings
- Optionally disable model
"""

from __future__ import annotations

import logging
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

from ml_engine.registry.model_registry import ModelRegistry, ModelStatus

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels for model reliability."""

    FULL = "full"           # Fully trusted
    REDUCED = "reduced"     # Reduced trust - increased scrutiny
    LIMITED = "limited"     # Limited trust - significant concerns
    UNTRUSTED = "untrusted" # Untrusted - should not be used

    def __str__(self) -> str:
        return self.value


@dataclass
class MonitoringEvent:
    """A monitoring event/alert."""

    event_id: str
    timestamp: str
    model_id: str
    event_type: str
    severity: str  # "info", "warning", "critical"
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionRecord:
    """Record of a single prediction for tracking."""

    timestamp: str
    model_id: str
    signal: str
    confidence: float
    buy_probability: float
    sell_probability: float
    hold_probability: float
    regime: str
    features_hash: str = ""


@dataclass
class SignalOutcome:
    """Outcome of a trading signal."""

    signal_id: str
    timestamp: str
    model_id: str
    signal: str
    entry_price: float
    exit_price: float | None = None
    outcome: str = ""  # "win", "loss", "open"
    return_pct: float = 0.0
    holding_periods: int = 0


class ModelMonitor:
    """Monitors model performance and health in production.

    Tracks predictions, outcomes, and feature distributions to detect
    performance deterioration and trigger appropriate responses.
    """

    # Thresholds
    PSI_THRESHOLD_WARNING = 0.2
    PSI_THRESHOLD_CRITICAL = 0.3
    CONFIDENCE_DROP_THRESHOLD = 0.15
    ACCURACY_DROP_THRESHOLD = 0.10
    PREDICTION_DRIFT_THRESHOLD = 0.3

    # Window sizes
    DEFAULT_WINDOW_SIZE = 100
    MIN_SAMPLES_FOR_DRIFT = 30

    def __init__(
        self,
        registry: ModelRegistry,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the ModelMonitor.

        Args:
            registry: ModelRegistry instance.
            config: Configuration dictionary with optional keys:
                - window_size: Number of predictions to track (default: 100)
                - drift_check_interval: Checks between drift calculations (default: 50)
                - auto_disable: Auto-disable on critical deterioration (default: False)
                - alert_callback: Function to call on alerts
        """
        self.registry = registry
        self.config = config or {}

        self.window_size = self.config.get("window_size", self.DEFAULT_WINDOW_SIZE)
        self.drift_check_interval = self.config.get("drift_check_interval", 50)
        self.auto_disable = self.config.get("auto_disable", False)
        self.alert_callback = self.config.get("alert_callback")

        # State
        self._is_active = False
        self._trust_levels: dict[str, TrustLevel] = {}
        self._prediction_history: dict[str, deque[PredictionRecord]] = {}
        self._signal_outcomes: dict[str, list[SignalOutcome]] = {}
        self._events: list[MonitoringEvent] = []
        self._baseline_distributions: dict[str, dict[str, np.ndarray]] = {}
        self._baseline_confidence: dict[str, float] = {}
        self._prediction_counts: dict[str, int] = {}

        logger.info("Model monitor initialized")

    @property
    def is_active(self) -> bool:
        """Check if monitoring is active."""
        return self._is_active

    def start_monitoring(self, model_id: str) -> None:
        """Start monitoring a model.

        Args:
            model_id: ID of the model to monitor.
        """
        entry = self.registry.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")

        self._prediction_history[model_id] = deque(maxlen=self.window_size)
        self._signal_outcomes[model_id] = []
        self._trust_levels[model_id] = TrustLevel.FULL
        self._prediction_counts[model_id] = 0

        # Set baseline confidence from training metrics
        self._baseline_confidence[model_id] = entry.metrics.get("accuracy", 0.5)

        self._is_active = True
        logger.info(f"Started monitoring model: {model_id}")

    def stop_monitoring(self, model_id: str) -> None:
        """Stop monitoring a model.

        Args:
            model_id: ID of the model to stop monitoring.
        """
        self._prediction_history.pop(model_id, None)
        self._signal_outcomes.pop(model_id, None)
        self._trust_levels.pop(model_id, None)
        self._prediction_counts.pop(model_id, None)

        if not self._prediction_history:
            self._is_active = False

        logger.info(f"Stopped monitoring model: {model_id}")

    def record_prediction(self, model_id: str, prediction: dict[str, Any]) -> None:
        """Record a prediction for monitoring.

        Args:
            model_id: ID of the model that made the prediction.
            prediction: Prediction dictionary from Predictor.
        """
        if model_id not in self._prediction_history:
            logger.warning(f"Model '{model_id}' is not being monitored. Call start_monitoring first.")
            return

        record = PredictionRecord(
            timestamp=prediction.get("timestamp", datetime.now(timezone.utc).isoformat()),
            model_id=model_id,
            signal=prediction.get("signal", "HOLD"),
            confidence=prediction.get("confidence_score", 0.0),
            buy_probability=prediction.get("probabilities", {}).get("buy", 0.0),
            sell_probability=prediction.get("probabilities", {}).get("sell", 0.0),
            hold_probability=prediction.get("probabilities", {}).get("hold", 0.0),
            regime=prediction.get("regime", "UNKNOWN"),
        )

        self._prediction_history[model_id].append(record)
        self._prediction_counts[model_id] = self._prediction_counts.get(model_id, 0) + 1

        # Check for issues
        self._check_prediction_distribution(model_id)
        self._check_confidence_drift(model_id)

        # Periodic drift check
        if self._prediction_counts[model_id] % self.drift_check_interval == 0:
            self._check_feature_drift(model_id)

    def record_signal_outcome(
        self,
        model_id: str,
        signal: str,
        entry_price: float,
        exit_price: float | None = None,
        holding_periods: int = 0,
    ) -> None:
        """Record the outcome of a trading signal.

        Args:
            model_id: ID of the model that generated the signal.
            signal: The signal that was generated (BUY/SELL/HOLD).
            entry_price: Price at signal generation.
            exit_price: Price at signal closure (None if still open).
            holding_periods: Number of periods the position was held.
        """
        if model_id not in self._signal_outcomes:
            return

        outcome = "open"
        return_pct = 0.0

        if exit_price is not None:
            if signal == "BUY":
                return_pct = ((exit_price - entry_price) / entry_price) * 100
            elif signal == "SELL":
                return_pct = ((entry_price - exit_price) / entry_price) * 100

            outcome = "win" if return_pct > 0 else "loss"

        signal_outcome = SignalOutcome(
            signal_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_id=model_id,
            signal=signal,
            entry_price=entry_price,
            exit_price=exit_price,
            outcome=outcome,
            return_pct=return_pct,
            holding_periods=holding_periods,
        )

        self._signal_outcomes[model_id].append(signal_outcome)

        # Check performance
        self._check_performance_deterioration(model_id)

    def set_baseline_distribution(
        self, model_id: str, feature_name: str, distribution: np.ndarray
    ) -> None:
        """Set the baseline distribution for a feature.

        Args:
            model_id: ID of the model.
            feature_name: Name of the feature.
            distribution: Baseline distribution values.
        """
        if model_id not in self._baseline_distributions:
            self._baseline_distributions[model_id] = {}

        self._baseline_distributions[model_id][feature_name] = distribution

    def get_trust_level(self, model_id: str) -> TrustLevel:
        """Get the current trust level for a model."""
        return self._trust_levels.get(model_id, TrustLevel.FULL)

    def get_events(
        self,
        model_id: str | None = None,
        severity: str | None = None,
        unacknowledged_only: bool = False,
    ) -> list[MonitoringEvent]:
        """Get monitoring events with optional filtering."""
        events = self._events

        if model_id is not None:
            events = [e for e in events if e.model_id == model_id]
        if severity is not None:
            events = [e for e in events if e.severity == severity]
        if unacknowledged_only:
            events = [e for e in events if not e.acknowledged]

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    def acknowledge_event(self, event_id: str) -> None:
        """Acknowledge a monitoring event."""
        for event in self._events:
            if event.event_id == event_id:
                event.acknowledged = True
                logger.info(f"Event acknowledged: {event_id}")
                return

    def get_performance_summary(self, model_id: str) -> dict[str, Any]:
        """Get performance summary for a model.

        Args:
            model_id: ID of the model.

        Returns:
            Performance summary dictionary.
        """
        entry = self.registry.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")

        predictions = list(self._prediction_history.get(model_id, []))
        outcomes = self._signal_outcomes.get(model_id, [])

        # Prediction statistics
        if predictions:
            signals = [p.signal for p in predictions]
            confidences = [p.confidence for p in predictions]
            signal_distribution = {
                signal: signals.count(signal) / len(signals)
                for signal in set(signals)
            }
            avg_confidence = np.mean(confidences)
            confidence_trend = self._calculate_trend(confidences)
        else:
            signal_distribution = {}
            avg_confidence = 0.0
            confidence_trend = "insufficient_data"

        # Outcome statistics
        closed_outcomes = [o for o in outcomes if o.outcome != "open"]
        if closed_outcomes:
            wins = [o for o in closed_outcomes if o.outcome == "win"]
            losses = [o for o in closed_outcomes if o.outcome == "loss"]
            win_rate = len(wins) / len(closed_outcomes)
            avg_return = np.mean([o.return_pct for o in closed_outcomes])
            total_return = sum(o.return_pct for o in closed_outcomes)
        else:
            win_rate = 0.0
            avg_return = 0.0
            total_return = 0.0

        # Training vs live comparison
        training_accuracy = entry.metrics.get("accuracy", 0.0)
        live_win_rate = win_rate if closed_outcomes else 0.0
        performance_gap = training_accuracy - live_win_rate

        return {
            "model_id": model_id,
            "name": entry.name,
            "version": entry.version,
            "status": entry.status.value,
            "trust_level": self._trust_levels.get(model_id, TrustLevel.FULL).value,
            "monitoring_active": model_id in self._prediction_history,
            "total_predictions": len(predictions),
            "total_signals": len(outcomes),
            "closed_signals": len(closed_outcomes),
            "signal_distribution": signal_distribution,
            "average_confidence": round(avg_confidence, 4),
            "confidence_trend": confidence_trend,
            "win_rate": round(win_rate, 4),
            "average_return_pct": round(avg_return, 4),
            "total_return_pct": round(total_return, 4),
            "training_accuracy": round(training_accuracy, 4),
            "performance_gap": round(performance_gap, 4),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    def get_strategy_performance(self, model_id: str) -> dict[str, Any]:
        """Get strategy-level performance metrics.

        Args:
            model_id: ID of the model.

        Returns:
            Strategy performance dictionary.
        """
        entry = self.registry.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")

        outcomes = self._signal_outcomes.get(model_id, [])
        closed = [o for o in outcomes if o.outcome != "open"]

        if not closed:
            return {
                "model_id": model_id,
                "strategy": entry.strategy,
                "total_trades": 0,
                "message": "No closed trades yet",
            }

        # Calculate strategy metrics
        returns = [o.return_pct for o in closed]
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]

        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1e-10
        profit_factor = gross_profit / gross_loss

        # Sharpe-like ratio (simplified)
        if len(returns) > 1:
            sharpe = np.mean(returns) / (np.std(returns) + 1e-10) * np.sqrt(252)
        else:
            sharpe = 0.0

        # Max drawdown
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0.0

        # Average holding period
        avg_holding = np.mean([o.holding_periods for o in closed])

        return {
            "model_id": model_id,
            "strategy": entry.strategy,
            "total_trades": len(closed),
            "win_rate": round(len(wins) / len(closed), 4),
            "profit_factor": round(profit_factor, 4),
            "sharpe_ratio": round(sharpe, 4),
            "max_drawdown_pct": round(max_drawdown, 4),
            "average_return_pct": round(np.mean(returns), 4),
            "total_return_pct": round(sum(returns), 4),
            "average_holding_periods": round(avg_holding, 1),
            "largest_win_pct": round(max(returns), 4) if returns else 0,
            "largest_loss_pct": round(min(returns), 4) if returns else 0,
        }

    def _check_prediction_distribution(self, model_id: str) -> None:
        """Check if prediction distribution has shifted significantly."""
        predictions = list(self._prediction_history.get(model_id, []))
        if len(predictions) < self.MIN_SAMPLES_FOR_DRIFT:
            return

        # Calculate current signal distribution
        signals = [p.signal for p in predictions]
        current_dist = {
            signal: signals.count(signal) / len(signals)
            for signal in set(signals)
        }

        # Compare with expected distribution (from training)
        entry = self.registry.get(model_id)
        if entry is None:
            return

        # If HOLD probability is extremely high, model may be stale
        hold_pct = current_dist.get("HOLD", 0)
        if hold_pct > 0.9:
            self._raise_event(
                model_id=model_id,
                event_type="prediction_distribution",
                severity="warning",
                message=f"Excessive HOLD signals: {hold_pct:.1%} of recent predictions",
                details={"hold_percentage": hold_pct, "distribution": current_dist},
            )

    def _check_confidence_drift(self, model_id: str) -> None:
        """Check if confidence scores have dropped significantly."""
        predictions = list(self._prediction_history.get(model_id, []))
        if len(predictions) < self.MIN_SAMPLES_FOR_DRIFT:
            return

        recent_confidences = [p.confidence for p in predictions[-self.MIN_SAMPLES_FOR_DRIFT:]]
        avg_recent_confidence = np.mean(recent_confidences)
        baseline = self._baseline_confidence.get(model_id, 0.5)

        confidence_drop = baseline - avg_recent_confidence

        if confidence_drop > self.CONFIDENCE_DROP_THRESHOLD:
            self._reduce_trust(model_id, TrustLevel.REDUCED)
            self._raise_event(
                model_id=model_id,
                event_type="confidence_drift",
                severity="warning",
                message=(
                    f"Confidence dropped by {confidence_drop:.2f} "
                    f"(baseline: {baseline:.2f}, current: {avg_recent_confidence:.2f})"
                ),
                details={
                    "baseline_confidence": baseline,
                    "current_confidence": avg_recent_confidence,
                    "drop": confidence_drop,
                },
            )

    def _check_feature_drift(self, model_id: str) -> None:
        """Check for feature drift using PSI (Population Stability Index)."""
        # This would compare current feature distributions with baseline
        # For now, we check prediction probability distributions
        predictions = list(self._prediction_history.get(model_id, []))
        if len(predictions) < self.MIN_SAMPLES_FOR_DRIFT:
            return

        # Check probability distribution drift
        recent_buy_probs = [p.buy_probability for p in predictions[-self.MIN_SAMPLES_FOR_DRIFT:]]
        recent_sell_probs = [p.sell_probability for p in predictions[-self.MIN_SAMPLES_FOR_DRIFT:]]

        buy_prob_std = np.std(recent_buy_probs)
        sell_prob_std = np.std(recent_sell_probs)

        # If probabilities are extremely concentrated, model may be stuck
        if buy_prob_std < 0.05 and sell_prob_std < 0.05:
            self._raise_event(
                model_id=model_id,
                event_type="feature_drift",
                severity="info",
                message="Prediction probabilities show low variance - possible model stagnation",
                details={
                    "buy_prob_std": buy_prob_std,
                    "sell_prob_std": sell_prob_std,
                },
            )

    def _check_performance_deterioration(self, model_id: str) -> None:
        """Check if model performance has deteriorated based on signal outcomes."""
        outcomes = self._signal_outcomes.get(model_id, [])
        closed = [o for o in outcomes if o.outcome != "open"]

        if len(closed) < 10:
            return

        # Calculate recent win rate (last 10 trades)
        recent = closed[-10:]
        recent_wins = sum(1 for o in recent if o.outcome == "win")
        recent_win_rate = recent_wins / len(recent)

        # Compare with training accuracy
        entry = self.registry.get(model_id)
        if entry is None:
            return

        training_accuracy = entry.metrics.get("accuracy", 0.5)
        performance_gap = training_accuracy - recent_win_rate

        if performance_gap > self.ACCURACY_DROP_THRESHOLD:
            current_trust = self._trust_levels.get(model_id, TrustLevel.FULL)

            if current_trust == TrustLevel.FULL:
                self._reduce_trust(model_id, TrustLevel.REDUCED)
                self._raise_event(
                    model_id=model_id,
                    event_type="performance_deterioration",
                    severity="warning",
                    message=(
                        f"Performance gap detected: training acc {training_accuracy:.2f} "
                        f"vs live win rate {recent_win_rate:.2f}"
                    ),
                    details={
                        "training_accuracy": training_accuracy,
                        "live_win_rate": recent_win_rate,
                        "performance_gap": performance_gap,
                    },
                )
            elif current_trust == TrustLevel.REDUCED and performance_gap > 0.2:
                self._reduce_trust(model_id, TrustLevel.LIMITED)
                self._raise_event(
                    model_id=model_id,
                    event_type="performance_deterioration",
                    severity="critical",
                    message=(
                        f"Severe performance deterioration: gap {performance_gap:.2f}. "
                        "Model trust reduced to LIMITED."
                    ),
                    details={
                        "training_accuracy": training_accuracy,
                        "live_win_rate": recent_win_rate,
                        "performance_gap": performance_gap,
                    },
                )

                # Auto-disable if configured
                if self.auto_disable:
                    self._disable_model(model_id, "Severe performance deterioration")

    def _reduce_trust(self, model_id: str, new_level: TrustLevel) -> None:
        """Reduce the trust level of a model."""
        current = self._trust_levels.get(model_id, TrustLevel.FULL)

        # Only reduce, never automatically increase
        trust_order = [TrustLevel.FULL, TrustLevel.REDUCED, TrustLevel.LIMITED, TrustLevel.UNTRUSTED]
        if trust_order.index(new_level) > trust_order.index(current):
            self._trust_levels[model_id] = new_level
            logger.warning(f"Trust level reduced for '{model_id}': {current.value} -> {new_level.value}")

    def _disable_model(self, model_id: str, reason: str) -> None:
        """Disable a model by retiring it."""
        try:
            self.registry.retire(model_id, reason=reason, updated_by="monitor")
            logger.critical(f"Model '{model_id}' auto-disabled: {reason}")
        except ValueError as e:
            logger.error(f"Failed to disable model '{model_id}': {e}")

    def _raise_event(
        self,
        model_id: str,
        event_type: str,
        severity: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Raise a monitoring event."""
        event = MonitoringEvent(
            event_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_id=model_id,
            event_type=event_type,
            severity=severity,
            message=message,
            details=details or {},
        )

        self._events.append(event)

        # Log based on severity
        if severity == "critical":
            logger.critical(f"[MONITOR] {message}")
        elif severity == "warning":
            logger.warning(f"[MONITOR] {message}")
        else:
            logger.info(f"[MONITOR] {message}")

        # Call alert callback if configured
        if self.alert_callback is not None:
            try:
                self.alert_callback(event)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    @staticmethod
    def _calculate_trend(values: list[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 10:
            return "insufficient_data"

        # Simple linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    @staticmethod
    def _calculate_psi(
        expected: np.ndarray, actual: np.ndarray, buckets: int = 10
    ) -> float:
        """Calculate Population Stability Index (PSI).

        PSI < 0.1: No significant shift
        0.1 <= PSI < 0.2: Moderate shift
        PSI >= 0.2: Significant shift
        """
        # Create breakpoints from expected distribution
        breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
        breakpoints = np.unique(breakpoints)

        if len(breakpoints) < 2:
            return 0.0

        # Calculate proportions
        expected_counts = np.histogram(expected, bins=breakpoints)[0]
        actual_counts = np.histogram(actual, bins=breakpoints)[0]

        # Normalize
        expected_pct = expected_counts / (expected_counts.sum() + 1e-10)
        actual_pct = actual_counts / (actual_counts.sum() + 1e-10)

        # Calculate PSI
        psi = np.sum(
            (actual_pct - expected_pct) * np.log((actual_pct + 1e-10) / (expected_pct + 1e-10))
        )

        return float(psi)
