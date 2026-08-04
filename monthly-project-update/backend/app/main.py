from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.application.services import GetProjectUpdate, SubmitProjectUpdate, SystemClock
from app.infrastructure.database import SqlAlchemyUnitOfWork, create_session_factory
from app.infrastructure.settings import Settings
from app.presentation.api import create_project_update_router


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    session_factory = create_session_factory(config.database_url)
    unit_of_work = SqlAlchemyUnitOfWork(session_factory)
    submit = SubmitProjectUpdate(unit_of_work, SystemClock())

    application = FastAPI(title="Weekly Project Update API", version="0.2.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Idempotency-Key"],
    )
    application.include_router(create_project_update_router(submit, GetProjectUpdate(unit_of_work)))

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