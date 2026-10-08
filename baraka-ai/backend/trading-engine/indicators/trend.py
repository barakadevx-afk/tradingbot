"""Trend indicators: EMA, SMA, ADX."""
import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=period).mean()


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average Directional Index."""
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    return adx


def ema_cross_state(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """Returns 1 when fast > slow, -1 when fast < slow, 0 when equal."""
    cross = pd.Series(0, index=fast.index)
    cross[fast > slow] = 1
    cross[fast < slow] = -1
    return cross


def ema_distance(price: pd.Series, ema_series: pd.Series) -> pd.Series:
    """Percentage distance from price to EMA."""
    return (price - ema_series) / ema_series * 100
