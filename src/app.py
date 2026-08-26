import os
from fastapi import FastAPI
import uvicorn

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.items import router as items_router
from src.api.v1.endpoints.storage import router as storage_router
from src.api.v1.endpoints.users import router as users_router

app = FastAPI(
    title="FastAPI CI/CD Demo",
    version="0.1.0",
)

# Include Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(items_router, prefix="/api/v1/items", tags=["items"])
app.include_router(storage_router, prefix="/api/v1/storage", tags=["storage"])


def add(a: int, b: int) -> int:
    return a + b


@app.get("/")
def read_root():
    return {"status": "OK", "message": "FastAPI service is running"}


@app.get("/add")
def add_endpoint(a: int = 0, b: int = 0):
    return {"result": add(a, b)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.app:app", host="0.0.0.0", port=port, reload=False)
