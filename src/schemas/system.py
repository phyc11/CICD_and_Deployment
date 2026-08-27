from datetime import datetime
from typing import Dict
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    uptime_seconds: float


class MetricsResponse(BaseModel):
    status: str
    cpu_percent: float
    memory_usage_mb: float
    uptime_seconds: float
    python_version: str


class VersionResponse(BaseModel):
    version: str
    git_commit_sha: str
    environment: str
    python_version: str
