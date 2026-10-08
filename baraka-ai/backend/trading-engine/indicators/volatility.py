"""Volatility indicators: ATR, Bollinger Bands, Historical Volatility."""
import pandas as pd
import numpy as np


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range."""
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def bollinger_bands(close: pd.Series, period: int = 20, num_std: float = 2.0) -> tuple:
    """Bollinger Bands: upper, middle, lower."""
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    return upper, middle, lower


def historical_volatility(close: pd.Series, period: int = 20) -> pd.Series:
    """Annualized historical volatility."""
    log_returns = np.log(close / close.shift(1))
    return log_returns.rolling(window=period).std() * np.sqrt(365) * 100


def candle_range_stats(df: pd.DataFrame, period: int = 20) -> dict:
    """Candle range statistics."""
    ranges = df['high'] - df['low']
    body = (df['close'] - df['open']).abs()
    upper_wick = df['high'] - df[['open', 'close']].max(axis=1)
    lower_wick = df[['open', 'close']].min(axis=1) - df['low']

    return {
        'avg_range': ranges.rolling(period).mean().iloc[-1] if len(ranges) >= period else 0,
        'avg_body': body.rolling(period).mean().iloc[-1] if len(body) >= period else 0,
        'avg_upper_wick': upper_wick.rolling(period).mean().iloc[-1] if len(upper_wick) >= period else 0,
        'avg_lower_wick': lower_wick.rolling(period).mean().iloc[-1] if len(lower_wick) >= period else 0,
        'body_ratio': (body / ranges.replace(0, np.nan)).rolling(period).mean().iloc[-1] if len(ranges) >= period else 0,
    }
