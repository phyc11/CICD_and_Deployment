import os
from fastapi import FastAPI
import uvicorn

from src.api.v1.endpoints.analytics import router as analytics_router
from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.items import router as items_router
from src.api.v1.endpoints.settings import router as settings_router
from src.api.v1.endpoints.storage import router as storage_router
from src.api.v1.endpoints.system import router as system_router
from src.api.v1.endpoints.users import router as users_router
from src.services.system_service import system_service

app = FastAPI(
    title="FastAPI CI/CD Demo",
    version="0.1.0",
)

# Include Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(items_router, prefix="/api/v1/items", tags=["items"])
app.include_router(storage_router, prefix="/api/v1/storage", tags=["storage"])
app.include_router(system_router, prefix="/api/v1/system", tags=["system"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["settings"])


def add(a: int, b: int) -> int:
    return a + b


@app.get("/")
def read_root():
    return {"status": "OK", "message": "FastAPI service is running"}


@app.get("/health", tags=["system"])
def root_health_check():
    return system_service.get_health()


@app.get("/add")
def add_endpoint(a: int = 0, b: int = 0):
    return {"result": add(a, b)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.app:app", host="0.0.0.0", port=port, reload=False)
