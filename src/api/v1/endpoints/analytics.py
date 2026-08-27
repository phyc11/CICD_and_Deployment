from fastapi import APIRouter, Depends, Query, status
from src.core.security import require_admin
from src.schemas.analytics import (
    GrowthAnalyticsResponse,
    OverviewAnalyticsResponse,
)
from src.schemas.auth import UserResponse
from src.services.analytics_service import analytics_service

router = APIRouter()


@router.get(
    "/overview",
    response_model=OverviewAnalyticsResponse,
    status_code=status.HTTP_200_OK,
)
def get_analytics_overview(
    admin_user: UserResponse = Depends(require_admin),
):
    return analytics_service.get_overview()


@router.get(
    "/growth",
    response_model=GrowthAnalyticsResponse,
    status_code=status.HTTP_200_OK,
)
def get_analytics_growth(
    period: str = Query("daily", pattern="^(daily|monthly)$"),
    days: int = Query(7, ge=1, le=365),
    admin_user: UserResponse = Depends(require_admin),
):
    return analytics_service.get_growth(period=period, days=days)
