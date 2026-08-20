from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.contracts import IdempotencyConflictError, SubmitCommand, SubmitResult, UpdateCommand
from app.domain import ProjectUpdate
from app.presentation.api import create_project_update_router


class FakeSubmit:
    def __init__(self, replayed: bool = False, conflict: bool = False) -> None:
        self.replayed = replayed
        self.conflict = conflict
        self.command: SubmitCommand | None = None

    def execute(self, command: SubmitCommand, user_id: UUID | None = None) -> SubmitResult:
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
            user_id=user_id,
        )
        return SubmitResult(update, replayed=self.replayed)


class FakeGet:
    def __init__(self, update: ProjectUpdate | None = None) -> None:
        self.update = update

    def execute(self, update_id: UUID) -> ProjectUpdate | None:
        return self.update


class FakeList:
    def __init__(self, updates: list[ProjectUpdate] | None = None) -> None:
        self.updates = updates or []
        self.user_ids: set[UUID] | None = set()

    def execute(self, user_ids: set[UUID] | None = None) -> list[ProjectUpdate]:
        self.user_ids = user_ids
        return self.updates


class FakeUpdate:
    def __init__(self, update: ProjectUpdate | None = None) -> None:
        self.update = update
        self.editor_id: UUID | None = None
        self.editor_role: str | None = None
        self.command: UpdateCommand | None = None

    def execute(self, update_id: UUID, editor_id: UUID, editor_role: str, command: UpdateCommand) -> ProjectUpdate | None:
        self.editor_id = editor_id
        self.editor_role = editor_role
        self.command = command
        return self.update


class FakeApprove:
    def __init__(self, update: ProjectUpdate | None = None) -> None:
        self.update = update

    def execute(self, update_id: UUID, approver_id: UUID) -> ProjectUpdate | None:
        return self.update


class FakeAuthService:
    def __init__(self, team_members: list[UUID] | None = None) -> None:
        self.team_members = team_members or []

    def get_team_members(self, manager_id: UUID) -> list[UUID]:
        return self.team_members

    def get_usernames_by_ids(self, user_ids: set[UUID]) -> dict[UUID, str]:
        return {user_id: f"user-{index}" for index, user_id in enumerate(user_ids, start=1)}

    def get_active_delegation_for_delegate(self, delegate_id: UUID) -> UUID | None:
        return None


class FakeCheckExisting:
    def __init__(self, report: ProjectUpdate | None = None) -> None:
        self.report = report

    def execute(self, user_id: UUID, start_of_week: date, team_project: str) -> ProjectUpdate | None:
        return self.report


def client_for(
    submit: FakeSubmit,
    *,
    role: str = "TEAM_LEAD",
    user_id: UUID | None = None,
    get_update: FakeGet | None = None,
    list_updates: FakeList | None = None,
    update: FakeUpdate | None = None,
    check_existing: FakeCheckExisting | None = None,
    approve: FakeApprove | None = None,
    auth_service: FakeAuthService | None = None,
) -> TestClient:
    current_user_id = user_id or uuid4()

    def get_current_user() -> dict[str, str]:
        return {"sub": str(current_user_id), "username": "current-user", "role": role}

    app = FastAPI()
    app.include_router(
        create_project_update_router(
            submit,
            get_update or FakeGet(),
            list_updates or FakeList(),
            update or FakeUpdate(),
            check_existing or FakeCheckExisting(),
            approve or FakeApprove(),
            get_current_user,
            auth_service or FakeAuthService(),
        )
    )
    return TestClient(app)


def project_update(user_id: UUID) -> ProjectUpdate:
    now = datetime.now(UTC)
    return ProjectUpdate(
        id=uuid4(),
        idempotency_key=str(uuid4()),
        request_hash="a" * 64,
        user_id=user_id,
        start_of_week=date(2026, 7, 20),
        end_of_week=date(2026, 7, 26),
        team_project="Rights Management API",
        achievements="Released version 1.0",
        initiatives="Started US development",
        next_weeks_plan="Complete API testing",
        created_at=now,
        updated_at=now,
    )


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
        "id", "user_id", "owner_username", "start_of_week", "end_of_week",
        "team_project", "achievements", "initiatives", "next_weeks_plan",
        "created_at", "updated_at", "approval_status", "approved_by_id", "approved_at",
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


def test_employee_list_is_scoped_to_current_user() -> None:
    user_id = uuid4()
    list_updates = FakeList([project_update(user_id)])

    response = client_for(FakeSubmit(), user_id=user_id, list_updates=list_updates).get(
        "/api/v1/project-updates"
    )

    assert response.status_code == 200
    assert list_updates.user_ids == {user_id}
    assert response.json()[0]["user_id"] == str(user_id)


def test_manager_list_sees_all_reports() -> None:
    manager_id = uuid4()
    employee_id = uuid4()
    list_updates = FakeList()

    response = client_for(
        FakeSubmit(),
        role="TEAM_MANAGER",
        user_id=manager_id,
        list_updates=list_updates,
        auth_service=FakeAuthService([employee_id]),
    ).get("/api/v1/project-updates")

    assert response.status_code == 200
    # TEAM_MANAGER sees all reports (user_ids=None means unscoped)
    assert list_updates.user_ids is None


def test_admin_list_is_unscoped() -> None:
    list_updates = FakeList()

    response = client_for(FakeSubmit(), role="APP_ADMIN", list_updates=list_updates).get(
        "/api/v1/project-updates"
    )

    assert response.status_code == 200
    assert list_updates.user_ids is None


def test_owner_can_edit_report() -> None:
    user_id = uuid4()
    existing = project_update(user_id)
    fake_update = FakeUpdate(existing)

    response = client_for(FakeSubmit(), user_id=user_id, get_update=FakeGet(existing), update=fake_update).put(
        f"/api/v1/project-updates/{existing.id}", json=form_data()
    )

    assert response.status_code == 200
    assert fake_update.editor_id == user_id
    assert fake_update.command is not None
    assert fake_update.command.achievements == "Released version 1.0"


def test_non_owner_cannot_edit_report() -> None:
    owner_id = uuid4()
    existing = project_update(owner_id)

    response = client_for(
        FakeSubmit(),
        role="TEAM_LEAD",
        get_update=FakeGet(existing),
        update=FakeUpdate(),
    ).put(f"/api/v1/project-updates/{existing.id}", json=form_data())

    assert response.status_code == 403
    assert response.json()["detail"] == "Only the report owner can edit this update."


def test_check_returns_null_when_no_existing_report() -> None:
    response = client_for(FakeSubmit()).get(
        "/api/v1/project-updates/check",
        params={"start_of_week": "2026-07-20", "team_project": "Rights Management API"},
    )

    assert response.status_code == 200
    assert response.json() == {"exists": False, "report": None}


def test_check_returns_report_when_exists() -> None:
    user_id = uuid4()
    existing = project_update(user_id)
    checker = FakeCheckExisting(existing)

    response = client_for(FakeSubmit(), user_id=user_id, check_existing=checker).get(
        "/api/v1/project-updates/check",
        params={"start_of_week": "2026-07-20", "team_project": "Rights Management API"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["exists"] is True
    assert body["report"]["id"] == str(existing.id)
    # owner_username comes from auth_service.get_usernames_by_ids, not from current_user
    assert body["report"]["owner_username"] is not None