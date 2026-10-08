"""
BARAKA AI - Backtesting Engine
==============================

A production-grade backtesting framework for algorithmic trading strategies.

Modules:
    engine       - Core backtesting engine
    metrics      - Performance metrics calculations
    walk_forward - Walk-forward validation
    monte_carlo  - Monte Carlo analysis
    data_loader  - Historical data loading
"""

from .engine import BacktestEngine, BacktestConfig, BacktestResult
from .metrics import PerformanceMetrics
from .walk_forward import WalkForwardValidator, WalkForwardResult
from .monte_carlo import MonteCarloAnalyzer, MonteCarloResult
from .data_loader import DataLoader, DataConfig

__version__ = "1.0.0"
__author__ = "BARAKA AI"

__all__ = [
    "BacktestEngine",
    "BacktestConfig",
    "BacktestResult",
    "PerformanceMetrics",
    "WalkForwardValidator",
    "WalkForwardResult",
    "MonteCarloAnalyzer",
    "MonteCarloResult",
    "DataLoader",
    "DataConfig",
]
