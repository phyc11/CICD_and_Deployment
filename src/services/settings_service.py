from datetime import datetime, timezone
from typing import Dict, List
from src.schemas.settings import (
    PublicSettingsResponse,
    SettingItemResponse,
    SettingUpdateRequest,
)


class SettingsService:

    def __init__(self):
        self._settings: Dict[str, dict] = {}
        self._init_defaults()

    def _init_defaults(self):
        now = datetime.now(timezone.utc)
        defaults = [
            {
                "key": "maintenance_mode",
                "value": False,
                "description": "Maintenance mode status",
                "is_public": True,
                "updated_at": now,
            },
            {
                "key": "allow_user_registration",
                "value": True,
                "description": "Allow new user registrations",
                "is_public": True,
                "updated_at": now,
            },
            {
                "key": "max_upload_size_mb",
                "value": 10,
                "description": "Max file upload size in MB",
                "is_public": True,
                "updated_at": now,
            },
            {
                "key": "enable_audit_logging",
                "value": True,
                "description": "Enable internal audit logging",
                "is_public": False,
                "updated_at": now,
            },
            {
                "key": "app_name",
                "value": "FastAPI CI/CD Demo",
                "description": "Application display name",
                "is_public": True,
                "updated_at": now,
            },
        ]
        for item in defaults:
            self._settings[item["key"]] = item

    def reset_state(self):
        self._settings.clear()
        self._init_defaults()

    def get_public_settings(self) -> PublicSettingsResponse:
        public_dict = {
            item["key"]: item["value"]
            for item in self._settings.values()
            if item["is_public"]
        }
        return PublicSettingsResponse(settings=public_dict)

    def get_all_settings(self) -> List[SettingItemResponse]:
        return [SettingItemResponse(**item) for item in self._settings.values()]

    def get_setting_by_key(self, key: str) -> SettingItemResponse:
        if key not in self._settings:
            raise ValueError(f"Setting with key '{key}' not found")
        return SettingItemResponse(**self._settings[key])

    def update_setting(
        self, key: str, req: SettingUpdateRequest
    ) -> SettingItemResponse:
        now = datetime.now(timezone.utc)
        if key in self._settings:
            item = self._settings[key]
            item["value"] = req.value
            if req.description is not None:
                item["description"] = req.description
            item["updated_at"] = now
        else:
            item = {
                "key": key,
                "value": req.value,
                "description": req.description or f"Custom setting {key}",
                "is_public": False,
                "updated_at": now,
            }
            self._settings[key] = item

        return SettingItemResponse(**item)


# Singleton instance
settings_service = SettingsService()
