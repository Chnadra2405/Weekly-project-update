from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.contracts import IdempotencyConflictError, SubmitCommand, SubmitResult
from app.domain import EmailAddress, ProjectUpdate, ReportingMonth
from app.presentation.api import create_project_update_router


class FakeSubmit:
    def __init__(self, replayed: bool = False, conflict: bool = False, pending: bool = False) -> None:
        self.replayed = replayed
        self.conflict = conflict
        self.pending = pending
        self.command: SubmitCommand | None = None

    def execute(self, command: SubmitCommand) -> SubmitResult:
        self.command = command
        if self.conflict:
            raise IdempotencyConflictError("The idempotency key was already used with different content.")
        now = datetime.now(UTC)
        update = ProjectUpdate(
            id=uuid4(),
            idempotency_key=command.idempotency_key,
            request_hash="a" * 64,
            employee_name=command.employee_name,
            employee_email=EmailAddress(command.employee_email),
            reporting_month=ReportingMonth.from_html_month(command.reporting_month),
            team_project=command.team_project,
            achievements=command.achievements,
            initiatives=command.initiatives,
            next_weeks_plan=command.next_weeks_plan,
            created_at=now,
            updated_at=now,
        )
        if not self.pending:
            update.mark_sent(f"<{update.id}@example.com>", now)
        return SubmitResult(update, replayed=self.replayed)


class FakeGet:
    def execute(self, update_id: UUID) -> ProjectUpdate | None:
        return None


def client_for(submit: FakeSubmit) -> TestClient:
    app = FastAPI()
    app.include_router(create_project_update_router(submit, FakeGet()))  # type: ignore[arg-type]
    return TestClient(app)


def form_data() -> dict[str, str]:
    return {
        "employee_name": "Ada Lovelace",
        "employee_email": "ada@example.com",
        "reporting_month": "2026-07",
        "team_project": "Rights Management API",
        "achievements": "Released version 1.0",
        "initiatives": "Started US development",
        "next_weeks_plan": "Complete API testing",
    }


def test_create_accepts_multipart_fields_and_optional_files() -> None:
    submit = FakeSubmit()

    response = client_for(submit).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
        files={"image": ("status.png", b"image bytes", "image/png")},
    )

    assert response.status_code == 201
    assert response.json()["delivery_status"] == "SENT"
    assert submit.command is not None
    assert submit.command.image is not None
    assert submit.command.image.filename == "status.png"


def test_matching_replay_returns_replay_header() -> None:
    response = client_for(FakeSubmit(replayed=True)).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
    )

    assert response.status_code == 200
    assert response.headers["Idempotent-Replayed"] == "true"


def test_pending_replay_returns_accepted() -> None:
    response = client_for(FakeSubmit(replayed=True, pending=True)).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
    )

    assert response.status_code == 202
    assert response.json()["delivery_status"] == "PENDING"


def test_conflicting_replay_returns_conflict() -> None:
    response = client_for(FakeSubmit(conflict=True)).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
    )

    assert response.status_code == 409
    assert "different content" in response.json()["detail"]