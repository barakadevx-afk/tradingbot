"""Tests for signal endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_signals(client: AsyncClient, test_user: User):
    """Test getting signals list."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/signals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_signal(client: AsyncClient, test_user: User):
    """Test creating a signal."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/signals",
        json={
            "symbol": "BTC/USDT",
            "signal_type": "buy",
            "source": "manual",
            "confidence": 0.85,
            "entry_price": 65000,
            "target_price": 70000,
            "stop_loss": 63000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "BTC/USDT"
    assert data["signal_type"] == "buy"
