from datetime import datetime, timezone
import uuid
from typing import Dict, Optional
from src.schemas.auth import UserResponse
from src.schemas.items import (
    ItemCreateRequest,
    ItemPaginatedResponse,
    ItemResponse,
    ItemUpdateRequest,
)


class ItemService:

    def __init__(self):
        # In-memory store: item_id -> item_dict
        self._items: Dict[str, dict] = {}

    def reset_state(self):
        self._items.clear()

    def create_item(self, req: ItemCreateRequest, owner_id: str) -> ItemResponse:
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        item_data = {
            "id": item_id,
            "title": req.title,
            "description": req.description,
            "price": req.price,
            "category": req.category,
            "is_available": req.is_available,
            "owner_id": owner_id,
            "created_at": now,
            "updated_at": now,
        }
        self._items[item_id] = item_data
        return ItemResponse(**item_data)

    def get_item_by_id(self, item_id: str) -> ItemResponse:
        if item_id not in self._items:
            raise ValueError("Item not found")
        return ItemResponse(**self._items[item_id])

    def list_items(
        self,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        is_available: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> ItemPaginatedResponse:
        filtered = list(self._items.values())

        if category:
            filtered = [
                item
                for item in filtered
                if item["category"].lower() == category.lower()
            ]

        if is_available is not None:
            filtered = [
                item for item in filtered if item["is_available"] == is_available
            ]

        if min_price is not None:
            filtered = [item for item in filtered if item["price"] >= min_price]

        if max_price is not None:
            filtered = [item for item in filtered if item["price"] <= max_price]

        if search:
            s = search.lower()
            filtered = [
                item
                for item in filtered
                if s in item["title"].lower()
                or (item["description"] and s in item["description"].lower())
            ]

        # Sorting
        reverse = order.lower() == "desc"
        if sort_by in ["title", "price", "category", "created_at"]:
            filtered.sort(key=lambda x: x[sort_by], reverse=reverse)

        total = len(filtered)
        paginated = filtered[skip : skip + limit]

        items = [ItemResponse(**item) for item in paginated]

        return ItemPaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    def update_item(
        self,
        item_id: str,
        req: ItemUpdateRequest,
        current_user: UserResponse,
    ) -> ItemResponse:
        if item_id not in self._items:
            raise ValueError("Item not found")

        item = self._items[item_id]

        # Check ownership or admin
        if item["owner_id"] != current_user.id and current_user.role != "admin":
            raise PermissionError("Not authorized to modify this item")

        if req.title is not None:
            item["title"] = req.title
        if req.description is not None:
            item["description"] = req.description
        if req.price is not None:
            item["price"] = req.price
        if req.category is not None:
            item["category"] = req.category
        if req.is_available is not None:
            item["is_available"] = req.is_available

        item["updated_at"] = datetime.now(timezone.utc)
        return ItemResponse(**item)

    def delete_item(self, item_id: str, current_user: UserResponse) -> None:
        if item_id not in self._items:
            raise ValueError("Item not found")

        item = self._items[item_id]

        # Check ownership or admin
        if item["owner_id"] != current_user.id and current_user.role != "admin":
            raise PermissionError("Not authorized to delete this item")

        del self._items[item_id]


# Singleton instance
item_service = ItemService()
