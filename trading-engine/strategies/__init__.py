"""
Trading Strategies Module
=========================

Provides strategy implementations for the BARAKA AI trading engine.
"""

from trading_engine.strategies.trend_following import TrendFollowingStrategy
from trading_engine.strategies.breakout import BreakoutStrategy
from trading_engine.strategies.pullback import PullbackStrategy
from trading_engine.strategies.mean_reversion import MeanReversionStrategy

__all__ = [
    "TrendFollowingStrategy",
    "BreakoutStrategy",
    "PullbackStrategy",
    "MeanReversionStrategy",
]
