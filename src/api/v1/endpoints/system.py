from fastapi import APIRouter, status
from src.schemas.system import (
    HealthCheckResponse,
    MetricsResponse,
    VersionResponse,
)
from src.services.system_service import system_service

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
)
def get_health_status():
    return system_service.get_health()


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
)
def get_system_metrics():
    return system_service.get_metrics()


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
)
def get_system_version():
    return system_service.get_version()
