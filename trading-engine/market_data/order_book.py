"""
Order Book Simulation
=====================

Provides a realistic order book simulation with bid/ask levels,
spread calculation, and market depth analysis.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class OrderBookLevel:
    """Represents a single level in the order book."""
    price: float
    quantity: float
    orders: int = 1


@dataclass
class OrderBookSnapshot:
    """Complete order book snapshot."""
    symbol: str
    bids: List[OrderBookLevel] = field(default_factory=list)
    asks: List[OrderBookLevel] = field(default_factory=list)
    timestamp: Optional[float] = None

    @property
    def best_bid(self) -> Optional[float]:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        return self.asks[0].price if self.asks else None

    @property
    def mid_price(self) -> Optional[float]:
        if self.best_bid and self.best_ask:
            return (self.best_bid + self.best_ask) / 2
        return None

    @property
    def spread(self) -> Optional[float]:
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None

    @property
    def spread_percentage(self) -> Optional[float]:
        mid = self.mid_price
        spread = self.spread
        if mid and spread:
            return (spread / mid) * 100
        return None

    def get_depth(self, levels: int = 10) -> Dict[str, List[Dict]]:
        """Get market depth for visualization."""
        return {
            "bids": [{"price": l.price, "quantity": l.quantity} for l in self.bids[:levels]],
            "asks": [{"price": l.price, "quantity": l.quantity} for l in self.asks[:levels]],
        }


class OrderBook:
    """
    Order book manager for a single symbol.
    Maintains sorted bid/ask levels with efficient updates.
    """

    def __init__(self, symbol: str, base_price: float, depth: int = 20):
        self.symbol = symbol
        self.base_price = base_price
        self.depth = depth
        self.bids: List[OrderBookLevel] = []
        self.asks: List[OrderBookLevel] = []
        self._initialize_book()

    def _initialize_book(self) -> None:
        """Initialize order book with simulated depth."""
        spread = self.base_price * 0.001  # 0.1% spread

        for i in range(self.depth):
            # Bids below mid
            bid_price = self.base_price - spread * (i + 1) / 2
            bid_size = random.uniform(0.1, 10.0) * (1 - i / self.depth)
            self.bids.append(OrderBookLevel(
                price=round(bid_price, 8),
                quantity=round(bid_size, 4),
                orders=random.randint(1, 20)
            ))

            # Asks above mid
            ask_price = self.base_price + spread * (i + 1) / 2
            ask_size = random.uniform(0.1, 10.0) * (1 - i / self.depth)
            self.asks.append(OrderBookLevel(
                price=round(ask_price, 8),
                quantity=round(ask_size, 4),
                orders=random.randint(1, 20)
            ))

    def update(self, price_change_pct: float = 0.0) -> None:
        """Update order book with new price movement."""
        if price_change_pct != 0:
            self.base_price *= (1 + price_change_pct)

        # Re-center the book around new price
        spread = self.base_price * 0.001
        for i in range(self.depth):
            self.bids[i].price = round(self.base_price - spread * (i + 1) / 2, 8)
            self.bids[i].quantity = round(
                random.uniform(0.1, 10.0) * (1 - i / self.depth), 4
            )
            self.asks[i].price = round(self.base_price + spread * (i + 1) / 2, 8)
            self.asks[i].quantity = round(
                random.uniform(0.1, 10.0) * (1 - i / self.depth), 4
            )

    def get_snapshot(self) -> OrderBookSnapshot:
        """Get current order book snapshot."""
        return OrderBookSnapshot(
            symbol=self.symbol,
            bids=self.bids.copy(),
            asks=self.asks.copy(),
            timestamp=__import__('time').time()
        )

    def get_volume_at_price(self, price: float, side: str = "both") -> float:
        """Get total volume at a specific price level."""
        volume = 0.0
        if side in ("bid", "both"):
            for level in self.bids:
                if abs(level.price - price) < 0.01:
                    volume += level.quantity
        if side in ("ask", "both"):
            for level in self.asks:
                if abs(level.price - price) < 0.01:
                    volume += level.quantity
        return volume

    def get_weighted_average_price(self, quantity: float, side: str) -> Optional[float]:
        """Calculate VWAP for a given quantity."""
        levels = self.bids if side == "sell" else self.asks  # Sell hits bids, buy hits asks
        remaining = quantity
        total_cost = 0.0

        for level in levels:
            if remaining <= 0:
                break
            fill_qty = min(remaining, level.quantity)
            total_cost += fill_qty * level.price
            remaining -= fill_qty

        if remaining > 0:
            return None  # Not enough liquidity

        return total_cost / quantity
