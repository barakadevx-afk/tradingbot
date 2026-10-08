\"\"\"BARAKA AI - Backend Tests\"\"\"
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get('/api/v1/system/health')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data


def test_register_validation():
    response = client.post('/api/v1/auth/register', json={
        'email': 'invalid',
        'password': 'short',
        'full_name': ''
    })
    assert response.status_code == 422


def test_login_missing_user():
    response = client.post('/api/v1/auth/login', json={
        'email': 'nonexistent@test.com',
        'password': 'password123'
    })
    assert response.status_code == 401


def test_markets_endpoint():
    response = client.get('/api/v1/markets')
    assert response.status_code in [200, 401]


def test_signals_endpoint():
    response = client.get('/api/v1/signals')
    assert response.status_code in [200, 401]


def test_risk_endpoint():
    response = client.get('/api/v1/risk')
    assert response.status_code in [200, 401]


def test_kill_switch_status():
    response = client.get('/api/v1/kill-switch/status')
    assert response.status_code in [200, 401]


def test_paper_status():
    response = client.get('/api/v1/paper/status')
    assert response.status_code in [200, 401]


def test_strategies_endpoint():
    response = client.get('/api/v1/strategies')
    assert response.status_code in [200, 401]


def test_models_endpoint():
    response = client.get('/api/v1/models')
    assert response.status_code in [200, 401]


def test_audit_logs_endpoint():
    response = client.get('/api/v1/system/audit-logs')
    assert response.status_code in [200, 401]
