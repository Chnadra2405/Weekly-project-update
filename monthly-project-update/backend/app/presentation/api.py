from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Header, HTTPException, Response, status

from app.application.contracts import IdempotencyConflictError, SubmitCommand
from app.application.services import GetProjectUpdate, SubmitProjectUpdate
from app.domain import ProjectUpdate
from app.domain.exceptions import DomainValidationError


def serialize(update: ProjectUpdate) -> dict[str, object]:
    return {
        "id": str(update.id),
        "start_of_week": update.start_of_week,
        "end_of_week": update.end_of_week,
        "team_project": update.team_project,
        "achievements": update.achievements,
        "initiatives": update.initiatives,
        "next_weeks_plan": update.next_weeks_plan,
        "created_at": update.created_at,
        "updated_at": update.updated_at,
    }


def create_project_update_router(submit: SubmitProjectUpdate, get_update: GetProjectUpdate) -> APIRouter:
    router = APIRouter(prefix="/api/v1/project-updates", tags=["project updates"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_update(
        response: Response,
        idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128)],
        start_of_week: Annotated[date, Form()],
        end_of_week: Annotated[date, Form()],
        team_project: Annotated[str, Form(min_length=1, max_length=300)],
        achievements: Annotated[str, Form(min_length=1, max_length=5000)],
        initiatives: Annotated[str, Form(min_length=1, max_length=5000)],
        next_weeks_plan: Annotated[str, Form(min_length=1, max_length=5000)],
    ) -> dict[str, object]:
        try:
            result = submit.execute(
                SubmitCommand(
                    idempotency_key=idempotency_key,
                    start_of_week=start_of_week,
                    end_of_week=end_of_week,
                    team_project=team_project,
                    achievements=achievements,
                    initiatives=initiatives,
                    next_weeks_plan=next_weeks_plan,
                )
            )
        except IdempotencyConflictError as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        except DomainValidationError as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
        if result.replayed:
            response.status_code = status.HTTP_200_OK
            response.headers["Idempotent-Replayed"] = "true"
        return serialize(result.update)

    @router.get("/{update_id}")
    def read_update(update_id: UUID) -> dict[str, object]:
        update = get_update.execute(update_id)
        if update is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Project update not found.")
        return serialize(update)

    return router
