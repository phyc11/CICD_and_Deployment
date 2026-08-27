import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.schemas.auth import UserRegisterRequest
from src.services.auth_service import auth_service
from src.services.item_service import item_service
from src.services.storage_service import storage_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    auth_service.reset_state()
    item_service.reset_state()
    storage_service.reset_state()
    yield
    auth_service.reset_state()
    item_service.reset_state()
    storage_service.reset_state()


def _create_user_and_get_token(username: str, role: str = "user") -> str:
    req = UserRegisterRequest(
        email=f"{username}@example.com",
        username=username,
        password="password123",
    )
    auth_service.register_user(req, role=role)
    token_res = auth_service.authenticate_user(
        username_or_email=username, password="password123"
    )
    return token_res.access_token


def test_analytics_overview_unauthorized_fails():
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 401


def test_analytics_overview_non_admin_forbidden():
    user_token = _create_user_and_get_token("regularuser", role="user")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/analytics/overview", headers=headers)
    assert response.status_code == 403


def test_analytics_overview_admin_success():
    admin_token = _create_user_and_get_token("adminanalytics", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create item
    client.post(
        "/api/v1/items/",
        json={"title": "Analytics Item", "price": 99.0},
        headers=headers,
    )

    response = client.get("/api/v1/analytics/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 1
    assert data["total_items"] == 1
    assert data["available_items"] == 1
    assert "total_files" in data
    assert "total_storage_bytes" in data
    assert "system_uptime_seconds" in data


def test_analytics_growth_admin_success():
    admin_token = _create_user_and_get_token("adminanalytics2", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        "/api/v1/analytics/growth?period=daily&days=7", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "daily"
    assert len(data["data_points"]) == 7


def test_analytics_growth_monthly_admin_success():
    admin_token = _create_user_and_get_token("adminanalytics3", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        "/api/v1/analytics/growth?period=monthly&days=3", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "monthly"
    assert len(data["data_points"]) == 3
