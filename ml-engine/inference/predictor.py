"""
AI Prediction Module
====================
Generates predictions from trained BARAKA AI models.

Provides:
- BUY/SELL/HOLD probabilities
- Expected return estimate
- Expected volatility estimate
- Market regime classification
- Confidence score (never claims certainty)

All predictions include uncertainty quantification and are designed
to support, not replace, human decision-making.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from ml_engine.features.feature_engineering import FeatureEngineer
from ml_engine.training.trainer import ModelInfo

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Complete prediction result with uncertainty quantification."""

    # Class probabilities
    buy_probability: float
    sell_probability: float
    hold_probability: float

    # Signal
    signal: str  # "BUY", "SELL", "HOLD"
    signal_strength: float  # 0.0 to 1.0

    # Market expectations
    expected_return: float  # Expected return as percentage
    expected_volatility: float  # Expected volatility as percentage

    # Market regime
    regime: str  # "UPTREND", "DOWNTREND", "SIDEWAYS", "VOLATILE"
    regime_confidence: float  # 0.0 to 1.0

    # Confidence
    confidence_score: float  # Overall confidence 0.0 to 1.0
    confidence_level: str  # "LOW", "MEDIUM", "HIGH"

    # Uncertainty
    prediction_entropy: float  # Shannon entropy of prediction
    uncertainty: float  # 0.0 (certain) to 1.0 (uncertain)

    # Metadata
    model_id: str
    model_version: str
    timestamp: str
    features_used: int
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "probabilities": {
                "buy": round(self.buy_probability, 4),
                "sell": round(self.sell_probability, 4),
                "hold": round(self.hold_probability, 4),
            },
            "signal": self.signal,
            "signal_strength": round(self.signal_strength, 4),
            "expected_return_pct": round(self.expected_return, 4),
            "expected_volatility_pct": round(self.expected_volatility, 4),
            "regime": self.regime,
            "regime_confidence": round(self.regime_confidence, 4),
            "confidence_score": round(self.confidence_score, 4),
            "confidence_level": self.confidence_level,
            "prediction_entropy": round(self.prediction_entropy, 4),
            "uncertainty": round(self.uncertainty, 4),
            "model_id": self.model_id,
            "model_version": self.model_version,
            "timestamp": self.timestamp,
            "features_used": self.features_used,
            "warnings": self.warnings,
        }

    def __str__(self) -> str:
        return (
            f"Prediction({self.signal}, "
            f"conf={self.confidence_level}({self.confidence_score:.2f}), "
            f"regime={self.regime})"
        )


