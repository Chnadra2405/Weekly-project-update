from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.contracts import (
    Clock,
    IdempotencyConflictError,
    SubmitCommand,
    SubmitResult,
    UnitOfWork,
)
from app.domain import ProjectUpdate


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class SubmitProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork, clock: Clock) -> None:
        self.unit_of_work = unit_of_work
        self.clock = clock

    def execute(self, command: SubmitCommand) -> SubmitResult:
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