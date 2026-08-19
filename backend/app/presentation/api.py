from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.application.auth_service import AuthService
from app.application.contracts import IdempotencyConflictError, SubmitCommand, UpdateCommand
from app.application.services import (
    CheckExistingReport,
    GetProjectUpdate,
    ListProjectUpdates,
    SubmitProjectUpdate,
    UpdateProjectUpdate,
)
from app.domain import ProjectUpdate
from app.domain.exceptions import DomainValidationError


class UpdateProjectUpdateRequest(BaseModel):
    start_of_week: date
    end_of_week: date
    team_project: str = Field(min_length=1, max_length=300)
    achievements: str = Field(min_length=1, max_length=5000)
    initiatives: str = Field(min_length=1, max_length=5000)
    next_weeks_plan: str = Field(min_length=1, max_length=5000)


def serialize(update: ProjectUpdate, owner_username: str | None = None) -> dict[str, object]:
    return {
        "id": str(update.id),
        "user_id": str(update.user_id) if update.user_id else None,
        "owner_username": owner_username,
        "start_of_week": update.start_of_week,
        "end_of_week": update.end_of_week,
        "team_project": update.team_project,
        "achievements": update.achievements,
        "initiatives": update.initiatives,
        "next_weeks_plan": update.next_weeks_plan,
        "created_at": update.created_at,
        "updated_at": update.updated_at,
    }


def create_project_update_router(
    submit: SubmitProjectUpdate,
    get_update: GetProjectUpdate,
    list_updates_service: ListProjectUpdates,
    update_service: UpdateProjectUpdate,
    check_existing: CheckExistingReport,
    get_current_user,
    auth_service: AuthService,
) -> APIRouter:
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
        current_user: dict = Depends(get_current_user),
    ) -> dict[str, object]:
        current_user_id = UUID(current_user["sub"])
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
                ),
                user_id=current_user_id,
            )
        except IdempotencyConflictError as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        except DomainValidationError as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
        if result.replayed:
            response.status_code = status.HTTP_200_OK
            response.headers["Idempotent-Replayed"] = "true"
        return serialize(result.update)

    @router.get("/check")
    def check_report(
        start_of_week: date,
        team_project: str,
        current_user: dict = Depends(get_current_user),
    ) -> dict[str, object]:
        """Return the existing report for this week+team (any owner), or null."""
        user_id = UUID(current_user["sub"])
        existing = check_existing.execute(user_id, start_of_week, team_project)
        if existing is None:
            return {"exists": False, "report": None}
        owner_username = None
        if existing.user_id is not None:
            usernames = auth_service.get_usernames_by_ids({existing.user_id})
            owner_username = usernames.get(existing.user_id)
        return {"exists": True, "report": serialize(existing, owner_username)}

    @router.get("/{update_id}")
    def read_update(
        update_id: UUID,
        current_user: dict = Depends(get_current_user),
    ) -> dict[str, object]:
        user_id = UUID(current_user["sub"])
        user_role = current_user.get("role")
        update = get_update.execute(update_id)
        if update is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Project update not found.")

        if user_role == "ADMIN":
            return serialize(update)
        elif user_role == "MANAGER":
            team_member_ids = auth_service.get_team_members(user_id)
            if update.user_id not in team_member_ids and update.user_id != user_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized to view this update.")
            return serialize(update)
        elif user_role == "EMPLOYEE":
            if update.user_id != user_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized to view this update.")
            return serialize(update)
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid role.")

    @router.get("")
    def list_updates(
        current_user: dict = Depends(get_current_user),
    ) -> list[dict[str, object]]:
        user_id = UUID(current_user["sub"])
        user_role = current_user.get("role")

        if user_role == "ADMIN":
            updates = list_updates_service.execute()
        elif user_role == "MANAGER":
            visible_user_ids = set(auth_service.get_team_members(user_id)) | {user_id}
            updates = list_updates_service.execute(visible_user_ids)
        elif user_role == "EMPLOYEE":
            updates = list_updates_service.execute({user_id})
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid role.")

        owner_ids = {update.user_id for update in updates if update.user_id is not None}
        usernames = auth_service.get_usernames_by_ids(owner_ids)
        return [serialize(update, usernames.get(update.user_id)) for update in updates]

    @router.put("/{update_id}")
    def update_project_update(
        update_id: UUID,
        request: UpdateProjectUpdateRequest,
        current_user: dict = Depends(get_current_user),
    ) -> dict[str, object]:
        user_id = UUID(current_user["sub"])
        try:
            update = update_service.execute(
                update_id,
                user_id,
                UpdateCommand(
                    start_of_week=request.start_of_week,
                    end_of_week=request.end_of_week,
                    team_project=request.team_project,
                    achievements=request.achievements,
                    initiatives=request.initiatives,
                    next_weeks_plan=request.next_weeks_plan,
                ),
            )
        except DomainValidationError as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
        if update is None:
            existing = get_update.execute(update_id)
            if existing is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Project update not found.")
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the report owner can edit this update.")
        return serialize(update, current_user.get("username"))

    return router
