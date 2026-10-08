"""
Exchange Adapter
================

Provides a unified interface for connecting to cryptocurrency exchanges.
Currently supports Binance and Bybit with a common API.

All methods are async for non-blocking I/O operations.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    """Supported exchange types."""
    BINANCE = "BINANCE"
    BYBIT = "BYBIT"


@dataclass
class ExchangeConfig:
    """Exchange connection configuration."""
    exchange_type: ExchangeType
    api_key: str
    api_secret: str
    testnet: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3


@dataclass
class Ticker:
    """Ticker data."""
    symbol: str
    bid: float
    ask: float
    last: float
    volume_24h: float
    timestamp: datetime


@dataclass
class Candle:
    """Candle data."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class OrderResponse:
    """Order response from exchange."""
    order_id: str
    symbol: str
    status: str
    side: str
    quantity: float
    filled_quantity: float
    price: float
    fee: float
    timestamp: datetime


class ExchangeAdapter:
    """
    Unified exchange adapter for Binance and Bybit.

    Provides a common interface for:
    - Connection management
    - Market data retrieval
    - Order management
    - Account information
    """

    # Exchange URLs
    BINANCE_TESTNET = "https://testnet.binancefuture.com"
    BINANCE_LIVE = "https://fapi.binance.com"
    BYBIT_TESTNET = "https://api-testnet.bybit.com"
    BYBIT_LIVE = "https://api.bybit.com"

    def __init__(self, config: ExchangeConfig):
        self.config = config
        self._session: Any = None
        self._connected: bool = False
        self._base_url: str = ""
        self._ws_url: str = ""

        self._setup_urls()

        logger.info(f"ExchangeAdapter initialized for {config.exchange_type.value} (testnet={config.testnet})")

    def _setup_urls(self) -> None:
        """Setup URLs based on exchange type and environment."""
        if self.config.exchange_type == ExchangeType.BINANCE:
            self._base_url = self.BINANCE_TESTNET if self.config.testnet else self.BINANCE_LIVE
            self._ws_url = "wss://stream.binancefuture.com" if self.config.testnet else "wss://fstream.binance.com"
        elif self.config.exchange_type == ExchangeType.BYBIT:
            self._base_url = self.BYBIT_TESTNET if self.config.testnet else self.BYBIT_LIVE
            self._ws_url = "wss://stream-testnet.bybit.com" if self.config.testnet else "wss://stream.bybit.com"

    async def connect(self) -> bool:
        """
        Establish connection to the exchange.

        Returns:
            True if connection successful
        """
        try:
            import aiohttp

            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
            )

            # Test connection
            if self.config.exchange_type == ExchangeType.BINANCE:
                async with self._session.get(f"{self._base_url}/fapi/v1/ping") as resp:
                    self._connected = resp.status == 200
            elif self.config.exchange_type == ExchangeType.BYBIT:
                async with self._session.get(f"{self._base_url}/v2/public/time") as resp:
                    self._connected = resp.status == 200

            if self._connected:
                logger.info(f"Connected to {self.config.exchange_type.value}")
            else:
                logger.error(f"Failed to connect to {self.config.exchange_type.value}")

            return self._connected

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from the exchange."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        logger.info(f"Disconnected from {self.config.exchange_type.value}")

    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance.

        Returns:
            Dictionary of asset balances
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                return await self._get_binance_balance()
            elif self.config.exchange_type == ExchangeType.BYBIT:
                return await self._get_bybit_balance()
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise

    async def _get_binance_balance(self) -> Dict[str, float]:
        """Get Binance account balance."""
        timestamp = int(time.time() * 1000)
        query = f"timestamp={timestamp}"
        signature = self._sign_binance(query)

        url = f"{self._base_url}/fapi/v2/balance?{query}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.config.api_key}

        async with self._session.get(url, headers=headers) as resp:
            data = await resp.json()
            return {item["asset"]: float(item["availableBalance"]) for item in data}

    async def _get_bybit_balance(self) -> Dict[str, float]:
        """Get Bybit account balance."""
        timestamp = int(time.time() * 1000)
        params = f"api_key={self.config.api_key}&timestamp={timestamp}"
        signature = self._sign_bybit(params)

        url = f"{self._base_url}/v2/private/wallet/balance?{params}&sign={signature}"

        async with self._session.get(url) as resp:
            data = await resp.json()
            result = data.get("result", {})
            return {k: float(v.get("available_balance", 0)) for k, v in result.items()}

    async def get_ticker(self, symbol: str) -> Ticker:
        """
        Get current ticker for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Ticker data
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                url = f"{self._base_url}/fapi/v1/ticker/bookTicker?symbol={symbol}"
                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return Ticker(
                        symbol=symbol,
                        bid=float(data["bidPrice"]),
                        ask=float(data["askPrice"]),
                        last=float(data["bidPrice"]),  # Approximation
                        volume_24h=0.0,
                        timestamp=datetime.now(timezone.utc),
                    )
            elif self.config.exchange_type == ExchangeType.BYBIT:
                url = f"{self._base_url}/v2/public/tickers?symbol={symbol}"
                async with self._session.get(url) as resp:
                    data = await resp.json()
                    ticker = data["result"][0]
                    return Ticker(
                        symbol=symbol,
                        bid=float(ticker["bid_price"]),
                        ask=float(ticker["ask_price"]),
                        last=float(ticker["last_price"]),
                        volume_24h=float(ticker["volume_24h"]),
                        timestamp=datetime.now(timezone.utc),
                    )
        except Exception as e:
            logger.error(f"Error getting ticker: {e}")
            raise

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, List[Dict[str, float]]]:
        """
        Get order book for a symbol.

        Args:
            symbol: Trading symbol
            limit: Number of levels

        Returns:
            Order book with bids and asks
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                url = f"{self._base_url}/fapi/v1/depth?symbol={symbol}&limit={limit}"
                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return {
                        "bids": [{"price": float(b[0]), "quantity": float(b[1])} for b in data["bids"]],
                        "asks": [{"price": float(a[0]), "quantity": float(a[1])} for a in data["asks"]],
                    }
            elif self.config.exchange_type == ExchangeType.BYBIT:
                url = f"{self._base_url}/v2/public/orderBook/L2?symbol={symbol}&limit={limit}"
                async with self._session.get(url) as resp:
                    data = await resp.json()
                    result = data["result"]
                    return {
                        "bids": [{"price": float(b[0]), "quantity": float(b[1])} for b in result["bids"]],
                        "asks": [{"price": float(a[0]), "quantity": float(a[1])} for a in result["asks"]],
                    }
        except Exception as e:
            logger.error(f"Error getting order book: {e}")
            raise

    async def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
    ) -> List[Candle]:
        """
        Get historical candles.

        Args:
            symbol: Trading symbol
            interval: Candle interval
            limit: Number of candles

        Returns:
            List of Candle objects
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                url = f"{self._base_url}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return [Candle(
                        symbol=symbol,
                        timestamp=datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc),
                        open=float(c[1]),
                        high=float(c[2]),
                        low=float(c[3]),
                        close=float(c[4]),
                        volume=float(c[5]),
                    ) for c in data]
            elif self.config.exchange_type == ExchangeType.BYBIT:
                url = f"{self._base_url}/v2/public/kline/list?symbol={symbol}&interval={interval}&limit={limit}"
                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return [Candle(
                        symbol=symbol,
                        timestamp=datetime.fromtimestamp(int(c["open_time"]), tz=timezone.utc),
                        open=float(c["open"]),
                        high=float(c["high"]),
                        low=float(c["low"]),
                        close=float(c["close"]),
                        volume=float(c["volume"]),
                    ) for c in data["result"]]
        except Exception as e:
            logger.error(f"Error getting candles: {e}")
            raise

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders.

        Args:
            symbol: Filter by symbol

        Returns:
            List of open orders
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                query = f"timestamp={int(time.time() * 1000)}"
                if symbol:
                    query = f"symbol={symbol}&{query}"
                signature = self._sign_binance(query)
                url = f"{self._base_url}/fapi/v1/openOrders?{query}&signature={signature}"
                headers = {"X-MBX-APIKEY": self.config.api_key}

                async with self._session.get(url, headers=headers) as resp:
                    return await resp.json()
            elif self.config.exchange_type == ExchangeType.BYBIT:
                params = f"api_key={self.config.api_key}&timestamp={int(time.time() * 1000)}"
                if symbol:
                    params = f"symbol={symbol}&{params}"
                signature = self._sign_bybit(params)
                url = f"{self._base_url}/v2/private/order/list?{params}&sign={signature}"

                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return data.get("result", {}).get("data", [])
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            raise

    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current positions.

        Args:
            symbol: Filter by symbol

        Returns:
            List of positions
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                query = f"timestamp={int(time.time() * 1000)}"
                signature = self._sign_binance(query)
                url = f"{self._base_url}/fapi/v2/positionRisk?{query}&signature={signature}"
                headers = {"X-MBX-APIKEY": self.config.api_key}

                async with self._session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    if symbol:
                        data = [p for p in data if p["symbol"] == symbol]
                    return data
            elif self.config.exchange_type == ExchangeType.BYBIT:
                params = f"api_key={self.config.api_key}&timestamp={int(time.time() * 1000)}"
                if symbol:
                    params = f"symbol={symbol}&{params}"
                signature = self._sign_bybit(params)
                url = f"{self._base_url}/v2/private/position/list?{params}&sign={signature}"

                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return data.get("result", [])
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise

    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> OrderResponse:
        """
        Create a new order.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            order_type: MARKET, LIMIT, etc.
            quantity: Order quantity
            price: Order price (for limit orders)
            stop_price: Stop price (for stop orders)
            time_in_force: Time in force

        Returns:
            OrderResponse with order details
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                return await self._create_binance_order(symbol, side, order_type, quantity, price, stop_price, time_in_force)
            elif self.config.exchange_type == ExchangeType.BYBIT:
                return await self._create_bybit_order(symbol, side, order_type, quantity, price, stop_price, time_in_force)
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise

    async def _create_binance_order(
        self, symbol: str, side: str, order_type: str, quantity: float,
        price: Optional[float], stop_price: Optional[float], time_in_force: str,
    ) -> OrderResponse:
        """Create order on Binance."""
        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": timestamp,
        }
        if price:
            params["price"] = price
        if stop_price:
            params["stopPrice"] = stop_price
        if time_in_force:
            params["timeInForce"] = time_in_force

        query = "&".join(f"{k}={v}" for k, v in params.items())
        signature = self._sign_binance(query)

        url = f"{self._base_url}/fapi/v1/order?{query}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.config.api_key}

        async with self._session.post(url, headers=headers) as resp:
            data = await resp.json()
            return OrderResponse(
                order_id=str(data["orderId"]),
                symbol=symbol,
                status=data["status"],
                side=side,
                quantity=quantity,
                filled_quantity=float(data.get("executedQty", 0)),
                price=float(data.get("avgPrice", 0)),
                fee=float(data.get("commission", 0)),
                timestamp=datetime.now(timezone.utc),
            )

    async def _create_bybit_order(
        self, symbol: str, side: str, order_type: str, quantity: float,
        price: Optional[float], stop_price: Optional[float], time_in_force: str,
    ) -> OrderResponse:
        """Create order on Bybit."""
        params = {
            "api_key": self.config.api_key,
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "qty": quantity,
            "time_in_force": time_in_force,
            "timestamp": int(time.time() * 1000),
        }
        if price:
            params["price"] = price
        if stop_price:
            params["stop_loss"] = stop_price

        query = "&".join(f"{k}={v}" for k, v in params.items())
        signature = self._sign_bybit(query)

        url = f"{self._base_url}/v2/private/order/create?{query}&sign={signature}"

        async with self._session.post(url) as resp:
            data = await resp.json()
            result = data.get("result", {})
            return OrderResponse(
                order_id=result["order_id"],
                symbol=symbol,
                status=result["order_status"],
                side=side,
                quantity=quantity,
                filled_quantity=float(result.get("cum_exec_qty", 0)),
                price=float(result.get("avg_price", 0)),
                fee=float(result.get("cum_exec_fee", 0)),
                timestamp=datetime.now(timezone.utc),
            )

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel

        Returns:
            True if cancelled successfully
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                timestamp = int(time.time() * 1000)
                query = f"symbol={symbol}&orderId={order_id}&timestamp={timestamp}"
                signature = self._sign_binance(query)
                url = f"{self._base_url}/fapi/v1/order?{query}&signature={signature}"
                headers = {"X-MBX-APIKEY": self.config.api_key}

                async with self._session.delete(url, headers=headers) as resp:
                    return resp.status == 200
            elif self.config.exchange_type == ExchangeType.BYBIT:
                params = f"api_key={self.config.api_key}&symbol={symbol}&order_id={order_id}&timestamp={int(time.time() * 1000)}"
                signature = self._sign_bybit(params)
                url = f"{self._base_url}/v2/private/order/cancel?{params}&sign={signature}"

                async with self._session.post(url) as resp:
                    data = await resp.json()
                    return data.get("ret_code") == 0
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False

    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Get order status.

        Args:
            symbol: Trading symbol
            order_id: Order ID

        Returns:
            Order status details
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                timestamp = int(time.time() * 1000)
                query = f"symbol={symbol}&orderId={order_id}&timestamp={timestamp}"
                signature = self._sign_binance(query)
                url = f"{self._base_url}/fapi/v1/order?{query}&signature={signature}"
                headers = {"X-MBX-APIKEY": self.config.api_key}

                async with self._session.get(url, headers=headers) as resp:
                    return await resp.json()
            elif self.config.exchange_type == ExchangeType.BYBIT:
                params = f"api_key={self.config.api_key}&symbol={symbol}&order_id={order_id}&timestamp={int(time.time() * 1000)}"
                signature = self._sign_bybit(params)
                url = f"{self._base_url}/v2/private/order?{params}&sign={signature}"

                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return data.get("result", {})
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise

    async def get_trade_history(
        self,
        symbol: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get trade history.

        Args:
            symbol: Trading symbol
            limit: Number of trades

        Returns:
            List of trades
        """
        if not self._connected:
            raise ConnectionError("Not connected to exchange")

        try:
            if self.config.exchange_type == ExchangeType.BINANCE:
                timestamp = int(time.time() * 1000)
                query = f"symbol={symbol}&limit={limit}&timestamp={timestamp}"
                signature = self._sign_binance(query)
                url = f"{self._base_url}/fapi/v1/userTrades?{query}&signature={signature}"
                headers = {"X-MBX-APIKEY": self.config.api_key}

                async with self._session.get(url, headers=headers) as resp:
                    return await resp.json()
            elif self.config.exchange_type == ExchangeType.BYBIT:
                params = f"api_key={self.config.api_key}&symbol={symbol}&limit={limit}&timestamp={int(time.time() * 1000)}"
                signature = self._sign_bybit(params)
                url = f"{self._base_url}/v2/private/execution/list?{params}&sign={signature}"

                async with self._session.get(url) as resp:
                    data = await resp.json()
                    return data.get("result", {}).get("trade_list", [])
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            raise

    def _sign_binance(self, query: str) -> str:
        """Create Binance API signature."""
        return hmac.new(
            self.config.api_secret.encode(),
            query.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _sign_bybit(self, params: str) -> str:
        """Create Bybit API signature."""
        return hmac.new(
            self.config.api_secret.encode(),
            params.encode(),
            hashlib.sha256,
        ).hexdigest()

    @property
    def is_connected(self) -> bool:
        """Check if connected to exchange."""
        return self._connected
