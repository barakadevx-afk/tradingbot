"""Market structure detection."""
import pandas as pd
import numpy as np
from typing import Optional


def detect_structure(df: pd.DataFrame, lookback: int = 5) -> dict:
    """Detect market structure: higher highs, lower lows, etc."""
    if len(df) < lookback * 2:
        return {"structure": "UNCERTAIN", "higher_highs": False, "higher_lows": False,
                "lower_highs": False, "lower_lows": False}

    recent_highs = df['high'].rolling(lookback).max().iloc[-lookback:]
    recent_lows = df['low'].rolling(lookback).min().iloc[-lookback:]

    higher_highs = all(recent_highs.iloc[i] < recent_highs.iloc[i+1] for i in range(len(recent_highs)-1))
    higher_lows = all(recent_lows.iloc[i] < recent_lows.iloc[i+1] for i in range(len(recent_lows)-1))
    lower_highs = all(recent_highs.iloc[i] > recent_highs.iloc[i+1] for i in range(len(recent_highs)-1))
    lower_lows = all(recent_lows.iloc[i] > recent_lows.iloc[i+1] for i in range(len(recent_lows)-1))

    if higher_highs and higher_lows:
        structure = "UPTREND"
    elif lower_highs and lower_lows:
        structure = "DOWNTREND"
    elif higher_lows and lower_highs:
        structure = "CONSOLIDATION"
    else:
        structure = "UNCERTAIN"

    return {
        "structure": structure,
        "higher_highs": higher_highs,
        "higher_lows": higher_lows,
        "lower_highs": lower_highs,
        "lower_lows": lower_lows,
    }


def find_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
    """Find support and resistance levels."""
    recent = df.tail(window)
    support = recent['low'].min()
    resistance = recent['high'].max()
    current_price = df['close'].iloc[-1]

    return {
        "support": support,
        "resistance": resistance,
        "current_price": current_price,
        "distance_to_support": (current_price - support) / current_price * 100 if support > 0 else 0,
        "distance_to_resistance": (resistance - current_price) / current_price * 100 if resistance > 0 else 0,
    }


def detect_breakout(df: pd.DataFrame, consolidation_period: int = 20, volume_threshold: float = 1.5) -> dict:
    """Detect breakout from consolidation."""
    if len(df) < consolidation_period + 1:
        return {"breakout": False, "direction": None, "strength": 0}

    consolidation = df.tail(consolidation_period + 1).head(consolidation_period)
    current = df.iloc[-1]

    consolidation_high = consolidation['high'].max()
    consolidation_low = consolidation['low'].min()
    consolidation_range = consolidation_high - consolidation_low

    avg_volume = consolidation['volume'].mean()
    volume_expansion = current['volume'] / avg_volume if avg_volume > 0 else 1

    breakout_up = current['close'] > consolidation_high
    breakout_down = current['close'] < consolidation_low

    if breakout_up and volume_expansion > volume_threshold:
        return {"breakout": True, "direction": "UP", "strength": min(volume_expansion / 2, 1.0)}
    elif breakout_down and volume_expansion > volume_threshold:
        return {"breakout": True, "direction": "DOWN", "strength": min(volume_expansion / 2, 1.0)}

    return {"breakout": False, "direction": None, "strength": 0}
