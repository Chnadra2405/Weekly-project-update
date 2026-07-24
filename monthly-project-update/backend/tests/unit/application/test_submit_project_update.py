from __future__ import annotations

from pathlib import Path
from typing import cast
from uuid import UUID

from app.application.contracts import IncomingFile, StagedUpload, SubmitCommand
from app.application.services import SubmitProjectUpdate, SystemClock
from app.domain import ProjectUpdate


class FakeStorage:
    def stage(self, submission_id: UUID, files: list[IncomingFile]) -> list[StagedUpload]:
        return []

    def commit(self, submission_id: UUID, staged: list[StagedUpload]) -> None:
        return None

    def discard(self, submission_id: UUID) -> None:
        return None

    def absolute_path(self, attachment: object) -> Path:
        raise AssertionError("No attachment expected")

    def is_ready(self) -> bool:
        return True


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

    def save_status(self, update: ProjectUpdate) -> None:
        self.update = update


class FakeMailSender:
    def __init__(self, error: Exception | None = None) -> None:
        self.calls = 0
        self.error = error

    def send(self, update: ProjectUpdate) -> str:
        self.calls += 1
        if self.error:
            raise self.error
        return f"<{update.id}@example.com>"


def command() -> SubmitCommand:
    return SubmitCommand("key-1", "Ada", "ada@example.com", "2026-07", "Platform", "Done", "Next", "Plan")


def test_matching_replay_does_not_send_twice() -> None:
    unit_of_work = FakeUnitOfWork()
    sender = FakeMailSender()
    service = SubmitProjectUpdate(unit_of_work, FakeStorage(), sender, SystemClock())

    first = service.execute(command())
    replay = service.execute(command())

    assert first.update.delivery_status.value == "SENT"
    assert replay.replayed is True
    assert sender.calls == 1


def test_mail_failure_is_persisted_without_secret_detail() -> None:
    unit_of_work = FakeUnitOfWork()
    sender = FakeMailSender(RuntimeError("password=secret"))
    service = SubmitProjectUpdate(unit_of_work, FakeStorage(), sender, SystemClock())

    result = service.execute(command())

    assert result.update.delivery_status.value == "FAILED"
    assert result.update.failure_code == "SMTP_DELIVERY_FAILED"
    assert "secret" not in cast(str, result.update.failure_detail)