from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.contracts import IdempotencyConflictError, SubmitCommand, SubmitResult
from app.domain import ProjectUpdate
from app.presentation.api import create_project_update_router


class FakeSubmit:
    def __init__(self, replayed: bool = False, conflict: bool = False) -> None:
        self.replayed = replayed
        self.conflict = conflict
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
            start_of_week=command.start_of_week,
            end_of_week=command.end_of_week,
            team_project=command.team_project,
            achievements=command.achievements,
            initiatives=command.initiatives,
            next_weeks_plan=command.next_weeks_plan,
            created_at=now,
            updated_at=now,
        )
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
        "start_of_week": "2026-07-20",
        "end_of_week": "2026-07-26",
        "team_project": "Rights Management API",
        "achievements": "Released version 1.0",
        "initiatives": "Started US development",
        "next_weeks_plan": "Complete API testing",
    }


def test_create_returns_all_persisted_record_data() -> None:
    submit = FakeSubmit()

    response = client_for(submit).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
    )

    assert response.status_code == 201
    assert response.json().keys() == {
        "id", "start_of_week", "end_of_week", "team_project", "achievements",
        "initiatives", "next_weeks_plan", "created_at", "updated_at",
    }
    assert response.json()["start_of_week"] == "2026-07-20"
    assert response.json()["next_weeks_plan"] == "Complete API testing"
    assert submit.command is not None
    assert submit.command.start_of_week == date(2026, 7, 20)


def test_matching_replay_returns_replay_header() -> None:
    response = client_for(FakeSubmit(replayed=True)).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
    )

    assert response.status_code == 200
    assert response.headers["Idempotent-Replayed"] == "true"


def test_invalid_week_range_returns_unprocessable_entity() -> None:
    invalid = form_data() | {"end_of_week": "2026-07-27"}
    response = client_for(FakeSubmit()).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=invalid,
    )

    assert response.status_code == 422
    assert "exactly seven inclusive days" in response.json()["detail"]


def test_conflicting_replay_returns_conflict() -> None:
    response = client_for(FakeSubmit(conflict=True)).post(
        "/api/v1/project-updates",
        headers={"Idempotency-Key": "request-1"},
        data=form_data(),
    )

    assert response.status_code == 409
    assert "different content" in response.json()["detail"]