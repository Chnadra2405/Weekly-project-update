from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.auth_service import AuthService

security = HTTPBearer()


def create_get_current_user(auth_service: AuthService):
    """Factory to create get_current_user with auth_service bound."""
    def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> dict:
        token = credentials.credentials
        payload = auth_service.decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            )
        return payload
    return get_current_user


def create_get_current_user_id(get_current_user_func):
    """Factory to create get_current_user_id with get_current_user bound."""
    def get_current_user_id(
        current_user: Annotated[dict, Depends(get_current_user_func)]
    ) -> UUID:
        return UUID(current_user["sub"])
    return get_current_user_id


def create_require_role(get_current_user_func):
    """Factory to create role requirement checker."""
    def require_role(required_role: str | list[str]):
        def check_role(
            current_user: Annotated[dict, Depends(get_current_user_func)]
        ) -> dict:
            user_role = current_user.get("role")
            required_roles = [required_role] if isinstance(required_role, str) else required_role
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions.",
                )
            return current_user
        return check_role
    return require_role
