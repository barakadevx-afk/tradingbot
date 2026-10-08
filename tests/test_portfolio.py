"""Tests for portfolio endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_portfolio(client: AsyncClient, test_user: User):
    """Test getting portfolio overview."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/portfolio",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_value" in data
    assert "cash_balance" in data
    assert "positions" in data


@pytest.mark.asyncio
async def test_get_portfolio_performance(client: AsyncClient, test_user: User):
    """Test getting portfolio performance."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/portfolio/performance",
        params={"period": "30d"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_return" in data
    assert "sharpe_ratio" in data
