from datetime import datetime, timezone
import uuid
from typing import Dict, Optional, Set

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.schemas.auth import (
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:

    def __init__(self):
        # In-memory storage for demonstration & testing
        self._users: Dict[str, dict] = {}  # user_id -> user_dict
        self._revoked_tokens: Set[str] = set()

    def reset_state(self):
        """Utility method to clear in-memory state during test runs."""
        self._users.clear()
        self._revoked_tokens.clear()

    def register_user(self, req: UserRegisterRequest) -> UserResponse:
        # Check duplicate username or email
        for u in self._users.values():
            if u["username"] == req.username:
                raise ValueError("Username already exists")
            if u["email"] == req.email:
                raise ValueError("Email already exists")

        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(req.password)
        now = datetime.now(timezone.utc)

        user_data = {
            "id": user_id,
            "email": req.email,
            "username": req.username,
            "password_hash": hashed_pwd,
            "created_at": now,
        }
        self._users[user_id] = user_data

        return UserResponse(
            id=user_id,
            email=req.email,
            username=req.username,
            created_at=now,
        )

    def authenticate_user(self, username_or_email: str, password: str) -> TokenResponse:
        target_user: Optional[dict] = None
        for u in self._users.values():
            if u["username"] == username_or_email or u["email"] == username_or_email:
                target_user = u
                break

        if not target_user or not verify_password(
            password, target_user["password_hash"]
        ):
            raise ValueError("Invalid username/email or password")

        access_token = create_access_token(subject=target_user["id"])
        refresh_token = create_refresh_token(subject=target_user["id"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        if refresh_token in self._revoked_tokens:
            raise ValueError("Token has been revoked")

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id or user_id not in self._users:
            raise ValueError("User associated with token not found")

        new_access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)

        # Revoke old refresh token to prevent reuse (token rotation)
        self._revoked_tokens.add(refresh_token)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    def logout_user(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        if not payload:
            raise ValueError("Invalid token")

        self._revoked_tokens.add(refresh_token)


# Singleton instance
auth_service = AuthService()
