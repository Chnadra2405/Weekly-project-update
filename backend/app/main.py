from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.application.auth_service import AuthService
from app.application.services import (
    ApproveProjectUpdate,
    CheckExistingReport,
    GetProjectUpdate,
    ListProjectUpdates,
    SubmitProjectUpdate,
    SystemClock,
    UpdateProjectUpdate,
)
from app.infrastructure.database import SqlAlchemyUnitOfWork, create_session_factory
from app.infrastructure.settings import Settings
from app.presentation.api import create_project_update_router
from app.presentation.auth_api import create_auth_router
from app.presentation.dependencies import create_get_current_user


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    session_factory = create_session_factory(config.database_url)
    unit_of_work = SqlAlchemyUnitOfWork(session_factory)
    submit = SubmitProjectUpdate(unit_of_work, SystemClock())
    list_updates = ListProjectUpdates(unit_of_work)
    update_project_update = UpdateProjectUpdate(unit_of_work, SystemClock())
    approve_project_update = ApproveProjectUpdate(unit_of_work)
    check_existing = CheckExistingReport(unit_of_work)
    auth_service = AuthService(
        session_factory=session_factory,
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
        access_token_expire_minutes=config.jwt_access_token_expire_minutes,
    )

    application = FastAPI(title="Weekly Project Update API", version="0.3.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "Idempotency-Key", "Authorization"],
        expose_headers=["Content-Disposition"],
    )

    get_current_user = create_get_current_user(auth_service)

    application.include_router(create_auth_router(auth_service, get_current_user))
    application.include_router(
        create_project_update_router(
            submit,
            GetProjectUpdate(unit_of_work),
            list_updates,
            update_project_update,
            check_existing,
            approve_project_update,
            get_current_user,
            auth_service,
        )
    )

    @application.get("/api/v1/health/live", tags=["health"])
    def live() -> dict[str, str]:
        return {"status": "live"}

    @application.get("/api/v1/health/ready", tags=["health"])
    def ready() -> dict[str, str]:
        try:
            with session_factory() as session:
                session.execute(text("SELECT 1"))
        except Exception as error:
            raise HTTPException(503, "Service dependencies are not ready.") from error
        return {"status": "ready"}

    return application


app = create_app()

