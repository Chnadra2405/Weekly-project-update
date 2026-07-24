from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, Header, HTTPException, Response, UploadFile, status

from app.application.contracts import IdempotencyConflictError, IncomingFile, SubmitCommand, UploadValidationError
from app.application.services import GetProjectUpdate, SubmitProjectUpdate
from app.domain import DeliveryStatus, ProjectUpdate
from app.domain.exceptions import DomainValidationError


def serialize(update: ProjectUpdate) -> dict[str, object]:
    return {
        "id": str(update.id),
        "employee_name": update.employee_name,
        "employee_email": str(update.employee_email),
        "reporting_month": str(update.reporting_month),
        "team_project": update.team_project,
        "achievements": update.achievements,
        "initiatives": update.initiatives,
        "next_weeks_plan": update.next_weeks_plan,
        "delivery_status": update.delivery_status.value,
        "smtp_message_id": update.smtp_message_id,
        "failure_code": update.failure_code,
        "failure_detail": update.failure_detail,
        "sent_at": update.sent_at,
        "created_at": update.created_at,
        "attachments": [
            {
                "kind": item.kind.value,
                "original_filename": item.original_filename,
                "media_type": item.media_type,
                "size_bytes": item.size_bytes,
                "sha256": item.sha256,
            }
            for item in update.attachments
        ],
    }


def create_project_update_router(submit: SubmitProjectUpdate, get_update: GetProjectUpdate) -> APIRouter:
    router = APIRouter(prefix="/api/v1/project-updates", tags=["project updates"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_update(
        response: Response,
        idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128)],
        employee_name: Annotated[str, Form(min_length=1, max_length=200)],
        employee_email: Annotated[str, Form(min_length=3, max_length=320)],
        reporting_month: Annotated[str, Form(pattern=r"^\d{4}-\d{2}$")],
        team_project: Annotated[str, Form(min_length=1, max_length=300)],
        achievements: Annotated[str, Form(min_length=1, max_length=5000)],
        initiatives: Annotated[str, Form(min_length=1, max_length=5000)],
        next_weeks_plan: Annotated[str, Form(min_length=1, max_length=5000)],
        reference_email: UploadFile | None = File(default=None),
        image: UploadFile | None = File(default=None),
    ) -> dict[str, object]:
        try:
            result = submit.execute(
                SubmitCommand(
                    idempotency_key=idempotency_key,
                    employee_name=employee_name,
                    employee_email=employee_email,
                    reporting_month=reporting_month,
                    team_project=team_project,
                    achievements=achievements,
                    initiatives=initiatives,
                    next_weeks_plan=next_weeks_plan,
                    reference_email=_incoming(reference_email),
                    image=_incoming(image),
                )
            )
        except IdempotencyConflictError as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
        except (DomainValidationError, UploadValidationError) as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
        if result.replayed:
            response.status_code = (
                status.HTTP_202_ACCEPTED
                if result.update.delivery_status is DeliveryStatus.PENDING
                else status.HTTP_200_OK
            )
            response.headers["Idempotent-Replayed"] = "true"
        return serialize(result.update)

    @router.get("/{update_id}")
    def read_update(update_id: UUID) -> dict[str, object]:
        update = get_update.execute(update_id)
        if update is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Project update not found.")
        return serialize(update)

    return router


def _incoming(upload: UploadFile | None) -> IncomingFile | None:
    if upload is None:
        return None
    return IncomingFile(upload.filename or "upload", upload.content_type or "application/octet-stream", upload.file)