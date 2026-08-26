from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.core.security import get_current_user
from src.schemas.auth import UserResponse
from src.schemas.items import (
    ItemCreateRequest,
    ItemPaginatedResponse,
    ItemResponse,
    ItemUpdateRequest,
)
from src.services.item_service import item_service

router = APIRouter()


@router.get(
    "/",
    response_model=ItemPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
def list_items_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
):
    return item_service.list_items(
        skip=skip,
        limit=limit,
        category=category,
        is_available=is_available,
        min_price=min_price,
        max_price=max_price,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item_endpoint(
    item_in: ItemCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    return item_service.create_item(req=item_in, owner_id=current_user.id)


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
)
def get_item_endpoint(item_id: str):
    try:
        return item_service.get_item_by_id(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
)
def put_item_endpoint(
    item_id: str,
    item_in: ItemUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return item_service.update_item(
            item_id=item_id, req=item_in, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
)
def patch_item_endpoint(
    item_id: str,
    item_in: ItemUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return item_service.update_item(
            item_id=item_id, req=item_in, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_200_OK,
)
def delete_item_endpoint(
    item_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        item_service.delete_item(item_id=item_id, current_user=current_user)
        return {"message": "Item deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
