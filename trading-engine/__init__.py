"""
BARAKA AI Trading Engine
========================

A production-grade algorithmic trading engine supporting:
- Multi-asset market data feeds (simulated & live WebSocket)
- Technical indicators (trend, momentum, volatility, structure)
- Market regime detection
- Strategy execution (trend following, breakout, pullback, mean reversion)
- Signal generation with confidence scoring
- Risk management and position sizing
- Paper trading execution with realistic fill simulation
- Portfolio tracking and analytics

Author: BARAKA AI
Version: 1.0.0
License: Proprietary
"""

__version__ = "1.0.0"
__author__ = "BARAKA AI"

from trading_engine.market_data.data_feed import MarketDataFeed
from trading_engine.market_data.order_book import OrderBook
from trading_engine.indicators.trend import TrendIndicators
from trading_engine.indicators.momentum import MomentumIndicators
from trading_engine.indicators.volatility import VolatilityIndicators
from trading_engine.indicators.structure import StructureIndicators
from trading_engine.regimes.regime_detector import RegimeDetector
from trading_engine.strategies.trend_following import TrendFollowingStrategy
from trading_engine.strategies.breakout import BreakoutStrategy
from trading_engine.strategies.pullback import PullbackStrategy
from trading_engine.strategies.mean_reversion import MeanReversionStrategy
from trading_engine.signals.signal_generator import SignalGenerator
from trading_engine.risk.risk_engine import RiskEngine
from trading_engine.risk.position_sizer import PositionSizer
from trading_engine.risk.stop_loss import StopLossCalculator
from trading_engine.risk.take_profit import TakeProfitCalculator
from trading_engine.execution.paper_executor import PaperExecutor
from trading_engine.execution.order_manager import OrderManager
from trading_engine.execution.exchange_adapter import ExchangeAdapter
from trading_engine.portfolio.portfolio_manager import PortfolioManager

__all__ = [
    "MarketDataFeed",
    "OrderBook",
    "TrendIndicators",
    "MomentumIndicators",
    "VolatilityIndicators",
    "StructureIndicators",
    "RegimeDetector",
    "TrendFollowingStrategy",
    "BreakoutStrategy",
    "PullbackStrategy",
    "MeanReversionStrategy",
    "SignalGenerator",
    "RiskEngine",
    "PositionSizer",
    "StopLossCalculator",
    "TakeProfitCalculator",
    "PaperExecutor",
    "OrderManager",
    "ExchangeAdapter",
    "PortfolioManager",
]
