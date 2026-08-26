from datetime import datetime, timedelta, timezone
import os
import uuid

from fastapi import UploadFile
import jwt
from src.core.config import settings
from src.schemas.storage import FileUploadResponse, PresignedUrlResponse


class StorageService:

    def __init__(self):
        self._files: dict[str, dict] = {}
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def reset_state(self):
        self._files.clear()
        if os.path.exists(self.upload_dir):
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
        else:
            os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file: UploadFile, uploader_id: str) -> FileUploadResponse:
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename or "")[1]
        saved_filename = f"{file_id}{ext}"
        file_path = os.path.join(self.upload_dir, saved_filename)

        # Read file contents and write to disk
        contents = file.file.read()
        size_bytes = len(contents)

        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise ValueError(
                f"File size exceeds limit of {settings.MAX_FILE_SIZE_MB}MB"
            )

        with open(file_path, "wb") as f:
            f.write(contents)

        now = datetime.now(timezone.utc)
        file_url = f"/api/v1/storage/download/{file_id}"
        content_type = file.content_type or "application/octet-stream"

        file_metadata = {
            "file_id": file_id,
            "filename": file.filename or "unknown",
            "saved_filename": saved_filename,
            "file_path": file_path,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "uploader_id": uploader_id,
            "uploaded_at": now,
            "file_url": file_url,
        }
        self._files[file_id] = file_metadata

        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename or "unknown",
            file_url=file_url,
            content_type=content_type,
            size_bytes=size_bytes,
            uploaded_at=now,
        )

    def generate_presigned_url(
        self, file_id: str, expires_in: int = settings.PRESIGNED_URL_EXPIRE_SECONDS
    ) -> PresignedUrlResponse:
        if file_id not in self._files:
            raise ValueError("File not found")

        meta = self._files[file_id]
        expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        token_data = {
            "file_id": file_id,
            "exp": expire_at,
            "type": "presigned_download",
        }
        signed_token = jwt.encode(
            token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        download_url = f"/api/v1/storage/download/{file_id}?token={signed_token}"

        return PresignedUrlResponse(
            file_id=file_id,
            filename=meta["filename"],
            download_url=download_url,
            expires_at=expire_at,
            expires_in_seconds=expires_in,
        )

    def verify_download_token(self, file_id: str, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.PyJWTError:
            raise ValueError("Invalid or expired download token")

        if payload.get("type") != "presigned_download":
            raise ValueError("Invalid token type")

        if payload.get("file_id") != file_id:
            raise ValueError("Token does not match requested file")

        if file_id not in self._files:
            raise ValueError("File not found")

        return self._files[file_id]

    def get_file_info(self, file_id: str) -> dict:
        if file_id not in self._files:
            raise ValueError("File not found")
        return self._files[file_id]


# Singleton instance
storage_service = StorageService()
