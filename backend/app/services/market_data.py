"""Market data service with WebSocket support and simulated data generation."""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import numpy as np

from app.core.config import settings


class MarketDataService:
    """Service for managing market data, WebSocket connections, and simulated data."""

    def __init__(self):
        self._price_cache: Dict[str, float] = {}
        self._subscribers: Dict[str, List] = {}
        self._running = False
        self._ws_connections: Dict[str, List] = {}
        self._simulated_symbols = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT",
            "XRP/USDT", "ADA/USDT", "DOGE/USDT", "DOT/USDT",
        ]
        self._base_prices = {
            "BTC/USDT": 65000.0,
            "ETH/USDT": 3500.0,
            "BNB/USDT": 600.0,
            "SOL/USDT": 150.0,
            "XRP/USDT": 0.55,
            "ADA/USDT": 0.45,
            "DOGE/USDT": 0.12,
            "DOT/USDT": 7.5,
        }

    async def get_markets(self, search: Optional[str] = None) -> List[dict]:
        """Get list of available markets."""
        markets = []
        for symbol in self._simulated_symbols:
            if search and search.upper() not in symbol:
                continue
            price = await self.get_current_price(symbol)
            markets.append(
                {
                    "symbol": symbol,
                    "price": price,
                    "change_24h": round(random.uniform(-5, 5), 2),
                    "change_percent_24h": round(random.uniform(-10, 10), 2),
                    "high_24h": round(price * 1.05, 2),
                    "low_24h": round(price * 0.95, 2),
                    "volume_24h": round(random.uniform(1000000, 100000000), 2),
                    "timestamp": datetime.now(timezone.utc),
                }
            )
        return markets

    async def get_market_data(self, symbol: str) -> Optional[dict]:
        """Get detailed market data for a symbol."""
        if symbol not in self._simulated_symbols:
            return None

        price = await self.get_current_price(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "change_24h": round(random.uniform(-5, 5), 2),
            "change_percent_24h": round(random.uniform(-10, 10), 2),
            "high_24h": round(price * 1.05, 2),
            "low_24h": round(price * 0.95, 2),
            "volume_24h": round(random.uniform(1000000, 100000000), 2),
            "timestamp": datetime.now(timezone.utc),
        }

    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        if symbol not in self._price_cache:
            base = self._base_prices.get(symbol, 100.0)
            self._price_cache[symbol] = base

        # Add small random movement
        current = self._price_cache[symbol]
        change = random.uniform(-0.001, 0.001)
        new_price = current * (1 + change)
        self._price_cache[symbol] = new_price
        return round(new_price, 8)

    async def get_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
    ) -> List[dict]:
        """Get candlestick data for a symbol."""
        candles = []
        base_price = self._base_prices.get(symbol, 100.0)
        now = datetime.now(timezone.utc)

        # Parse timeframe to minutes
        tf_minutes = self._parse_timeframe(timeframe)

        for i in range(limit):
            timestamp = now - timedelta(minutes=tf_minutes * (limit - i))
            volatility = base_price * 0.02

            open_price = base_price * (1 + random.uniform(-0.01, 0.01))
            close_price = open_price * (1 + random.uniform(-0.01, 0.01))
            high_price = max(open_price, close_price) + random.uniform(0, volatility * 0.5)
            low_price = min(open_price, close_price) - random.uniform(0, volatility * 0.5)
            volume = random.uniform(1000, 100000)

            candles.append(
                {
                    "timestamp": timestamp,
                    "open": round(open_price, 8),
                    "high": round(high_price, 8),
                    "low": round(low_price, 8),
                    "close": round(close_price, 8),
                    "volume": round(volume, 2),
                }
            )

            base_price = close_price

        return candles

    async def get_orderbook(self, symbol: str, depth: int = 20) -> dict:
        """Get order book data."""
        price = await self.get_current_price(symbol)
        spread = price * 0.001

        bids = []
        asks = []

        for i in range(depth):
            bid_price = price - spread * (i + 1) / 2
            ask_price = price + spread * (i + 1) / 2
            bid_size = random.uniform(0.1, 10.0)
            ask_size = random.uniform(0.1, 10.0)

            bids.append({"price": round(bid_price, 8), "size": round(bid_size, 4)})
            asks.append({"price": round(ask_price, 8), "size": round(ask_size, 4)})

        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.now(timezone.utc),
        }

    async def get_recent_trades(self, symbol: str, limit: int = 50) -> List[dict]:
        """Get recent trades."""
        price = await self.get_current_price(symbol)
        trades = []

        for i in range(limit):
            trade_price = price * (1 + random.uniform(-0.002, 0.002))
            side = "buy" if random.random() > 0.5 else "sell"
            quantity = random.uniform(0.001, 5.0)
            timestamp = datetime.now(timezone.utc) - timedelta(seconds=i * random.uniform(1, 10))

            trades.append(
                {
                    "id": f"trade_{i}",
                    "symbol": symbol,
                    "price": round(trade_price, 8),
                    "quantity": round(quantity, 8),
                    "side": side,
                    "timestamp": timestamp,
                }
            )

        return trades

    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to minutes."""
        unit = timeframe[-1]
        value = int(timeframe[:-1])

        multipliers = {
            "m": 1,
            "h": 60,
            "d": 1440,
            "w": 10080,
        }

        return value * multipliers.get(unit, 60)

    async def start_websocket(self, symbol: str, callback) -> None:
        """Start WebSocket connection for real-time data."""
        if symbol not in self._ws_connections:
            self._ws_connections[symbol] = []
        self._ws_connections[symbol].append(callback)

    async def stop_websocket(self, symbol: str, callback) -> None:
        """Stop WebSocket connection."""
        if symbol in self._ws_connections:
            self._ws_connections[symbol] = [
                cb for cb in self._ws_connections[symbol] if cb != callback
            ]

    async def broadcast_price(self, symbol: str, price: float) -> None:
        """Broadcast price update to all subscribers."""
        if symbol in self._ws_connections:
            for callback in self._ws_connections[symbol]:
                try:
                    await callback({"symbol": symbol, "price": price})
                except Exception:
                    pass

    async def start_simulation(self) -> None:
        """Start simulated market data feed."""
        self._running = True
        while self._running:
            for symbol in self._simulated_symbols:
                new_price = await self.get_current_price(symbol)
                await self.broadcast_price(symbol, new_price)
            await asyncio.sleep(1)

    def stop_simulation(self) -> None:
        """Stop simulated market data feed."""
        self._running = False
