from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status

from app.application.auth_schemas import UserLoginRequest, UserRegisterRequest, TokenResponse
from app.application.auth_service import AuthService

logger = logging.getLogger(__name__)


def create_auth_router(auth_service: AuthService) -> APIRouter:
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

    return router
