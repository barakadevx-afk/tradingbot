"""Tests for market data endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_markets(client: AsyncClient, test_user: User):
    """Test getting market list."""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/markets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_market_detail(client: AsyncClient, test_user: User):
    """Test getting market detail."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/markets/BTC/USDT",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC/USDT"
    assert "price" in data


@pytest.mark.asyncio
async def test_get_candles(client: AsyncClient, test_user: User):
    """Test getting candlestick data."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/markets/BTC/USDT/candles",
        params={"timeframe": "1h", "limit": 50},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "open" in data[0]
    assert "high" in data[0]
    assert "low" in data[0]
    assert "close" in data[0]
