from __future__ import annotations

from datetime import date
from uuid import UUID

import pytest

from app.application.contracts import IdempotencyConflictError, SubmitCommand
from app.application.services import SubmitProjectUpdate, SystemClock
from app.domain import ProjectUpdate


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.update: ProjectUpdate | None = None

    def claim(self, update: ProjectUpdate) -> tuple[ProjectUpdate, bool]:
        if self.update is not None:
            return self.update, False
        self.update = update
        return update, True

    def get(self, update_id: UUID) -> ProjectUpdate | None:
        return self.update if self.update and self.update.id == update_id else None


def command() -> SubmitCommand:
    return SubmitCommand("key-1", date(2026, 7, 20), date(2026, 7, 26), "Platform", "Done", "Next", "Plan")


def test_matching_replay_returns_the_stored_record() -> None:
    unit_of_work = FakeUnitOfWork()
    service = SubmitProjectUpdate(unit_of_work, SystemClock())

    first = service.execute(command())
    replay = service.execute(command())

    assert replay.replayed is True
    assert replay.update.id == first.update.id
    assert replay.update.created_at == first.update.created_at


def test_changed_replay_raises_conflict() -> None:
    unit_of_work = FakeUnitOfWork()
    service = SubmitProjectUpdate(unit_of_work, SystemClock())
    service.execute(command())
    changed = SubmitCommand(
        "key-1", date(2026, 7, 20), date(2026, 7, 26), "Platform", "Changed", "Next", "Plan"
    )

    with pytest.raises(IdempotencyConflictError, match="different content"):
        service.execute(changed)