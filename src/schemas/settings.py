from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class SettingItemResponse(BaseModel):
    key: str
    value: Any
    description: str
    is_public: bool
    updated_at: datetime


class SettingUpdateRequest(BaseModel):
    value: Any
    description: Optional[str] = None


class PublicSettingsResponse(BaseModel):
    settings: Dict[str, Any]