class Predictor:
    """Generates predictions from trained models.

    This class wraps a trained model and provides a clean interface
    for generating predictions with full uncertainty quantification.
    """

    # Confidence thresholds
    CONFIDENCE_HIGH = 0.75
    CONFIDENCE_MEDIUM = 0.50
    CONFIDENCE_LOW = 0.25

    # Signal strength thresholds
    STRONG_SIGNAL = 0.70
    MODERATE_SIGNAL = 0.50

    def __init__(
        self,
        model: Any,
        feature_engineer: FeatureEngineer,
        model_info: ModelInfo,
        scaler: Any | None = None,
    ):
        """Initialize the Predictor.

        Args:
            model: Trained ML model with predict_proba method.
            feature_engineer: Fitted FeatureEngineer instance.
            model_info: Model metadata.
            scaler: Optional feature scaler (StandardScaler).
        """
        self.model = model
        self.feature_engineer = feature_engineer
        self.model_info = model_info
        self.scaler = scaler

        # Determine class mapping from model_info
        self._class_map = self._infer_class_mapping()
        self._inverse_class_map = {v: k for k, v in self._class_map.items()}

        logger.info(
            f"Predictor initialized for model: {model_info.name} v{model_info.version}"
        )

    def predict(self, data: pd.DataFrame) -> Prediction:
        """Generate a prediction from market data.

        Args:
            data: DataFrame with OHLCV columns. Must contain enough historical
                  data for feature engineering (at least 50 rows recommended).

        Returns:
            Prediction object with probabilities, signal, and confidence.

        Raises:
            ValueError: If data is insufficient for feature engineering.
        """
        from datetime import datetime, timezone

        warnings: list[str] = []

        # Validate input
        if len(data) < 50:
            warnings.append(
                f"Limited data ({len(data)} rows). Predictions may be less reliable."
            )

        # Engineer features
        features_df = self.feature_engineer.transform(data)

        # Get the latest row (most recent data point)
        latest = features_df.iloc[-1:].copy()

        # Drop any NaN columns in the latest row
        latest = latest.dropna(axis=1)

        # Ensure we have features
        if latest.empty or latest.shape[1] == 0:
            raise ValueError(
                "No valid features could be computed from the provided data. "
                "Ensure sufficient historical data is provided."
            )

        # Align features with model's expected features
        expected_features = self.model_info.features
        available_features = [f for f in expected_features if f in latest.columns]
        missing_features = [f for f in expected_features if f not in latest.columns]

        if missing_features:
            warnings.append(
                f"Missing {len(missing_features)} features: {missing_features[:5]}..."
            )

        if not available_features:
            raise ValueError("None of the expected features are available.")

        X = latest[available_features].values

        # Scale features if scaler is available
        if self.scaler is not None:
            # Create full feature vector with zeros for missing features
            X_full = np.zeros((1, len(expected_features)))
            for i, feat in enumerate(expected_features):
                if feat in available_features:
                    X_full[0, i] = latest[feat].values[0]
            X = self.scaler.transform(X_full)

        # Get prediction probabilities
        try:
            proba = self.model.predict_proba(X)[0]
        except (AttributeError, NotImplementedError):
            # Fallback for models without predict_proba
            pred_class = self.model.predict(X)[0]
            proba = np.zeros(len(self._class_map))
            proba[pred_class] = 1.0
            warnings.append("Model does not provide probability estimates. Using hard predictions.")

        # Map probabilities to BUY/SELL/HOLD
        buy_prob, sell_prob, hold_prob = self._map_probabilities(proba)

        # Determine signal
        signal, signal_strength = self._determine_signal(buy_prob, sell_prob, hold_prob)

        # Calculate expected return and volatility
        expected_return = self._estimate_expected_return(
            buy_prob, sell_prob, hold_prob, data
        )
        expected_volatility = self._estimate_expected_volatility(data)

        # Determine market regime
        regime, regime_confidence = self._determine_regime(data, features_df)

        # Calculate confidence metrics
        confidence_score = self._calculate_confidence(proba, signal_strength)
        confidence_level = self._classify_confidence(confidence_score)
        entropy = self._calculate_entropy(proba)
        uncertainty = self._calculate_uncertainty(proba, confidence_score)

        # Additional warnings
        if confidence_level == "LOW":
            warnings.append("Low confidence prediction. Exercise caution.")
        if uncertainty > 0.5:
            warnings.append("High uncertainty in prediction.")

        prediction = Prediction(
            buy_probability=buy_prob,
            sell_probability=sell_prob,
            hold_probability=hold_prob,
            signal=signal,
            signal_strength=signal_strength,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            regime=regime,
            regime_confidence=regime_confidence,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            prediction_entropy=entropy,
            uncertainty=uncertainty,
            model_id=self.model_info.model_id,
            model_version=self.model_info.version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            features_used=len(available_features),
            warnings=warnings,
        )

        logger.debug(f"Prediction generated: {prediction}")
        return prediction

    def predict_batch(self, data: pd.DataFrame) -> list[Prediction]:
        """Generate predictions for multiple time steps.

        Args:
            data: DataFrame with OHLCV data.

        Returns:
            List of Prediction objects, one per valid time step.
        """
        predictions: list[Prediction] = []
        min_rows = 50

        for i in range(min_rows, len(data) + 1):
            try:
                subset = data.iloc[:i]
                pred = self.predict(subset)
                predictions.append(pred)
            except (ValueError, Exception) as e:
                logger.debug(f"Skipping prediction at index {i}: {e}")
                continue

        return predictions

    def _map_probabilities(self, proba: np.ndarray) -> tuple[float, float, float]:
        """Map model output probabilities to BUY/SELL/HOLD.

        Handles different class mappings:
        - 2 classes: [SELL, BUY] or [HOLD, TRADE]
        - 3 classes: [SELL, HOLD, BUY] or [BUY, HOLD, SELL]
        """
        n_classes = len(proba)

        if n_classes >= 3:
            # Assume order: [SELL, HOLD, BUY] or [BUY, HOLD, SELL]
            # Use model_info to determine
            class_dist = self.model_info.class_distribution

            # Try to infer from class distribution keys
            if "-1" in class_dist or class_dist.get("-1", 0) > 0:
                # Classes are -1 (SELL), 0 (HOLD), 1 (BUY)
                sell_prob = float(proba[0])
                hold_prob = float(proba[1])
                buy_prob = float(proba[2])
            else:
                # Classes are 0 (BUY), 1 (HOLD), 2 (SELL) or similar
                # Default: assume [BUY, HOLD, SELL]
                buy_prob = float(proba[0])
                hold_prob = float(proba[1])
                sell_prob = float(proba[2])
        elif n_classes == 2:
            # Binary: [SELL, BUY] or [HOLD, TRADE]
            # Assume [negative, positive] = [SELL, BUY]
            sell_prob = float(proba[0])
            buy_prob = float(proba[1])
            hold_prob = 0.0
        else:
            # Single class output
            buy_prob = float(proba[0])
            sell_prob = 0.0
            hold_prob = 0.0

        # Normalize to ensure they sum to 1
        total = buy_prob + sell_prob + hold_prob
        if total > 0:
            buy_prob /= total
            sell_prob /= total
            hold_prob /= total

        return buy_prob, sell_prob, hold_prob

    def _determine_signal(
        self, buy_prob: float, sell_prob: float, hold_prob: float
    ) -> tuple[str, float]:
        """Determine trading signal from probabilities."""
        probs = {"BUY": buy_prob, "SELL": sell_prob, "HOLD": hold_prob}
        signal = max(probs, key=probs.get)
        signal_strength = probs[signal]

        # If no clear signal, default to HOLD
        if signal_strength < self.MODERATE_SIGNAL:
            signal = "HOLD"
            signal_strength = hold_prob

        return signal, signal_strength

    def _estimate_expected_return(
        self, buy_prob: float, sell_prob: float, hold_prob: float, data: pd.DataFrame
    ) -> float:
        """Estimate expected return based on signal probabilities and recent volatility."""
        # Use recent returns as baseline
        if "close" in data.columns and len(data) > 1:
            recent_returns = data["close"].pct_change().dropna()
            if len(recent_returns) > 0:
                mean_return = recent_returns.mean() * 100  # As percentage
                std_return = recent_returns.std() * 100
            else:
                mean_return = 0.0
                std_return = 1.0
        else:
            mean_return = 0.0
            std_return = 1.0

        # Weight by probabilities
        # BUY: expect positive return, SELL: expect negative, HOLD: expect ~0
        expected = (buy_prob * abs(mean_return)) - (sell_prob * abs(mean_return))
        expected += hold_prob * mean_return * 0.1  # Small drift for HOLD

        # Adjust for signal strength
        signal_strength = max(buy_prob, sell_prob, hold_prob)
        expected *= signal_strength

        return float(expected)

    def _estimate_expected_volatility(self, data: pd.DataFrame) -> float:
        """Estimate expected volatility from recent data."""
        if "close" in data.columns and len(data) > 20:
            returns = data["close"].pct_change().dropna()
            if len(returns) > 0:
                # Annualized volatility as percentage
                vol = returns.std() * np.sqrt(252) * 100
                return float(vol)
        return 0.0

    def _determine_regime(
        self, data: pd.DataFrame, features_df: pd.DataFrame
    ) -> tuple[str, float]:
        """Determine market regime from features and price action."""
        if features_df.empty:
            return "UNKNOWN", 0.0

        latest = features_df.iloc[-1]

        # Use regime feature if available
        if "regime" in latest:
            regime_val = latest["regime"]
            if regime_val == 1:
                return "UPTREND", 0.7
            elif regime_val == -1:
                return "DOWNTREND", 0.7
            else:
                return "SIDEWAYS", 0.6

        # Fallback: use EMA alignment
        if "ema_alignment" in latest:
            alignment = latest["ema_alignment"]
            if alignment >= 2:
                return "UPTREND", min(0.5 + alignment * 0.1, 0.95)
            elif alignment <= -2:
                return "DOWNTREND", min(0.5 + abs(alignment) * 0.1, 0.95)
            else:
                return "SIDEWAYS", 0.6

        # Fallback: use ADX
        if "adx" in latest:
            adx = latest["adx"]
            if adx > 25:
                # Strong trend - determine direction from DI
                if "plus_di" in latest and "minus_di" in latest:
                    if latest["plus_di"] > latest["minus_di"]:
                        return "UPTREND", min(adx / 50, 0.95)
                    else:
                        return "DOWNTREND", min(adx / 50, 0.95)
                return "VOLATILE", min(adx / 50, 0.95)
            else:
                return "SIDEWAYS", 0.5

        return "UNKNOWN", 0.0

    def _calculate_confidence(self, proba: np.ndarray, signal_strength: float) -> float:
        """Calculate overall confidence score.

        Combines:
        - Maximum class probability (primary)
        - Margin between top two classes
        - Signal strength
        """
        sorted_proba = np.sort(proba)[::-1]
        max_proba = sorted_proba[0]

        if len(sorted_proba) > 1:
            margin = sorted_proba[0] - sorted_proba[1]
        else:
            margin = 1.0

        # Weighted combination
        confidence = 0.5 * max_proba + 0.3 * margin + 0.2 * signal_strength

        # Penalize if probabilities are too uniform (high uncertainty)
        if max_proba < 0.4:
            confidence *= 0.8

        return float(np.clip(confidence, 0.0, 1.0))

    def _classify_confidence(self, score: float) -> str:
        """Classify confidence score into level."""
        if score >= self.CONFIDENCE_HIGH:
            return "HIGH"
        elif score >= self.CONFIDENCE_MEDIUM:
            return "MEDIUM"
        elif score >= self.CONFIDENCE_LOW:
            return "LOW"
        else:
            return "VERY_LOW"

    def _calculate_entropy(self, proba: np.ndarray) -> float:
        """Calculate Shannon entropy of prediction distribution.

        Higher entropy = more uncertainty.
        """
        # Filter out zeros to avoid log(0)
        proba = proba[proba > 0]
        if len(proba) == 0:
            return 0.0

        entropy = -np.sum(proba * np.log2(proba))
        # Normalize by maximum possible entropy
        max_entropy = np.log2(len(proba))
        if max_entropy > 0:
            entropy /= max_entropy

        return float(entropy)

    def _calculate_uncertainty(self, proba: np.ndarray, confidence: float) -> float:
        """Calculate overall uncertainty score.

        Combines entropy and inverse confidence.
        """
        entropy = self._calculate_entropy(proba)
        uncertainty = 0.6 * entropy + 0.4 * (1 - confidence)
        return float(np.clip(uncertainty, 0.0, 1.0))

    def _infer_class_mapping(self) -> dict[int, int]:
        """Infer the class mapping from model info.

        Returns a dict mapping original labels to encoded labels.
        """
        class_dist = self.model_info.class_distribution

        # Try to parse class distribution
        mapping: dict[int, int] = {}
        for idx, (key, _) in enumerate(sorted(class_dist.items(), key=lambda x: int(x[0]))):
            mapping[int(key)] = idx

        if not mapping:
            # Default mapping
            mapping = {-1: 0, 0: 1, 1: 2}

        return mapping

    def get_model_summary(self) -> dict[str, Any]:
        """Get a summary of the model used for predictions."""
        return {
            "model_id": self.model_info.model_id,
            "name": self.model_info.name,
            "version": self.model_info.version,
            "type": self.model_info.model_type,
            "strategy": self.model_info.strategy,
            "training_date": self.model_info.training_date,
            "features_count": len(self.model_info.features),
            "test_accuracy": self.model_info.metrics.get("accuracy", 0.0),
            "test_f1": self.model_info.metrics.get("f1_macro", 0.0),
        }
