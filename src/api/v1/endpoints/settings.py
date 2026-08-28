from typing import List
from fastapi import APIRouter, Depends, status
from src.core.security import require_admin
from src.schemas.auth import UserResponse
from src.schemas.settings import (
    PublicSettingsResponse,
    SettingItemResponse,
    SettingUpdateRequest,
)
from src.services.settings_service import settings_service

router = APIRouter()


@router.get(
    "/public",
    response_model=PublicSettingsResponse,
    status_code=status.HTTP_200_OK,
)
def get_public_settings_endpoint():
    return settings_service.get_public_settings()


@router.get(
    "/",
    response_model=List[SettingItemResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_settings_endpoint(
    admin_user: UserResponse = Depends(require_admin),
):
    return settings_service.get_all_settings()


@router.put(
    "/{key}",
    response_model=SettingItemResponse,
    status_code=status.HTTP_200_OK,
)
def update_setting_endpoint(
    key: str,
    req: SettingUpdateRequest,
    admin_user: UserResponse = Depends(require_admin),
):
    return settings_service.update_setting(key=key, req=req)
