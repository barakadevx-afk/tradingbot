"""Tests for strategy endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_strategies(client: AsyncClient, test_user: User):
    """Test getting strategies list."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/strategies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_strategy(client: AsyncClient, test_user: User):
    """Test creating a strategy."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/strategies",
        json={
            "name": "Test Strategy",
            "strategy_type": "ai",
            "symbols": "BTC/USDT",
            "timeframe": "1h",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Strategy"
