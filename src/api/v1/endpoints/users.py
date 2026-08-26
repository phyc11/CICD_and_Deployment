from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.core.security import get_current_user, require_admin
from src.schemas.auth import UserResponse
from src.schemas.users import (
    UserPaginatedResponse,
    UserRoleUpdateRequest,
    UserUpdateMeRequest,
)
from src.services.auth_service import auth_service

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def read_current_user_me(
    current_user: UserResponse = Depends(get_current_user),
):
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_current_user_me(
    update_in: UserUpdateMeRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        updated_user = auth_service.update_user_profile(
            user_id=current_user.id, req=update_in
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/",
    response_model=UserPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
def list_users_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin_user: UserResponse = Depends(require_admin),
):
    return auth_service.list_users(skip=skip, limit=limit, search=search)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user_role_admin(
    user_id: str,
    role_in: UserRoleUpdateRequest,
    admin_user: UserResponse = Depends(require_admin),
):
    try:
        updated_user = auth_service.update_user_role(
            user_id=user_id, new_role=role_in.role
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
