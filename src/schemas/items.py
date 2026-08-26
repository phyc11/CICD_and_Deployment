from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ItemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str = "general"
    is_available: bool = True


class ItemUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    is_available: Optional[bool] = None


class ItemResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    category: str
    is_available: bool
    owner_id: str
    created_at: datetime
    updated_at: datetime


class ItemPaginatedResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    skip: int
    limit: int
