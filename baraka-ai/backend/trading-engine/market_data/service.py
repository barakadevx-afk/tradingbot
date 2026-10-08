"""Market data service with Binance integration and simulation fallback."""
import asyncio
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import random


class MarketDataService:
    """Service for fetching and managing market data."""

    BINANCE_REST_URL = "https://api.binance.com/api/v3"
    BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"

    SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT"]

    def __init__(self):
        self._cache = {}
        self._last_update = {}
        self._is_connected = False
        self._use_simulation = True

    async def connect(self):
        """Connect to market data source."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BINANCE_REST_URL}/ping", timeout=5.0)
                if response.status_code == 200:
                    self._is_connected = True
                    self._use_simulation = False
                    return True
        except Exception:
            pass

        self._use_simulation = True
        self._is_connected = True  # Simulation mode is always "connected"
        return True

    async def disconnect(self):
        """Disconnect from market data source."""
        self._is_connected = False

    def is_data_stale(self, symbol: str, max_age_seconds: int = 60) -> bool:
        """Check if market data is stale."""
        if symbol not in self._last_update:
            return True
        age = (datetime.utcnow() - self._last_update[symbol]).total_seconds()
        return age > max_age_seconds

    async def get_ticker(self, symbol: str) -> dict:
        """Get current ticker data for a symbol."""
        if self._use_simulation:
            return self._generate_simulated_ticker(symbol)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BINANCE_REST_URL}/ticker/24hr",
                    params={"symbol": symbol},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    ticker = {
                        "symbol": symbol,
                        "price": float(data["lastPrice"]),
                        "bid": float(data["bidPrice"]),
                        "ask": float(data["askPrice"]),
                        "volume": float(data["volume"]),
                        "change_24h": float(data["priceChangePercent"]),
                        "high_24h": float(data["highPrice"]),
                        "low_24h": float(data["lowPrice"]),
                        "timestamp": datetime.utcnow(),
                    }
                    self._cache[symbol] = ticker
                    self._last_update[symbol] = datetime.utcnow()
                    return ticker
        except Exception:
            pass

        return self._generate_simulated_ticker(symbol)

    async def get_candles(self, symbol: str, interval: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Get OHLCV candle data."""
        if self._use_simulation:
            return self._generate_simulated_candles(symbol, interval, limit)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BINANCE_REST_URL}/klines",
                    params={"symbol": symbol, "interval": interval, "limit": limit},
                    timeout=15.0
                )
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data, columns=[
                        "open_time", "open", "high", "low", "close", "volume",
                        "close_time", "quote_volume", "trades",
                        "taker_buy_base", "taker_buy_quote", "ignore"
                    ])
                    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
                    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
                    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
                        df[col] = df[col].astype(float)
                    df.set_index("open_time", inplace=True)
                    return df[["open", "high", "low", "close", "volume", "quote_volume", "trades"]]
        except Exception:
            pass

        return self._generate_simulated_candles(symbol, interval, limit)

    async def get_order_book(self, symbol: str, limit: int = 20) -> dict:
        """Get order book data."""
        if self._use_simulation:
            ticker = await self.get_ticker(symbol)
            price = ticker["price"]
            spread = price * 0.001
            return {
                "symbol": symbol,
                "bids": [[price - spread * (i+1), random.uniform(0.1, 5.0)] for i in range(limit)],
                "asks": [[price + spread * (i+1), random.uniform(0.1, 5.0)] for i in range(limit)],
                "timestamp": datetime.utcnow(),
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BINANCE_REST_URL}/depth",
                    params={"symbol": symbol, "limit": limit},
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass

        return await self.get_order_book(symbol, limit)  # Fallback to simulation

    def _generate_simulated_ticker(self, symbol: str) -> dict:
        """Generate simulated ticker data."""
        base_prices = {
            "BTCUSDT": 67500.0, "ETHUSDT": 3450.0, "SOLUSDT": 145.0,
            "BNBUSDT": 580.0, "XRPUSDT": 0.52, "ADAUSDT": 0.45, "DOGEUSDT": 0.12
        }
        base = base_prices.get(symbol, 100.0)
        change = random.uniform(-0.03, 0.03)
        price = base * (1 + change)

        ticker = {
            "symbol": symbol,
            "price": price,
            "bid": price * 0.9995,
            "ask": price * 1.0005,
            "volume": random.uniform(1000000, 50000000),
            "change_24h": change * 100,
            "high_24h": price * 1.02,
            "low_24h": price * 0.98,
            "timestamp": datetime.utcnow(),
            "is_simulated": True,
        }
        self._cache[symbol] = ticker
        self._last_update[symbol] = datetime.utcnow()
        return ticker

    def _generate_simulated_candles(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Generate simulated OHLCV candle data with realistic price action."""
        base_prices = {
            "BTCUSDT": 67500.0, "ETHUSDT": 3450.0, "SOLUSDT": 145.0,
            "BNBUSDT": 580.0, "XRPUSDT": 0.52, "ADAUSDT": 0.45, "DOGEUSDT": 0.12
        }
        base = base_prices.get(symbol, 100.0)

        # Generate timestamps
        end_time = datetime.utcnow()
        interval_minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
        minutes = interval_minutes.get(interval, 60)
        timestamps = [end_time - timedelta(minutes=minutes * i) for i in range(limit, 0, -1)]

        # Generate price series with trend and volatility
        np.random.seed(42)  # Reproducible for demo
        returns = np.random.normal(0.0001, 0.02, limit)
        # Add some trend
        trend = np.sin(np.linspace(0, 4*np.pi, limit)) * 0.005
        returns += trend

        prices = [base]
        for r in returns:
            prices.append(prices[-1] * (1 + r))
        prices = prices[1:]

        # Generate OHLCV
        data = []
        for i, (ts, close) in enumerate(zip(timestamps, prices)):
            volatility = close * 0.01
            open_price = close * (1 + random.uniform(-0.005, 0.005))
            high = max(open_price, close) + random.uniform(0, volatility)
            low = min(open_price, close) - random.uniform(0, volatility)
            volume = random.uniform(100000, 5000000) * (1 + abs(returns[i]) * 10)

            data.append({
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "quote_volume": volume * close,
                "trades": int(random.uniform(1000, 50000)),
            })

        df = pd.DataFrame(data, index=timestamps)
        df.index.name = "open_time"
        return df

    async def get_all_tickers(self) -> list:
        """Get tickers for all supported symbols."""
        tasks = [self.get_ticker(symbol) for symbol in self.SUPPORTED_SYMBOLS]
        return await asyncio.gather(*tasks)
