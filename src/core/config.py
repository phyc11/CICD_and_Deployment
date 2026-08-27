import os


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-cicd-demo-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE_MB: int = 10
    PRESIGNED_URL_EXPIRE_SECONDS: int = 3600

    # System & Version settings
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    GIT_COMMIT_SHA: str = os.getenv("GIT_COMMIT_SHA", "dev-commit-sha")


settings = Settings()
