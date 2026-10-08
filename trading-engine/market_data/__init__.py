"""
Market Data Module
==================

Provides market data feeds, order book simulation, and data validation
for the BARAKA AI trading engine.
"""

from trading_engine.market_data.data_feed import MarketDataFeed, OHLCV, DataValidationError
from trading_engine.market_data.order_book import OrderBook, OrderBookLevel

__all__ = [
    "MarketDataFeed",
    "OHLCV",
    "DataValidationError",
    "OrderBook",
    "OrderBookLevel",
]
