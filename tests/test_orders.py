"""Tests for order endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, test_user: User):
    """Test creating an order."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/orders",
        json={
            "symbol": "BTC/USDT",
            "order_type": "market",
            "side": "buy",
            "quantity": 0.01,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "BTC/USDT"
    assert data["side"] == "buy"
    assert data["status"] in ["open", "filled"]


@pytest.mark.asyncio
async def test_get_orders(client: AsyncClient, test_user: User):
    """Test getting orders list."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
