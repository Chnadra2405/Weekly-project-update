from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from app.application.contracts import (
    Clock,
    IdempotencyConflictError,
    SubmitCommand,
    SubmitResult,
    UnitOfWork,
    UpdateCommand,
)
from app.domain import ProjectUpdate


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class SubmitProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork, clock: Clock) -> None:
        self.unit_of_work = unit_of_work
        self.clock = clock

    def execute(self, command: SubmitCommand, user_id: UUID | None = None) -> SubmitResult:
        timestamp = self.clock.now()
        update = ProjectUpdate(
            id=uuid4(),
            idempotency_key=command.idempotency_key,
            request_hash=self._request_hash(command),
            start_of_week=command.start_of_week,
            end_of_week=command.end_of_week,
            team_project=command.team_project,
            achievements=command.achievements,
            initiatives=command.initiatives,
            next_weeks_plan=command.next_weeks_plan,
            created_at=timestamp,
            updated_at=timestamp,
            user_id=user_id or command.user_id,
        )
        claimed, is_new = self.unit_of_work.claim(update)
        if not is_new and claimed.request_hash != update.request_hash:
            raise IdempotencyConflictError("The idempotency key was already used with different content.")
        return SubmitResult(claimed, replayed=not is_new)

    @staticmethod
    def _request_hash(command: SubmitCommand) -> str:
        payload = {
            "version": 2,
            "start_of_week": command.start_of_week.isoformat(),
            "end_of_week": command.end_of_week.isoformat(),
            "team_project": command.team_project.strip(),
            "achievements": command.achievements.strip(),
            "initiatives": command.initiatives.strip(),
            "next_weeks_plan": command.next_weeks_plan.strip(),
        }
        canonical = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class GetProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, update_id: UUID) -> ProjectUpdate | None:
        return self.unit_of_work.get(update_id)


class CheckExistingReport:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(
        self, user_id: UUID, start_of_week: date, team_project: str
    ) -> ProjectUpdate | None:
        return self.unit_of_work.find_by_week_and_team(user_id, start_of_week, team_project)


class ApproveProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, update_id: UUID, approver_id: UUID) -> ProjectUpdate | None:
        existing = self.unit_of_work.get(update_id)
        if existing is None:
            return None
        # Idempotent: already approved is fine
        if existing.approval_status == "APPROVED":
            return existing
        return self.unit_of_work.approve(update_id, approver_id)


class ListProjectUpdates:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, user_ids: set[UUID] | None = None) -> list[ProjectUpdate]:
        return self.unit_of_work.list(user_ids)


class UpdateProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork, clock: Clock) -> None:
        self.unit_of_work = unit_of_work
        self.clock = clock

    def execute(self, update_id: UUID, editor_id: UUID, editor_role: str, command: UpdateCommand) -> ProjectUpdate | None:
        existing = self.unit_of_work.get(update_id)
        if existing is None:
            return None

        # Approved reports cannot be edited (APP_ADMIN is exempt)
        if existing.approval_status == "APPROVED" and editor_role != "APP_ADMIN":
            return None

        # DU_HEAD is read-only
        if editor_role == "DU_HEAD":
            return None

        # TEAM_LEAD may only edit their own reports (checked at API layer too)
        if editor_role == "TEAM_LEAD" and existing.user_id != editor_id:
            return None

        updated = ProjectUpdate(
            id=existing.id,
            idempotency_key=existing.idempotency_key,
            request_hash=SubmitProjectUpdate._request_hash(
                SubmitCommand(
                    idempotency_key=existing.idempotency_key,
                    start_of_week=command.start_of_week,
                    end_of_week=command.end_of_week,
                    team_project=command.team_project,
                    achievements=command.achievements,
                    initiatives=command.initiatives,
                    next_weeks_plan=command.next_weeks_plan,
                )
            ),
            user_id=existing.user_id,
            start_of_week=command.start_of_week,
            end_of_week=command.end_of_week,
            team_project=command.team_project,
            achievements=command.achievements,
            initiatives=command.initiatives,
            next_weeks_plan=command.next_weeks_plan,
            created_at=existing.created_at,
            updated_at=self.clock.now(),
        )
        return self.unit_of_work.save(updated)