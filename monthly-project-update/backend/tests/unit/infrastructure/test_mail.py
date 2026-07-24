from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.domain import EmailAddress, ProjectUpdate, ReportingMonth
from app.infrastructure.mail import build_message
from app.infrastructure.settings import Settings
from app.infrastructure.storage import LocalFileStorage


def test_html_message_escapes_user_content(tmp_path: Path) -> None:
    update = ProjectUpdate(
        id=uuid4(), idempotency_key="key", request_hash="a" * 64, employee_name="Ada <script>",
        employee_email=EmailAddress("ada@example.com"), reporting_month=ReportingMonth.from_html_month("2026-07"),
        team_project="Core & API", achievements="<b>done</b>", initiatives="Next", next_weeks_plan="Plan",
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    storage = LocalFileStorage(tmp_path, 1024, 2048, 1000)

    message = build_message(update, Settings(), storage)
    html_body = message.get_body(preferencelist=("html",)).get_content()

    assert "<script>" not in html_body
    assert "&lt;script&gt;" in html_body
    assert "Core &amp; API" in html_body