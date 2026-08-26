from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from src.schemas.auth import UserResponse


class UserUpdateMeRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    old_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=6, max_length=128)


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(..., description="Role value: 'user' or 'admin'")


class UserPaginatedResponse(BaseModel):
    items: List[UserResponse]
    total: int
    skip: int
    limit: int
