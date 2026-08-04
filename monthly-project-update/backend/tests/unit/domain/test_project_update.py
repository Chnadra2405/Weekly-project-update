from datetime import date, timedelta
from uuid import uuid4

import pytest

from app.domain import ProjectUpdate
from app.domain.exceptions import DomainValidationError


def make_update(**overrides: object) -> ProjectUpdate:
    values = {
        "id": uuid4(),
        "idempotency_key": "request-1",
        "request_hash": "a" * 64,
        "start_of_week": date(2026, 7, 20),
        "end_of_week": date(2026, 7, 26),
        "team_project": " Platform ",
        "achievements": "Shipped reporting",
        "initiatives": "Improve observability",
        "next_weeks_plan": "Measure adoption",
    }
    values.update(overrides)
    return ProjectUpdate(**values)  # type: ignore[arg-type]


def test_normalizes_required_text() -> None:
    update = make_update()

    assert update.team_project == "Platform"


@pytest.mark.parametrize("duration_days", [5, 7])
def test_requires_exactly_seven_inclusive_days(duration_days: int) -> None:
    start_of_week = date(2026, 7, 20)

    with pytest.raises(DomainValidationError, match="exactly seven inclusive days"):
        make_update(end_of_week=start_of_week + timedelta(days=duration_days))