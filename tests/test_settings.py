import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.schemas.auth import UserRegisterRequest
from src.services.auth_service import auth_service
from src.services.settings_service import settings_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    auth_service.reset_state()
    settings_service.reset_state()
    yield
    auth_service.reset_state()
    settings_service.reset_state()


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


def test_get_public_settings_success():
    response = client.get("/api/v1/settings/public")
    assert response.status_code == 200
    data = response.json()["settings"]
    assert "maintenance_mode" in data
    assert "allow_user_registration" in data
    assert "app_name" in data
    # Private settings should not be exposed
    assert "enable_audit_logging" not in data


def test_get_all_settings_unauthorized_fails():
    response = client.get("/api/v1/settings/")
    assert response.status_code == 401


def test_get_all_settings_non_admin_forbidden():
    user_token = _create_user_and_get_token("regularuser", role="user")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/settings/", headers=headers)
    assert response.status_code == 403


def test_get_all_settings_admin_success():
    admin_token = _create_user_and_get_token("adminuser", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/settings/", headers=headers)
    assert response.status_code == 200
    keys = [item["key"] for item in response.json()]
    assert "enable_audit_logging" in keys
    assert "maintenance_mode" in keys


def test_update_setting_admin_success():
    admin_token = _create_user_and_get_token("adminuser2", role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    put_payload = {
        "value": True,
        "description": "Enable maintenance mode for deployment",
    }
    response = client.put(
        "/api/v1/settings/maintenance_mode", json=put_payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "maintenance_mode"
    assert data["value"] is True

    # Verify public settings endpoint reflects updated value
    pub_res = client.get("/api/v1/settings/public")
    assert pub_res.status_code == 200
    assert pub_res.json()["settings"]["maintenance_mode"] is True
