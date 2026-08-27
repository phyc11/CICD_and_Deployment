from typing import List
from pydantic import BaseModel


class OverviewAnalyticsResponse(BaseModel):
    total_users: int
    total_items: int
    available_items: int
    total_files: int
    total_storage_bytes: int
    total_storage_mb: float
    system_uptime_seconds: float


class GrowthDataPoint(BaseModel):
    date: str
    new_users: int
    new_items: int


class GrowthAnalyticsResponse(BaseModel):
    period: str
    data_points: List[GrowthDataPoint]
