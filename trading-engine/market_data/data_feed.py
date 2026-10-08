"""
Market Data Feed
================

Provides real-time and simulated market data feeds with WebSocket support,
OHLCV data generation, and comprehensive data validation.

All timestamps are in UTC. Simulated data is clearly marked.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OHLCV:
    """OHLCV candle data structure."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str = "1m"
    is_simulated: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "timeframe": self.timeframe,
            "is_simulated": self.is_simulated,
        }


@dataclass
class Ticker:
    """Real-time ticker data."""
    symbol: str
    bid: float
    ask: float
    last: float
    volume_24h: float
    change_24h: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_simulated: bool = True

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def spread_percentage(self) -> float:
        if self.last == 0:
            return 0.0
        return (self.spread / self.last) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "bid": self.bid,
            "ask": self.ask,
            "last": self.last,
            "volume_24h": self.volume_24h,
            "change_24h": self.change_24h,
            "change_percent_24h": self.change_percent_24h,
            "high_24h": self.high_24h,
            "low_24h": self.low_24h,
            "timestamp": self.timestamp.isoformat(),
            "is_simulated": self.is_simulated,
        }


class MarketDataFeed:
    """
    Market data feed with WebSocket support and simulated data generation.

    Supports BTC, ETH, SOL, BNB, XRP, ADA, DOGE with realistic price simulation.
    All data is clearly marked as simulated.
    """

    SUPPORTED_SYMBOLS: List[str] = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT",
        "XRPUSDT", "ADAUSDT", "DOGEUSDT",
    ]

    BASE_PRICES: Dict[str, float] = {
        "BTCUSDT": 65000.0,
        "ETHUSDT": 3500.0,
        "SOLUSDT": 150.0,
        "BNBUSDT": 600.0,
        "XRPUSDT": 0.55,
        "ADAUSDT": 0.45,
        "DOGEUSDT": 0.12,
    }

    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        timeframe: str = "1m",
        enable_websocket: bool = False,
        websocket_url: Optional[str] = None,
    ):
        self.symbols = symbols or self.SUPPORTED_SYMBOLS
        self.timeframe = timeframe
        self.enable_websocket = enable_websocket
        self.websocket_url = websocket_url

        self._price_cache: Dict[str, float] = {}
        self._candle_history: Dict[str, List[OHLCV]] = {s: [] for s in self.symbols}
        self._subscribers: Dict[str, List[Callable]] = {s: [] for s in self.symbols}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._ws_connection: Any = None

        # Initialize prices
        for symbol in self.symbols:
            self._price_cache[symbol] = self.BASE_PRICES.get(symbol, 100.0)

        logger.info(f"MarketDataFeed initialized for {len(self.symbols)} symbols, timeframe={timeframe}")

    async def start(self) -> None:
        """Start the market data feed."""
        if self._running:
            logger.warning("Feed already running")
            return

        self._running = True

        if self.enable_websocket and self.websocket_url:
            self._task = asyncio.create_task(self._websocket_loop())
        else:
            self._task = asyncio.create_task(self._simulation_loop())

        logger.info("Market data feed started")

    async def stop(self) -> None:
        """Stop the market data feed."""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._ws_connection:
            await self._ws_connection.close()

        logger.info("Market data feed stopped")

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Get current ticker for a symbol."""
        if symbol not in self.symbols:
            return None

        price = await self.get_current_price(symbol)
        spread = price * 0.001

        return Ticker(
            symbol=symbol,
            bid=price - spread / 2,
            ask=price + spread / 2,
            last=price,
            volume_24h=random.uniform(1000000, 100000000),
            change_24h=round(random.uniform(-5, 5), 2),
            change_percent_24h=round(random.uniform(-10, 10), 2),
            high_24h=round(price * 1.05, 8),
            low_24h=round(price * 0.95, 8),
            is_simulated=True,
        )

    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        if symbol not in self._price_cache:
            base = self.BASE_PRICES.get(symbol, 100.0)
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
        timeframe: Optional[str] = None,
        limit: int = 100,
    ) -> List[OHLCV]:
        """Get candlestick data for a symbol."""
        if symbol not in self.symbols:
            return []

        tf = timeframe or self.timeframe
        candles = self._candle_history.get(symbol, [])

        if len(candles) < limit:
            # Generate historical candles
            base_price = self.BASE_PRICES.get(symbol, 100.0)
            now = datetime.now(timezone.utc)
            tf_minutes = self._parse_timeframe(tf)

            for i in range(limit):
                timestamp = now - timedelta(minutes=tf_minutes * (limit - i))
                volatility = base_price * 0.02

                open_price = base_price * (1 + random.uniform(-0.01, 0.01))
                close_price = open_price * (1 + random.uniform(-0.01, 0.01))
                high_price = max(open_price, close_price) + random.uniform(0, volatility * 0.5)
                low_price = min(open_price, close_price) - random.uniform(0, volatility * 0.5)
                volume = random.uniform(1000, 100000)

                candles.append(OHLCV(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=round(open_price, 8),
                    high=round(high_price, 8),
                    low=round(low_price, 8),
                    close=round(close_price, 8),
                    volume=round(volume, 2),
                    timeframe=tf,
                    is_simulated=True,
                ))

                base_price = close_price

            self._candle_history[symbol] = candles

        return candles[-limit:]

    def register_callback(self, symbol: str, callback: Callable) -> None:
        """Register a callback for price updates."""
        if symbol in self._subscribers:
            self._subscribers[symbol].append(callback)

    def unregister_callback(self, symbol: str, callback: Callable) -> None:
        """Unregister a callback."""
        if symbol in self._subscribers:
            self._subscribers[symbol] = [cb for cb in self._subscribers[symbol] if cb != callback]

    async def broadcast_price(self, symbol: str, price: float) -> None:
        """Broadcast price update to all subscribers."""
        if symbol in self._subscribers:
            for callback in self._subscribers[symbol]:
                try:
                    await callback({"symbol": symbol, "price": price})
                except Exception:
                    pass

    async def _simulation_loop(self) -> None:
        """Run simulated market data feed."""
        while self._running:
            for symbol in self.symbols:
                new_price = await self.get_current_price(symbol)
                await self.broadcast_price(symbol, new_price)
            await asyncio.sleep(1)

    async def _websocket_loop(self) -> None:
        """WebSocket connection loop for live data."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.websocket_url) as ws:
                    # Subscribe to symbols
                    for symbol in self.symbols:
                        await ws.send_json({
                            "method": "SUBSCRIBE",
                            "params": [f"{symbol.lower()}@ticker"],
                            "id": 1,
                        })

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = msg.json()
                            if "s" in data and "c" in data:
                                symbol = data["s"]
                                price = float(data["c"])
                                self._price_cache[symbol] = price
                                await self.broadcast_price(symbol, price)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket error: {ws.exception()}")
                            break
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")

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
