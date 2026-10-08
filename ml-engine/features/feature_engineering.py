"""
Feature Engineering Module
==========================
Generates AI-ready features from OHLCV market data.

All features are computed using only past and current data to prevent
data leakage. No future values are ever used in feature computation.

Features include:
- Normalized returns
- Rolling returns (multiple windows)
- EMA distance and cross state
- RSI (Relative Strength Index)
- MACD histogram
- ATR percentage
- Volatility (rolling standard deviation)
- Volume change
- Spread metrics
- Candle-body ratio and wick ratios
- Momentum indicators
- Price distance from support/resistance
- Trend strength (ADX-like)
- Market regime classification
- Rolling high/low distance
- Liquidity indicators
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Computes technical and statistical features from OHLCV data.

    This class is designed to be stateless - all methods take a DataFrame
    and return a new DataFrame with computed features. This ensures no
    data leakage between training and inference.
    """

    DEFAULT_PERIODS: dict[str, int] = {
        "rsi": 14,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "atr": 14,
        "volatility": 20,
        "volume_change": 10,
        "momentum": 10,
        "trend_strength": 14,
        "rolling_return_short": 5,
        "rolling_return_medium": 10,
        "rolling_return_long": 20,
        "ema_short": 12,
        "ema_medium": 26,
        "ema_long": 50,
        "rolling_high_low": 20,
        "liquidity": 20,
    }

    def __init__(self, periods: dict[str, int] | None = None):
        """Initialize the FeatureEngineer.

        Args:
            periods: Override default period parameters. Any key not provided
                     will use the default value.
        """
        self.periods = {**self.DEFAULT_PERIODS, **(periods or {})}
        self._feature_names: list[str] = []
        self._is_fitted = False

    @property
    def feature_names(self) -> list[str]:
        """Return the list of feature names produced by this engineer."""
        return list(self._feature_names)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform raw OHLCV data into feature-rich DataFrame.

        Args:
            data: DataFrame with columns ['open', 'high', 'low', 'close', 'volume'].
                  Must be sorted by time ascending.

        Returns:
            DataFrame with all computed features. Rows with NaN values
            (from rolling calculations) are preserved for the caller to handle.

        Raises:
            ValueError: If required columns are missing.
        """
        required = {"open", "high", "low", "close", "volume"}
        missing = required - set(data.columns.str.lower())
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = data.copy()
        df.columns = df.columns.str.lower()

        # Ensure proper ordering
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp").reset_index(drop=True)
        elif "date" in df.columns:
            df = df.sort_values("date").reset_index(drop=True)
        else:
            df = df.sort_index().reset_index(drop=True)

        features = pd.DataFrame(index=df.index)

        # --- Price-based features ---
        features = self._compute_returns(df, features)
        features = self._compute_rolling_returns(df, features)
        features = self._compute_ema_features(df, features)
        features = self._compute_rsi(df, features)
        features = self._compute_macd(df, features)
        features = self._compute_atr(df, features)
        features = self._compute_volatility(df, features)
        features = self._compute_momentum(df, features)
        features = self._compute_trend_strength(df, features)
        features = self._compute_regime(df, features)

        # --- Volume-based features ---
        features = self._compute_volume_features(df, features)
        features = self._compute_liquidity(df, features)

        # --- Candle-based features ---
        features = self._compute_candle_features(df, features)

        # --- Support/Resistance distance ---
        features = self._compute_sr_distance(df, features)

        # --- Rolling high/low distance ---
        features = self._compute_rolling_high_low(df, features)

        self._feature_names = features.columns.tolist()
        self._is_fitted = True

        logger.info(
            f"Feature engineering complete: {len(features.columns)} features "
            f"generated from {len(df)} rows"
        )

        return features

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one call (stateless, same as transform)."""
        return self.transform(data)

    def _compute_returns(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute normalized returns (percentage change)."""
        p = self.periods
        close = df["close"]

        # Simple normalized return
        features["return_1"] = close.pct_change(1)

        # Log return (more statistically well-behaved)
        features["log_return_1"] = np.log(close / close.shift(1))

        # Normalized return by ATR (risk-adjusted)
        atr = self._calculate_atr(df, p["atr"])
        features["return_atr_norm"] = features["return_1"] / (atr / close)

        # Z-score of returns (rolling)
        rolling_mean = features["return_1"].rolling(p["volatility"]).mean()
        rolling_std = features["return_1"].rolling(p["volatility"]).std()
        features["return_zscore"] = (features["return_1"] - rolling_mean) / rolling_std

        return features

    def _compute_rolling_returns(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute rolling returns over multiple windows."""
        p = self.periods
        close = df["close"]

        for label, window in [
            ("short", p["rolling_return_short"]),
            ("medium", p["rolling_return_medium"]),
            ("long", p["rolling_return_long"]),
        ]:
            features[f"rolling_return_{label}"] = close.pct_change(window)

        # Annualized return estimate (assuming daily data)
        features["annualized_return"] = (
            close.pct_change(p["rolling_return_long"]) * (252 / p["rolling_return_long"])
        )

        return features

    def _compute_ema_features(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute EMA distance and cross state features."""
        p = self.periods
        close = df["close"]

        ema_short = close.ewm(span=p["ema_short"], adjust=False).mean()
        ema_medium = close.ewm(span=p["ema_medium"], adjust=False).mean()
        ema_long = close.ewm(span=p["ema_long"], adjust=False).mean()

        # EMA distance (normalized by price)
        features["ema_dist_short"] = (close - ema_short) / close
        features["ema_dist_medium"] = (close - ema_medium) / close
        features["ema_dist_long"] = (close - ema_long) / close

        # EMA spread (difference between EMAs, normalized)
        features["ema_spread_sm"] = (ema_short - ema_medium) / close
        features["ema_spread_ml"] = (ema_medium - ema_long) / close
        features["ema_spread_sl"] = (ema_short - ema_long) / close

        # EMA cross state: 1 = short above medium, -1 = short below medium
        features["ema_cross_sm"] = np.where(ema_short > ema_medium, 1, -1)
        features["ema_cross_ml"] = np.where(ema_medium > ema_long, 1, -1)
        features["ema_cross_sl"] = np.where(ema_short > ema_long, 1, -1)

        # EMA slope (rate of change of EMA)
        features["ema_slope_short"] = ema_short.pct_change(1)
        features["ema_slope_medium"] = ema_medium.pct_change(1)
        features["ema_slope_long"] = ema_long.pct_change(1)

        # Triple EMA alignment: 3 = strong bullish, -3 = strong bearish
        features["ema_alignment"] = (
            features["ema_cross_sm"] + features["ema_cross_ml"] + features["ema_cross_sl"]
        )

        return features

    def _compute_rsi(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute RSI (Relative Strength Index)."""
        p = self.periods
        close = df["close"]
        period = p["rsi"]

        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        # Use Wilder's smoothing (RMA)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        features["rsi"] = 100 - (100 / (1 + rs))

        # RSI-derived features
        features["rsi_normalized"] = (features["rsi"] - 50) / 50  # [-1, 1]
        features["rsi_overbought"] = (features["rsi"] > 70).astype(int)
        features["rsi_oversold"] = (features["rsi"] < 30).astype(int)

        # RSI slope
        features["rsi_slope"] = features["rsi"].diff(3)

        # RSI divergence (price up but RSI down, or vice versa)
        price_up = close.diff(5) > 0
        rsi_down = features["rsi"].diff(5) < 0
        features["rsi_bullish_divergence"] = (price_up & rsi_down).astype(int)

        price_down = close.diff(5) < 0
        rsi_up = features["rsi"].diff(5) > 0
        features["rsi_bearish_divergence"] = (price_down & rsi_up).astype(int)

        return features

    def _compute_macd(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute MACD histogram and related features."""
        p = self.periods
        close = df["close"]

        ema_fast = close.ewm(span=p["macd_fast"], adjust=False).mean()
        ema_slow = close.ewm(span=p["macd_slow"], adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=p["macd_signal"], adjust=False).mean()
        histogram = macd_line - signal_line

        # Normalize by price
        features["macd_line"] = macd_line / close
        features["macd_signal"] = signal_line / close
        features["macd_histogram"] = histogram / close

        # MACD cross state
        features["macd_cross"] = np.where(macd_line > signal_line, 1, -1)

        # MACD momentum (change in histogram)
        features["macd_hist_change"] = features["macd_histogram"].diff(1)

        # MACD zero-line cross
        features["macd_above_zero"] = (macd_line > 0).astype(int)

        return features

    def _compute_atr(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute ATR (Average True Range) as percentage of price."""
        p = self.periods
        atr = self._calculate_atr(df, p["atr"])
        close = df["close"]

        features["atr"] = atr
        features["atr_pct"] = (atr / close) * 100  # ATR as percentage

        # ATR trend (increasing volatility)
        features["atr_slope"] = features["atr_pct"].diff(3)

        # ATR percentile (where current ATR sits in its range)
        atr_roll_max = features["atr_pct"].rolling(p["liquidity"]).max()
        atr_roll_min = features["atr_pct"].rolling(p["liquidity"]).min()
        features["atr_percentile"] = (features["atr_pct"] - atr_roll_min) / (
            atr_roll_max - atr_roll_min + 1e-10
        )

        # Normalized ATR (z-score)
        atr_mean = features["atr_pct"].rolling(p["liquidity"]).mean()
        atr_std = features["atr_pct"].rolling(p["liquidity"]).std()
        features["atr_zscore"] = (features["atr_pct"] - atr_mean) / (atr_std + 1e-10)

        return features

    def _compute_volatility(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute rolling volatility features."""
        p = self.periods
        close = df["close"]
        returns = close.pct_change()

        # Standard rolling volatility (annualized)
        features["volatility"] = returns.rolling(p["volatility"]).std() * np.sqrt(252)

        # Parkinson volatility (uses high-low range)
        hl_ratio = np.log(df["high"] / df["low"]) ** 2
        parkinson_vol = np.sqrt(
            hl_ratio.rolling(p["volatility"]).mean() / (4 * np.log(2))
        ) * np.sqrt(252)
        features["parkinson_volatility"] = parkinson_vol

        # Volatility regime (high/low relative to history)
        vol_median = features["volatility"].rolling(p["liquidity"]).median()
        features["vol_regime"] = np.where(
            features["volatility"] > vol_median, 1, 0
        )

        # Volatility of volatility
        features["vol_of_vol"] = (
            features["volatility"].rolling(p["volatility"]).std()
        )

        # GARCH-like: weighted recent volatility
        features["ewma_volatility"] = returns.ewm(span=p["volatility"]).std() * np.sqrt(
            252
        )

        return features

    def _compute_volume_features(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute volume-based features."""
        p = self.periods
        volume = df["volume"]
        close = df["close"]

        # Volume change (percentage)
        features["volume_change"] = volume.pct_change(1)

        # Volume z-score
        vol_mean = volume.rolling(p["volume_change"]).mean()
        vol_std = volume.rolling(p["volume_change"]).std()
        features["volume_zscore"] = (volume - vol_mean) / (vol_std + 1e-10)

        # Volume trend (EMA of volume)
        features["volume_ema"] = volume.ewm(span=p["volume_change"]).mean()
        features["volume_ratio"] = volume / (features["volume_ema"] + 1e-10)

        # On-Balance Volume (OBV)
        obv = (np.sign(close.diff()) * volume).cumsum()
        features["obv"] = obv
        features["obv_slope"] = obv.diff(5)

        # Volume-weighted price deviation
        typical_price = (df["high"] + df["low"] + close) / 3
        features["vwap_deviation"] = (close - typical_price) / typical_price

        # Dollar volume
        features["dollar_volume"] = volume * close
        features["dollar_volume_change"] = features["dollar_volume"].pct_change(1)

        return features

    def _compute_liquidity(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute liquidity indicators."""
        p = self.periods
        close = df["close"]
        volume = df["volume"]

        # Amihud illiquidity: |return| / dollar volume
        returns = close.pct_change().abs()
        dollar_vol = volume * close
        features["amihud_illiquidity"] = returns / (dollar_vol + 1e-10)

        # Rolling average spread proxy (using high-low)
        spread_proxy = (df["high"] - df["low"]) / close
        features["spread_proxy"] = spread_proxy
        features["spread_proxy_ma"] = spread_proxy.rolling(p["liquidity"]).mean()

        # Liquidity ratio: volume / ATR
        atr = self._calculate_atr(df, p["atr"])
        features["liquidity_ratio"] = volume / (atr + 1e-10)

        # Turnover proxy
        features["turnover_proxy"] = volume.rolling(p["liquidity"]).sum()

        # Kyle's lambda proxy (price impact)
        features["kyle_lambda"] = (
            close.diff().abs() / (volume + 1e-10)
        ).rolling(p["liquidity"]).mean()

        return features

    def _compute_candle_features(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute candlestick-based features."""
        o, h, l, c = df["open"], df["high"], df["low"], df["close"]

        body = c - o
        upper_wick = h - np.maximum(o, c)
        lower_wick = np.minimum(o, c) - l
        total_range = h - l

        # Candle body ratio (body / total range)
        features["candle_body_ratio"] = body.abs() / (total_range + 1e-10)

        # Wick ratios
        features["upper_wick_ratio"] = upper_wick / (total_range + 1e-10)
        features["lower_wick_ratio"] = lower_wick / (total_range + 1e-10)

        # Candle direction: 1 = bullish, -1 = bearish
        features["candle_direction"] = np.sign(body)

        # Candle size relative to recent average
        avg_range = total_range.rolling(self.periods["liquidity"]).mean()
        features["candle_size_ratio"] = total_range / (avg_range + 1e-10)

        # Doji detection (very small body)
        features["is_doji"] = (features["candle_body_ratio"] < 0.1).astype(int)

        # Hammer / shooting star patterns
        features["is_hammer"] = (
            (lower_wick > 2 * body.abs()) & (upper_wick < body.abs())
        ).astype(int)
        features["is_shooting_star"] = (
            (upper_wick > 2 * body.abs()) & (lower_wick < body.abs())
        ).astype(int)

        # Consecutive same-direction candles
        features["consecutive_bullish"] = self._count_consecutive(
            features["candle_direction"], 1
        )
        features["consecutive_bearish"] = self._count_consecutive(
            features["candle_direction"], -1
        )

        return features

    def _compute_momentum(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute momentum indicators."""
        p = self.periods
        close = df["close"]

        # Simple momentum (rate of change)
        features["momentum"] = close.pct_change(p["momentum"])

        # Momentum acceleration
        features["momentum_accel"] = features["momentum"].diff(1)

        # ROC (Rate of Change) as percentage
        features["roc"] = ((close - close.shift(p["momentum"])) / close.shift(p["momentum"])) * 100

        # Stochastic oscillator
        low_min = df["low"].rolling(p["momentum"]).min()
        high_max = df["high"].rolling(p["momentum"]).max()
        features["stoch_k"] = ((close - low_min) / (high_max - low_min + 1e-10)) * 100
        features["stoch_d"] = features["stoch_k"].rolling(3).mean()

        # Williams %R
        features["williams_r"] = (
            (high_max - close) / (high_max - low_min + 1e-10)
        ) * -100

        # Commodity Channel Index (CCI)
        typical_price = (df["high"] + df["low"] + close) / 3
        sma_tp = typical_price.rolling(p["momentum"]).mean()
        mean_dev = typical_price.rolling(p["momentum"]).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True
        )
        features["cci"] = (typical_price - sma_tp) / (0.015 * mean_dev + 1e-10)

        return features

    def _compute_trend_strength(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute trend strength (ADX-like) indicator."""
        p = self.periods
        period = p["trend_strength"]

        high, low, close = df["high"], df["low"], df["close"]

        # True Range
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

        # Smoothed values (Wilder's)
        atr = tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        plus_di = 100 * (
            plus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr
        )
        minus_di = 100 * (
            minus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr
        )

        # ADX
        dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10))
        adx = dx.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        features["adx"] = adx
        features["plus_di"] = plus_di
        features["minus_di"] = minus_di
        features["di_spread"] = plus_di - minus_di

        # Trend direction from DI
        features["trend_direction"] = np.where(plus_di > minus_di, 1, -1)

        # Strong trend threshold
        features["strong_trend"] = (adx > 25).astype(int)

        return features

    def _compute_regime(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Classify market regime."""
        p = self.periods
        close = df["close"]

        # Trend regime using EMA alignment
        ema_short = close.ewm(span=p["ema_short"], adjust=False).mean()
        ema_long = close.ewm(span=p["ema_long"], adjust=False).mean()

        # Regime: 1 = uptrend, -1 = downtrend, 0 = sideways
        features["regime"] = np.where(
            (close > ema_short) & (ema_short > ema_long), 1,
            np.where((close < ema_short) & (ema_short < ema_long), -1, 0),
        )

        # Regime strength (how long has the current regime persisted)
        features["regime_duration"] = self._count_consecutive(features["regime"], 0)

        # Volatility regime
        vol = close.pct_change().rolling(p["volatility"]).std()
        vol_percentile = vol.rolling(p["liquidity"]).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )
        features["vol_regime_percentile"] = vol_percentile

        # Combined regime score: trend + volatility
        features["regime_score"] = features["regime"] * (1 - vol_percentile)

        return features

    def _compute_sr_distance(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute price distance from support and resistance levels."""
        p = self.periods
        close = df["close"]
        high = df["high"]
        low = df["low"]

        # Rolling support/resistance (using percentiles)
        rolling_window = p["rolling_high_low"]

        # Resistance: rolling max of highs
        rolling_resistance = high.rolling(rolling_window).max()
        features["dist_from_resistance"] = (close - rolling_resistance) / close

        # Support: rolling min of lows
        rolling_support = low.rolling(rolling_window).min()
        features["dist_from_support"] = (close - rolling_support) / close

        # Position within range (0 = at support, 1 = at resistance)
        range_height = rolling_resistance - rolling_support
        features["position_in_range"] = (close - rolling_support) / (range_height + 1e-10)

        # Distance from pivot (midpoint of range)
        pivot = (rolling_resistance + rolling_support) / 2
        features["dist_from_pivot"] = (close - pivot) / close

        # Dynamic S/R using recent swing points
        features["swing_high_dist"] = (close - high.rolling(rolling_window).max().shift(1)) / close
        features["swing_low_dist"] = (close - low.rolling(rolling_window).min().shift(1)) / close

        return features

    def _compute_rolling_high_low(
        self, df: pd.DataFrame, features: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute rolling high/low distance features."""
        p = self.periods
        window = p["rolling_high_low"]
        close = df["close"]

        rolling_high = df["high"].rolling(window).max()
        rolling_low = df["low"].rolling(window).min()

        # Distance from rolling high/low
        features["dist_from_rolling_high"] = (close - rolling_high) / close
        features["dist_from_rolling_low"] = (close - rolling_low) / close

        # Rolling range (high - low) as percentage of price
        rolling_range = rolling_high - rolling_low
        features["rolling_range_pct"] = (rolling_range / close) * 100

        # Rolling range expansion/contraction
        features["range_expansion"] = features["rolling_range_pct"].diff(5)

        # Percentile of current price within rolling range
        features["price_in_range"] = (close - rolling_low) / (rolling_range + 1e-10)

        # Distance from rolling VWAP
        typical_price = (df["high"] + df["low"] + close) / 3
        vwap = (typical_price * df["volume"]).rolling(window).sum() / (
            df["volume"].rolling(window).sum() + 1e-10
        )
        features["dist_from_vwap"] = (close - vwap) / close

        return features

    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range."""
        high, low, close = df["high"], df["low"], df["close"]

        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    @staticmethod
    def _count_consecutive(series: pd.Series, value: int) -> pd.Series:
        """Count consecutive occurrences of a value.

        For regime_duration, we count how many consecutive bars the regime
        has been the same as the current bar.
        """
        # Create groups where value changes
        groups = (series != series.shift()).cumsum()
        # Count within each group
        counts = series.groupby(groups).cumcount() + 1
        # Only keep counts where series equals the target value
        return counts.where(series == value, 0)

    def get_feature_importance_report(self) -> dict[str, Any]:
        """Return a report of all features and their categories."""
        if not self._is_fitted:
            return {"status": "not_fitted", "features": []}

        categories = {
            "returns": [f for f in self._feature_names if "return" in f],
            "ema": [f for f in self._feature_names if "ema" in f],
            "momentum": [f for f in self._feature_names if any(x in f for x in ["rsi", "macd", "stoch", "williams", "cci", "momentum", "roc"])],
            "volatility": [f for f in self._feature_names if "vol" in f],
            "volume": [f for f in self._feature_names if "volume" in f or "obv" in f or "dollar" in f],
            "candle": [f for f in self._feature_names if "candle" in f or "wick" in f or "doji" in f or "hammer" in f],
            "trend": [f for f in self._feature_names if any(x in f for x in ["adx", "di_", "trend", "regime"])],
            "liquidity": [f for f in self._feature_names if any(x in f for x in ["liquidity", "spread", "amihud", "kyle", "turnover"])],
            "support_resistance": [f for f in self._feature_names if any(x in f for x in ["resistance", "support", "pivot", "range", "swing"])],
        }

        return {
            "status": "fitted",
            "total_features": len(self._feature_names),
            "categories": categories,
            "all_features": self._feature_names,
        }
