"""AI prediction service with simulated ML models."""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.system import ModelVersion
from app.repositories.system import ModelRepository
from app.services.market_data import MarketDataService


class AIEngine:
    """Engine for AI-powered trading predictions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_repo = ModelRepository(db)
        self.market_data = MarketDataService()
        self._models: Dict[str, any] = {}
        self._prediction_cache: Dict[str, Dict] = {}
        self._cache_ttl = 60  # seconds

    async def predict(
        self,
        symbol: str,
        timeframe: str = "1h",
    ) -> Dict:
        """Generate AI prediction for a symbol."""
        cache_key = f"{symbol}_{timeframe}"

        # Check cache
        if cache_key in self._prediction_cache:
            cached = self._prediction_cache[cache_key]
            if (datetime.now(timezone.utc) - cached["timestamp"]).seconds < self._cache_ttl:
                return cached["prediction"]

        # Get market data
        candles = await self.market_data.get_candles(symbol, timeframe, settings.AI_FEATURE_WINDOW)

        if not candles:
            return {
                "symbol": symbol,
                "signal": "hold",
                "confidence": 0.0,
                "reason": "Insufficient data",
            }

        # Generate prediction using simulated ML
        prediction = self._generate_prediction(symbol, candles)

        # Cache prediction
        self._prediction_cache[cache_key] = {
            "prediction": prediction,
            "timestamp": datetime.now(timezone.utc),
        }

        return prediction

    def _generate_prediction(self, symbol: str, candles: List[Dict]) -> Dict:
        """Generate prediction using technical analysis and simulated ML."""
        closes = np.array([c["close"] for c in candles])
        highs = np.array([c["high"] for c in candles])
        lows = np.array([c["low"] for c in candles])
        volumes = np.array([c["volume"] for c in candles])

        # Calculate technical indicators
        sma_20 = np.mean(closes[-20:])
        sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else np.mean(closes)
        current_price = closes[-1]

        # RSI calculation
        rsi = self._calculate_rsi(closes)

        # MACD calculation
        macd, signal = self._calculate_macd(closes)

        # Bollinger Bands
        bb_upper, bb_lower = self._calculate_bollinger_bands(closes)

        # Volume trend
        volume_sma = np.mean(volumes[-20:])
        volume_trend = volumes[-1] / volume_sma if volume_sma > 0 else 1.0

        # Generate signal based on indicators
        score = 0.0
        reasons = []

        # Trend analysis
        if current_price > sma_20 > sma_50:
            score += 0.3
            reasons.append("Bullish trend (price > SMA20 > SMA50)")
        elif current_price < sma_20 < sma_50:
            score -= 0.3
            reasons.append("Bearish trend (price < SMA20 < SMA50)")

        # RSI analysis
        if rsi < 30:
            score += 0.25
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            score -= 0.25
            reasons.append(f"RSI overbought ({rsi:.1f})")

        # MACD analysis
        if macd > signal:
            score += 0.2
            reasons.append("MACD bullish crossover")
        else:
            score -= 0.2
            reasons.append("MACD bearish crossover")

        # Bollinger Bands
        if current_price <= bb_lower:
            score += 0.15
            reasons.append("Price at lower Bollinger Band")
        elif current_price >= bb_upper:
            score -= 0.15
            reasons.append("Price at upper Bollinger Band")

        # Volume confirmation
        if volume_trend > 1.5:
            if score > 0:
                score += 0.1
                reasons.append("High volume confirms bullish move")
            elif score < 0:
                score -= 0.1
                reasons.append("High volume confirms bearish move")

        # Add some randomness to simulate ML uncertainty
        score += random.uniform(-0.1, 0.1)
        score = max(-1.0, min(1.0, score))

        # Determine signal
        if score >= settings.AI_PREDICTION_THRESHOLD:
            signal = "buy"
        elif score <= -settings.AI_PREDICTION_THRESHOLD:
            signal = "sell"
        else:
            signal = "hold"

        confidence = abs(score)

        # Calculate target and stop loss
        atr = self._calculate_atr(highs, lows, closes)
        if signal == "buy":
            target = current_price + (atr * 2)
            stop_loss = current_price - (atr * 1.5)
        elif signal == "sell":
            target = current_price - (atr * 2)
            stop_loss = current_price + (atr * 1.5)
        else:
            target = current_price
            stop_loss = current_price

        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": round(confidence, 4),
            "score": round(score, 4),
            "current_price": round(current_price, 8),
            "target_price": round(target, 8),
            "stop_loss": round(stop_loss, 8),
            "indicators": {
                "rsi": round(rsi, 2),
                "macd": round(macd, 8),
                "macd_signal": round(signal, 8),
                "sma_20": round(sma_20, 8),
                "sma_50": round(sma_50, 8),
                "bb_upper": round(bb_upper, 8),
                "bb_lower": round(bb_lower, 8),
                "atr": round(atr, 8),
                "volume_trend": round(volume_trend, 2),
            },
            "reasons": reasons,
            "timestamp": datetime.now(timezone.utc),
        }

    def _calculate_rsi(self, closes: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(closes) < period + 1:
            return 50.0

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

    def _calculate_macd(
        self, closes: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[float, float]:
        """Calculate MACD and signal line."""
        if len(closes) < slow:
            return 0.0, 0.0

        ema_fast = self._ema(closes, fast)
        ema_slow = self._ema(closes, slow)
        macd_line = ema_fast - ema_slow

        # Signal line is EMA of MACD
        macd_history = []
        for i in range(slow, len(closes) + 1):
            macd_history.append(self._ema(closes[:i], fast) - self._ema(closes[:i], slow))

        signal_line = self._ema(np.array(macd_history), signal) if len(macd_history) >= signal else macd_line

        return macd_line, signal_line

    def _ema(self, data: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(data) < period:
            return float(np.mean(data))

        multiplier = 2 / (period + 1)
        ema = float(np.mean(data[:period]))

        for price in data[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _calculate_bollinger_bands(
        self, closes: np.ndarray, period: int = 20, std_dev: float = 2.0
    ) -> Tuple[float, float]:
        """Calculate Bollinger Bands."""
        if len(closes) < period:
            period = len(closes)

        sma = np.mean(closes[-period:])
        std = np.std(closes[-period:])

        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        return upper, lower

    def _calculate_atr(
        self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14
    ) -> float:
        """Calculate Average True Range."""
        if len(closes) < 2:
            return 0.0

        trs = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            trs.append(tr)

        if len(trs) < period:
            return float(np.mean(trs)) if trs else 0.0

        return float(np.mean(trs[-period:]))

    async def train_model(self, model_type: str, symbol: str) -> Dict:
        """Train a new AI model."""
        # Simulate training process
        await asyncio.sleep(2)

        # Generate simulated metrics
        accuracy = random.uniform(0.55, 0.85)
        precision = random.uniform(0.50, 0.80)
        recall = random.uniform(0.50, 0.80)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        version = f"v{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}"

        model = await self.model_repo.create(
            {
                "model_name": f"{model_type}_{symbol.replace('/', '_')}",
                "version": version,
                "model_type": model_type,
                "file_path": f"{settings.MODEL_PATH}/{model_type}_{symbol.replace('/', '_')}_{version}.pkl",
                "is_active": False,
                "is_approved": False,
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "sharpe_ratio": round(random.uniform(0.5, 2.5), 2),
                "max_drawdown": round(random.uniform(0.05, 0.25), 4),
                "training_data_start": datetime.now(timezone.utc) - timedelta(days=365),
                "training_data_end": datetime.now(timezone.utc),
                "features_used": ["rsi", "macd", "bollinger", "volume", "sma", "ema"],
                "hyperparameters": {
                    "learning_rate": 0.01,
                    "max_depth": 6,
                    "n_estimators": 100,
                    "subsample": 0.8,
                },
            },
        )

        return {
            "message": "Model training completed",
            "model_id": model.id,
            "version": version,
            "metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
            },
        }

    async def get_feature_importance(self, model_id: int) -> Dict:
        """Get feature importance for a model."""
        return {
            "rsi": round(random.uniform(0.1, 0.3), 4),
            "macd": round(random.uniform(0.1, 0.25), 4),
            "bollinger": round(random.uniform(0.05, 0.2), 4),
            "volume": round(random.uniform(0.05, 0.15), 4),
            "sma": round(random.uniform(0.05, 0.15), 4),
            "ema": round(random.uniform(0.05, 0.15), 4),
        }

    async def batch_predict(self, symbols: List[str], timeframe: str = "1h") -> List[Dict]:
        """Generate predictions for multiple symbols."""
        predictions = []
        for symbol in symbols:
            pred = await self.predict(symbol, timeframe)
            predictions.append(pred)
        return predictions
