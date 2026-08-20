from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.application.auth_schemas import UserLoginRequest, UserRegisterRequest, TokenResponse
from app.application.auth_service import AuthService

logger = logging.getLogger(__name__)


class AssignDelegateRequest(BaseModel):
    manager_id: str
    delegate_id: str


def create_auth_router(auth_service: AuthService, get_current_user) -> APIRouter:
    router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

    @router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
    def register(request: UserRegisterRequest) -> TokenResponse:
        logger.info(f"Register request for username: {request.username}")
        try:
            user = auth_service.register_user(
                username=request.username,
                email=request.email,
                password=request.password,
                role=request.role,
                team=request.team,
            )
            logger.info(f"User registration result: {user}")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already exists.",
                )
            token = auth_service.create_access_token(user.id, user.username, user.role)
            logger.info(f"Token created for user: {user.username}")
            return TokenResponse(
                access_token=token,
                user_id=str(user.id),
                username=user.username,
                role=user.role,
            )
        except Exception as e:
            logger.error(f"Registration error: {e}", exc_info=True)
            raise

    @router.post("/login", response_model=TokenResponse)
    def login(request: UserLoginRequest) -> TokenResponse:
        user = auth_service.authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
            )
        token = auth_service.create_access_token(user.id, user.username, user.role)
        return TokenResponse(
            access_token=token,
            user_id=str(user.id),
            username=user.username,
            role=user.role,
        )

    @router.get("/users")
    def list_users(
        role: str | None = None,
        current_user: dict = Depends(get_current_user),
    ) -> list[dict]:
        if current_user.get("role") != "APP_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Application Admin can list users.",
            )
        users = auth_service.get_users(role=role)
        return [
            {"id": str(u.id), "username": u.username, "role": u.role}
            for u in users
        ]

    @router.post("/delegate", status_code=status.HTTP_200_OK)
    def assign_delegate(
        request: AssignDelegateRequest,
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        if current_user.get("role") != "APP_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Application Admin can assign delegates.",
            )
        success = auth_service.assign_delegate(
            manager_id=UUID(request.manager_id),
            delegate_id=UUID(request.delegate_id),
            created_by_id=UUID(current_user["sub"]),
        )
        return {"success": success}

    return router
