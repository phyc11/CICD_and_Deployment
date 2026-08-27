from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["database"] == "ok"
    assert "uptime_seconds" in data


def test_system_health_check():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "uptime_seconds" in data


def test_system_metrics():
    response = client.get("/api/v1/system/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cpu_percent" in data
    assert "memory_usage_mb" in data
    assert "python_version" in data
    assert "uptime_seconds" in data


def test_system_version():
    response = client.get("/api/v1/system/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"
    assert "git_commit_sha" in data
    assert "environment" in data
    assert "python_version" in data
