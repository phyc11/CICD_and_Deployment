from datetime import datetime, timedelta, timezone
from typing import Dict
from src.schemas.analytics import (
    GrowthAnalyticsResponse,
    GrowthDataPoint,
    OverviewAnalyticsResponse,
)
from src.services.auth_service import auth_service
from src.services.item_service import item_service
from src.services.storage_service import storage_service
from src.services.system_service import system_service


class AnalyticsService:

    def get_overview(self) -> OverviewAnalyticsResponse:
        total_users = len(auth_service._users)

        items_list = list(item_service._items.values())
        total_items = len(items_list)
        available_items = sum(
            1 for item in items_list if item.get("is_available", True)
        )

        files_list = list(storage_service._files.values())
        total_files = len(files_list)
        total_storage_bytes = sum(
            file_meta.get("size_bytes", 0) for file_meta in files_list
        )
        total_storage_mb = round(total_storage_bytes / (1024 * 1024), 4)

        uptime_seconds = system_service.get_uptime_seconds()

        return OverviewAnalyticsResponse(
            total_users=total_users,
            total_items=total_items,
            available_items=available_items,
            total_files=total_files,
            total_storage_bytes=total_storage_bytes,
            total_storage_mb=total_storage_mb,
            system_uptime_seconds=uptime_seconds,
        )

    def get_growth(
        self, period: str = "daily", days: int = 7
    ) -> GrowthAnalyticsResponse:
        now = datetime.now(timezone.utc)
        growth_map: Dict[str, Dict[str, int]] = {}

        if period.lower() == "monthly":
            # Generate key for last 'days' months
            for i in range(days - 1, -1, -1):
                # Approximate months
                dt = now - timedelta(days=i * 30)
                date_key = dt.strftime("%Y-%m")
                growth_map[date_key] = {"users": 0, "items": 0}
        else:
            # Daily key for last 'days' days
            for i in range(days - 1, -1, -1):
                dt = now - timedelta(days=i)
                date_key = dt.strftime("%Y-%m-%d")
                growth_map[date_key] = {"users": 0, "items": 0}

        # Count users by period
        for user in auth_service._users.values():
            created_at = user.get("created_at")
            if created_at:
                if period.lower() == "monthly":
                    key = created_at.strftime("%Y-%m")
                else:
                    key = created_at.strftime("%Y-%m-%d")
                if key in growth_map:
                    growth_map[key]["users"] += 1

        # Count items by period
        for item in item_service._items.values():
            created_at = item.get("created_at")
            if created_at:
                if period.lower() == "monthly":
                    key = created_at.strftime("%Y-%m")
                else:
                    key = created_at.strftime("%Y-%m-%d")
                if key in growth_map:
                    growth_map[key]["items"] += 1

        data_points = [
            GrowthDataPoint(
                date=k,
                new_users=v["users"],
                new_items=v["items"],
            )
            for k, v in growth_map.items()
        ]

        return GrowthAnalyticsResponse(
            period=period.lower(),
            data_points=data_points,
        )


# Singleton instance
analytics_service = AnalyticsService()
