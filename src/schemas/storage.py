from datetime import datetime
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_url: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class PresignedUrlResponse(BaseModel):
    file_id: str
    filename: str
    download_url: str
    expires_at: datetime
    expires_in_seconds: int
