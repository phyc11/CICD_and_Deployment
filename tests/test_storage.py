import io
import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.schemas.auth import UserRegisterRequest
from src.services.auth_service import auth_service
from src.services.storage_service import storage_service

pytest_plugins = ["pytest_asyncio"]

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    auth_service.reset_state()
    storage_service.reset_state()
    yield
    auth_service.reset_state()
    storage_service.reset_state()


def _create_user_and_get_token(username: str) -> str:
    req = UserRegisterRequest(
        email=f"{username}@example.com",
        username=username,
        password="password123",
    )
    auth_service.register_user(req)
    token_res = auth_service.authenticate_user(
        username_or_email=username, password="password123"
    )
    return token_res.access_token


def test_upload_unauthorized_fails():
    files = {"file": ("test.txt", io.BytesIO(b"Hello World"), "text/plain")}
    response = client.post("/api/v1/storage/upload", files=files)
    assert response.status_code == 401


def test_upload_file_success():
    token = _create_user_and_get_token("uploader")
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"Sample text file content"
    files = {"file": ("document.txt", io.BytesIO(file_content), "text/plain")}

    response = client.post("/api/v1/storage/upload", files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "document.txt"
    assert data["content_type"] == "text/plain"
    assert data["size_bytes"] == len(file_content)
    assert "file_id" in data


def test_get_presigned_url_success():
    token = _create_user_and_get_token("uploader2")
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"Presigned test content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

    upload_res = client.post("/api/v1/storage/upload", files=files, headers=headers)
    file_id = upload_res.json()["file_id"]

    # Generate presigned URL
    res = client.get(
        f"/api/v1/storage/presigned-url?file_id={file_id}&expires_in=600",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["file_id"] == file_id
    assert "download_url" in data
    assert "token=" in data["download_url"]


def test_get_presigned_url_file_not_found_fails():
    token = _create_user_and_get_token("uploader3")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(
        "/api/v1/storage/presigned-url?file_id=nonexistent-id",
        headers=headers,
    )
    assert res.status_code == 404


def test_download_file_via_presigned_token_success():
    token = _create_user_and_get_token("downloader")
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"Binary download content payload"
    files = {
        "file": ("avatar.png", io.BytesIO(file_content), "image/png"),
    }

    upload_res = client.post("/api/v1/storage/upload", files=files, headers=headers)
    file_id = upload_res.json()["file_id"]

    url_res = client.get(
        f"/api/v1/storage/presigned-url?file_id={file_id}", headers=headers
    )
    download_url = url_res.json()["download_url"]

    # Download file using presigned URL
    dl_res = client.get(download_url)
    assert dl_res.status_code == 200
    assert dl_res.content == file_content
    assert dl_res.headers["content-type"] == "image/png"


def test_download_file_invalid_token_fails():
    token = _create_user_and_get_token("downloader2")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("data.csv", io.BytesIO(b"a,b,c"), "text/csv")}
    upload_res = client.post("/api/v1/storage/upload", files=files, headers=headers)
    file_id = upload_res.json()["file_id"]

    # Download with invalid token
    dl_res = client.get(f"/api/v1/storage/download/{file_id}?token=invalid.jwt.token")
    assert dl_res.status_code == 401
