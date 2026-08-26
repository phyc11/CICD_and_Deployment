import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.schemas.auth import UserRegisterRequest
from src.services.auth_service import auth_service
from src.services.item_service import item_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    auth_service.reset_state()
    item_service.reset_state()
    yield
    auth_service.reset_state()
    item_service.reset_state()


def _create_user_and_get_token(username: str, role: str = "user") -> tuple[str, str]:
    req = UserRegisterRequest(
        email=f"{username}@example.com",
        username=username,
        password="password123",
    )
    user_res = auth_service.register_user(req, role=role)
    token_res = auth_service.authenticate_user(
        username_or_email=username, password="password123"
    )
    return user_res.id, token_res.access_token


def test_create_item_unauthorized_fails():
    payload = {"title": "Test Item", "price": 99.99}
    response = client.post("/api/v1/items/", json=payload)
    assert response.status_code == 401


def test_create_item_success():
    user_id, token = _create_user_and_get_token("itemowner")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Laptop Dell",
        "description": "High performance laptop",
        "price": 1200.0,
        "category": "electronics",
        "is_available": True,
    }
    response = client.post("/api/v1/items/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["owner_id"] == user_id
    assert "id" in data


def test_get_item_by_id_success():
    _, token = _create_user_and_get_token("seller")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/v1/items/",
        json={"title": "Phone", "price": 500.0},
        headers=headers,
    )
    item_id = create_res.json()["id"]

    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_item_not_found_fails():
    response = client.get("/api/v1/items/nonexistent-id")
    assert response.status_code == 404


def test_list_items_filtering_and_sorting():
    _, token = _create_user_and_get_token("merchant")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/items/",
        json={
            "title": "Book Python",
            "price": 30.0,
            "category": "books",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/items/",
        json={
            "title": "Book FastAPI",
            "price": 50.0,
            "category": "books",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/items/",
        json={
            "title": "Headphones",
            "price": 100.0,
            "category": "electronics",
        },
        headers=headers,
    )

    # Filter by category
    res_books = client.get("/api/v1/items/?category=books")
    assert res_books.status_code == 200
    assert res_books.json()["total"] == 2

    # Filter by min/max price
    res_price = client.get("/api/v1/items/?min_price=40.0&max_price=150.0")
    assert res_price.status_code == 200
    assert res_price.json()["total"] == 2

    # Search filter
    res_search = client.get("/api/v1/items/?search=FastAPI")
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1

    # Sorting by price asc
    res_sort = client.get("/api/v1/items/?sort_by=price&order=asc")
    assert res_sort.status_code == 200
    items = res_sort.json()["items"]
    assert items[0]["price"] == 30.0
    assert items[-1]["price"] == 100.0


def test_update_item_by_owner_success():
    _, owner_token = _create_user_and_get_token("itemowner2")
    headers = {"Authorization": f"Bearer {owner_token}"}

    create_res = client.post(
        "/api/v1/items/",
        json={"title": "Old Title", "price": 10.0},
        headers=headers,
    )
    item_id = create_res.json()["id"]

    put_res = client.put(
        f"/api/v1/items/{item_id}",
        json={"title": "New Title", "price": 15.0},
        headers=headers,
    )
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "New Title"
    assert put_res.json()["price"] == 15.0


def test_update_item_by_other_user_forbidden():
    _, owner_token = _create_user_and_get_token("itemowner3")
    _, stranger_token = _create_user_and_get_token("stranger")

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    stranger_headers = {"Authorization": f"Bearer {stranger_token}"}

    create_res = client.post(
        "/api/v1/items/",
        json={"title": "Private Item", "price": 20.0},
        headers=owner_headers,
    )
    item_id = create_res.json()["id"]

    put_res = client.put(
        f"/api/v1/items/{item_id}",
        json={"title": "Hacked Title"},
        headers=stranger_headers,
    )
    assert put_res.status_code == 403


def test_update_item_by_admin_success():
    _, owner_token = _create_user_and_get_token("itemowner4")
    _, admin_token = _create_user_and_get_token("adminuser", role="admin")

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    create_res = client.post(
        "/api/v1/items/",
        json={"title": "User Item", "price": 20.0},
        headers=owner_headers,
    )
    item_id = create_res.json()["id"]

    patch_res = client.patch(
        f"/api/v1/items/{item_id}",
        json={"title": "Admin Edited Title"},
        headers=admin_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Admin Edited Title"


def test_delete_item_by_owner_success():
    _, owner_token = _create_user_and_get_token("itemowner5")
    headers = {"Authorization": f"Bearer {owner_token}"}

    create_res = client.post(
        "/api/v1/items/",
        json={"title": "Item To Delete", "price": 20.0},
        headers=headers,
    )
    item_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify deleted
    get_res = client.get(f"/api/v1/items/{item_id}")
    assert get_res.status_code == 404


def test_delete_item_by_other_user_forbidden():
    _, owner_token = _create_user_and_get_token("itemowner6")
    _, stranger_token = _create_user_and_get_token("stranger2")

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    stranger_headers = {"Authorization": f"Bearer {stranger_token}"}

    create_res = client.post(
        "/api/v1/items/",
        json={"title": "Protected Item", "price": 20.0},
        headers=owner_headers,
    )
    item_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/items/{item_id}", headers=stranger_headers)
    assert del_res.status_code == 403
