from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import UUID

from app.domain import Attachment, ProjectUpdate


@dataclass(frozen=True, slots=True)
class IncomingFile:
    filename: str
    media_type: str
    stream: BinaryIO


@dataclass(frozen=True, slots=True)
class StagedUpload:
    attachment: Attachment
    staging_directory: Path


@dataclass(frozen=True, slots=True)
class SubmitCommand:
    idempotency_key: str
    employee_name: str
    employee_email: str
    reporting_month: str
    team_project: str
    achievements: str
    initiatives: str
    next_weeks_plan: str
    reference_email: IncomingFile | None = None
    image: IncomingFile | None = None


@dataclass(frozen=True, slots=True)
class SubmitResult:
    update: ProjectUpdate
    replayed: bool


class IdempotencyConflictError(RuntimeError):
    pass


class UploadValidationError(ValueError):
    pass


class Storage(Protocol):
    def stage(self, submission_id: UUID, files: list[IncomingFile]) -> list[StagedUpload]: ...
    def commit(self, submission_id: UUID, staged: list[StagedUpload]) -> None: ...
    def discard(self, submission_id: UUID) -> None: ...
    def absolute_path(self, attachment: Attachment) -> Path: ...
    def is_ready(self) -> bool: ...


class UnitOfWork(Protocol):
    def claim(self, update: ProjectUpdate) -> tuple[ProjectUpdate, bool]: ...
    def get(self, update_id: UUID) -> ProjectUpdate | None: ...
    def save_status(self, update: ProjectUpdate) -> None: ...


class MailSender(Protocol):
    def send(self, update: ProjectUpdate) -> str: ...


class Clock(Protocol):
    def now(self) -> datetime: ...