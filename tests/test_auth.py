import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.services.auth_service import auth_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    auth_service.reset_state()
    yield
    auth_service.reset_state()


def test_register_user_success():
    payload = {
        "email": "user@example.com",
        "username": "testuser",
        "password": "secretpassword123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_username_fails():
    payload = {
        "email": "user1@example.com",
        "username": "dupuser",
        "password": "secretpassword123",
    }
    client.post("/api/v1/auth/register", json=payload)

    payload_dup = {
        "email": "user2@example.com",
        "username": "dupuser",
        "password": "secretpassword123",
    }
    response = client.post("/api/v1/auth/register", json=payload_dup)
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]


def test_register_duplicate_email_fails():
    payload = {
        "email": "dup@example.com",
        "username": "user1",
        "password": "secretpassword123",
    }
    client.post("/api/v1/auth/register", json=payload)

    payload_dup = {
        "email": "dup@example.com",
        "username": "user2",
        "password": "secretpassword123",
    }
    response = client.post("/api/v1/auth/register", json=payload_dup)
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]


def test_login_success():
    reg_payload = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "mypassword123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "username": "loginuser",
        "password": "mypassword123",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password_fails():
    reg_payload = {
        "email": "wrongpwd@example.com",
        "username": "wronguser",
        "password": "correctpassword",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "username": "wronguser",
        "password": "wrongpassword",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid username/email or password" in response.json()["detail"]


def test_refresh_token_success_and_rotation():
    reg_payload = {
        "email": "refresh@example.com",
        "username": "refreshuser",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "refreshuser", "password": "password123"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Call refresh
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 200
    ref_data = ref_res.json()
    assert "access_token" in ref_data
    assert "refresh_token" in ref_data

    # Reuse of old refresh token must fail due to rotation
    ref_res_reuse = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert ref_res_reuse.status_code == 401
    assert "Token has been revoked" in ref_res_reuse.json()["detail"]


def test_logout_success():
    reg_payload = {
        "email": "logout@example.com",
        "username": "logoutuser",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "logoutuser", "password": "password123"},
    )
    refresh_token = login_res.json()["refresh_token"]

    logout_res = client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out"

    # Refresh after logout must fail
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 401
