from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from uuid import UUID

from app.domain.exceptions import DomainValidationError


@dataclass(slots=True)
class ProjectUpdate:
    id: UUID
    idempotency_key: str
    request_hash: str
    start_of_week: date
    end_of_week: date
    team_project: str
    achievements: str
    initiatives: str
    next_weeks_plan: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "idempotency_key",
            "team_project",
            "achievements",
            "initiatives",
            "next_weeks_plan",
        ):
            value = getattr(self, field_name).strip()
            if not value:
                raise DomainValidationError(f"{field_name.replace('_', ' ').title()} is required.")
            setattr(self, field_name, value)
        if len(self.idempotency_key) > 128 or len(self.request_hash) != 64:
            raise DomainValidationError("Request identity is invalid.")
        if self.end_of_week != self.start_of_week + timedelta(days=6):
            raise DomainValidationError("Week must span exactly seven inclusive days.")