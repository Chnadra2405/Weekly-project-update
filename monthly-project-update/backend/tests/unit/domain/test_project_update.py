from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain import Attachment, AttachmentKind, DeliveryStatus, EmailAddress, ProjectUpdate, ReportingMonth
from app.domain.exceptions import DomainValidationError, InvalidStatusTransitionError


def make_update(**overrides: object) -> ProjectUpdate:
    values = {
        "id": uuid4(),
        "idempotency_key": "request-1",
        "request_hash": "a" * 64,
        "employee_name": "  Ada Lovelace  ",
        "employee_email": EmailAddress(" ADA@EXAMPLE.COM "),
        "reporting_month": ReportingMonth.from_html_month("2026-07"),
        "team_project": " Platform ",
        "achievements": "Shipped reporting",
        "initiatives": "Improve observability",
        "next_weeks_plan": "Measure adoption",
    }
    values.update(overrides)
    return ProjectUpdate(**values)  # type: ignore[arg-type]


def test_normalizes_email_month_and_required_text() -> None:
    update = make_update()

    assert str(update.employee_email) == "ada@example.com"
    assert str(update.reporting_month) == "2026-07"
    assert update.employee_name == "Ada Lovelace"


def test_rejects_duplicate_attachment_kind() -> None:
    attachment = Attachment(uuid4(), AttachmentKind.IMAGE, "chart.png", "a/chart.png", "image/png", 4, "b" * 64)

    with pytest.raises(DomainValidationError, match="one attachment"):
        make_update(attachments=[attachment, attachment])


def test_terminal_status_cannot_transition_again() -> None:
    update = make_update()
    update.mark_sent("<id@example.com>", datetime.now(UTC))

    assert update.delivery_status is DeliveryStatus.SENT
    with pytest.raises(InvalidStatusTransitionError):
        update.mark_failed("SMTP_FAILED", "not used")


def test_failure_detail_is_bounded_and_single_line() -> None:
    update = make_update()
    update.mark_failed("SMTP_FAILED", "line one\n" + ("x" * 1100))

    assert update.delivery_status is DeliveryStatus.FAILED
    assert update.failure_detail is not None
    assert "\n" not in update.failure_detail
    assert len(update.failure_detail) == 1000