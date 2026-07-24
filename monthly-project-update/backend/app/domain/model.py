from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import DomainValidationError, InvalidStatusTransitionError
from app.domain.values import EmailAddress, ReportingMonth


class AttachmentKind(StrEnum):
    REFERENCE_EMAIL = "REFERENCE_EMAIL"
    IMAGE = "IMAGE"


class DeliveryStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class Attachment:
    id: UUID
    kind: AttachmentKind
    original_filename: str
    stored_relative_path: str
    media_type: str
    size_bytes: int
    sha256: str

    def __post_init__(self) -> None:
        if not self.original_filename.strip() or self.size_bytes <= 0:
            raise DomainValidationError("Attachment metadata is invalid.")
        if len(self.sha256) != 64:
            raise DomainValidationError("Attachment checksum is invalid.")


@dataclass(slots=True)
class ProjectUpdate:
    id: UUID
    idempotency_key: str
    request_hash: str
    employee_name: str
    employee_email: EmailAddress
    reporting_month: ReportingMonth
    team_project: str
    achievements: str
    initiatives: str
    next_weeks_plan: str
    attachments: list[Attachment] = field(default_factory=list)
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    smtp_message_id: str | None = None
    failure_code: str | None = None
    failure_detail: str | None = None
    sent_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "idempotency_key",
            "employee_name",
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
        kinds = [attachment.kind for attachment in self.attachments]
        if len(kinds) != len(set(kinds)):
            raise DomainValidationError("Only one attachment of each kind is allowed.")

    def mark_sent(self, message_id: str, sent_at: datetime) -> None:
        self._require_pending()
        self.delivery_status = DeliveryStatus.SENT
        self.smtp_message_id = message_id
        self.sent_at = sent_at
        self.failure_code = None
        self.failure_detail = None

    def mark_failed(self, code: str, detail: str) -> None:
        self._require_pending()
        safe_detail = " ".join(detail.split())[:1000]
        self.delivery_status = DeliveryStatus.FAILED
        self.failure_code = code.strip()[:64] or "DELIVERY_FAILED"
        self.failure_detail = safe_detail or "Delivery failed."
        self.sent_at = None
        self.smtp_message_id = None

    def _require_pending(self) -> None:
        if self.delivery_status is not DeliveryStatus.PENDING:
            raise InvalidStatusTransitionError("Terminal delivery status cannot be changed.")