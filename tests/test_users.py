import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.schemas.auth import UserRegisterRequest
from src.services.auth_service import auth_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    auth_service.reset_state()
    yield
    auth_service.reset_state()


def _create_user_and_get_token(username: str, role: str = "user") -> tuple[str, str]:
    req = UserRegisterRequest(
        email=f"{username}@example.com",
        username=username,
        password="password123",
    )
    user_res = auth_service.register_user(req, role=role)
    token_res = auth_service.authenticate_user(
        username_or_email=username, password="password123"
    )
    return user_res.id, token_res.access_token


def test_get_me_unauthorized_fails():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_me_success():
    user_id, token = _create_user_and_get_token("normaluser")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "normaluser"
    assert data["role"] == "user"


def test_update_me_profile_and_password_success():
    user_id, token = _create_user_and_get_token("updateme")
    headers = {"Authorization": f"Bearer {token}"}

    # Update email & username
    update_payload = {
        "email": "newemail@example.com",
        "username": "newusername",
        "old_password": "password123",
        "new_password": "newpassword456",
    }
    response = client.put("/api/v1/users/me", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"
    assert data["username"] == "newusername"

    # Login with new password must succeed
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "newusername", "password": "newpassword456"},
    )
    assert login_res.status_code == 200


def test_update_me_invalid_old_password_fails():
    _, token = _create_user_and_get_token("badpwduser")
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "old_password": "wrongoldpassword",
        "new_password": "newpassword456",
    }
    response = client.put("/api/v1/users/me", json=update_payload, headers=headers)
    assert response.status_code == 400
    assert "Current password (old_password) is incorrect" in response.json()["detail"]


def test_list_users_regular_user_forbidden():
    _, token = _create_user_and_get_token("regularuser", role="user")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


def test_list_users_admin_success_and_search():
    _, admin_token = _create_user_and_get_token("adminuser", role="admin")
    _create_user_and_get_token("alice", role="user")
    _create_user_and_get_token("bob", role="user")

    headers = {"Authorization": f"Bearer {admin_token}"}

    # List all users
    response = client.get("/api/v1/users/?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Search filter
    search_res = client.get("/api/v1/users/?search=alice", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] == 1
    assert search_data["items"][0]["username"] == "alice"


def test_update_user_role_admin_success():
    target_id, _ = _create_user_and_get_token("targetuser", role="user")
    _, admin_token = _create_user_and_get_token("adminuser2", role="admin")

    headers = {"Authorization": f"Bearer {admin_token}"}

    patch_payload = {"role": "admin"}
    response = client.patch(
        f"/api/v1/users/{target_id}/role", json=patch_payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_id
    assert data["role"] == "admin"
