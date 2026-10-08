"""Tests for kill switch endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_activate_kill_switch(client: AsyncClient, test_user: User):
    """Test activating kill switch."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/kill-switch/activate",
        params={"reason": "Testing"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Kill switch activated" in data["message"]


@pytest.mark.asyncio
async def test_get_kill_switch_status(client: AsyncClient, test_user: User):
    """Test getting kill switch status."""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/kill-switch/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "is_active" in data
