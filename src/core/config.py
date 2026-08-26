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


settings = Settings()
