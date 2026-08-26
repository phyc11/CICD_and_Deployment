from fastapi import APIRouter, HTTPException, status
from src.schemas.auth import (
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserRegisterRequest):
    try:
        user = auth_service.register_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(login_in: UserLoginRequest):
    try:
        token_response = auth_service.authenticate_user(
            username_or_email=login_in.username,
            password=login_in.password,
        )
        return token_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_token(refresh_in: RefreshTokenRequest):
    try:
        token_response = auth_service.refresh_access_token(
            refresh_token=refresh_in.refresh_token
        )
        return token_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(logout_in: LogoutRequest):
    try:
        auth_service.logout_user(refresh_token=logout_in.refresh_token)
        return {"message": "Successfully logged out"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
