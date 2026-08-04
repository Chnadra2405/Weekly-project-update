from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.domain import ProjectUpdate


@dataclass(frozen=True, slots=True)
class SubmitCommand:
    idempotency_key: str
    start_of_week: date
    end_of_week: date
    team_project: str
    achievements: str
    initiatives: str
    next_weeks_plan: str


@dataclass(frozen=True, slots=True)
class SubmitResult:
    update: ProjectUpdate
    replayed: bool


class IdempotencyConflictError(RuntimeError):
    pass


class UnitOfWork(Protocol):
    def claim(self, update: ProjectUpdate) -> tuple[ProjectUpdate, bool]: ...
    def get(self, update_id: UUID) -> ProjectUpdate | None: ...


class Clock(Protocol):
    def now(self) -> datetime: ...