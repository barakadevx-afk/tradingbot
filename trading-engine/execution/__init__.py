"""
Execution Module
================

Provides paper trading execution, order management, and exchange adapter
for the BARAKA AI trading engine.
"""

from trading_engine.execution.paper_executor import PaperExecutor, Position, Order, Fill
from trading_engine.execution.order_manager import OrderManager, OrderStatus
from trading_engine.execution.exchange_adapter import ExchangeAdapter, ExchangeConfig

__all__ = [
    "PaperExecutor",
    "Position",
    "Order",
    "Fill",
    "OrderManager",
    "OrderStatus",
    "ExchangeAdapter",
    "ExchangeConfig",
]
