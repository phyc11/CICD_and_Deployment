from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from src.core.config import settings
from src.core.security import get_current_user
from src.schemas.auth import UserResponse
from src.schemas.storage import FileUploadResponse, PresignedUrlResponse
from src.services.storage_service import storage_service

router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return storage_service.save_file(file=file, uploader_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    status_code=status.HTTP_200_OK,
)
def get_presigned_url(
    file_id: str = Query(...),
    expires_in: int = Query(settings.PRESIGNED_URL_EXPIRE_SECONDS, ge=1, le=86400),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return storage_service.generate_presigned_url(
            file_id=file_id, expires_in=expires_in
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/download/{file_id}",
    status_code=status.HTTP_200_OK,
)
def download_file(
    file_id: str,
    token: Optional[str] = Query(None),
):
    try:
        if token:
            file_meta = storage_service.verify_download_token(
                file_id=file_id, token=token
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Download token is required",
            )

        return FileResponse(
            path=file_meta["file_path"],
            media_type=file_meta["content_type"],
            filename=file_meta["filename"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
