"""Tests for risk management endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_risk_config(client: AsyncClient, test_user: User):
    """Test getting risk configuration."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/risk/config",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "max_position_size" in data
    assert "risk_per_trade" in data


@pytest.mark.asyncio
async def test_validate_trade(client: AsyncClient, test_user: User):
    """Test trade validation."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/risk/validate",
        params={
            "symbol": "BTC/USDT",
            "quantity": 0.01,
            "price": 65000,
            "side": "buy",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
