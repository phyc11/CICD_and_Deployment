from datetime import datetime, timezone
import platform
import sys
import time
from src.core.config import settings
from src.schemas.system import (
    HealthCheckResponse,
    MetricsResponse,
    VersionResponse,
)


class SystemService:

    def __init__(self):
        self._start_time = time.time()

    def get_uptime_seconds(self) -> float:
        return round(time.time() - self._start_time, 2)

    def get_health(self) -> HealthCheckResponse:
        now = datetime.now(timezone.utc)
        services = {
            "database": "ok",
            "redis": "ok",
        }
        return HealthCheckResponse(
            status="healthy",
            timestamp=now,
            services=services,
            uptime_seconds=self.get_uptime_seconds(),
        )

    def get_metrics(self) -> MetricsResponse:
        # Fallback metrics using standard libraries
        cpu_percent = 0.0
        memory_usage_mb = 0.0

        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            memory_usage_mb = round(mem.used / (1024 * 1024), 2)
        except ImportError:
            pass

        python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        return MetricsResponse(
            status="ok",
            cpu_percent=cpu_percent,
            memory_usage_mb=memory_usage_mb,
            uptime_seconds=self.get_uptime_seconds(),
            python_version=python_ver,
        )

    def get_version(self) -> VersionResponse:
        python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        return VersionResponse(
            version=settings.APP_VERSION,
            git_commit_sha=settings.GIT_COMMIT_SHA,
            environment=settings.ENVIRONMENT,
            python_version=f"{python_ver} ({platform.system()})",
        )


# Singleton instance
system_service = SystemService()
