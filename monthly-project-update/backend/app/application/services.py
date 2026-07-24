from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.contracts import (
    Clock,
    IdempotencyConflictError,
    MailSender,
    StagedUpload,
    Storage,
    SubmitCommand,
    SubmitResult,
    UnitOfWork,
)
from app.domain import EmailAddress, ProjectUpdate, ReportingMonth


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class SubmitProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork, storage: Storage, mail_sender: MailSender, clock: Clock) -> None:
        self.unit_of_work = unit_of_work
        self.storage = storage
        self.mail_sender = mail_sender
        self.clock = clock

    def execute(self, command: SubmitCommand) -> SubmitResult:
        submission_id = uuid4()
        files = [item for item in (command.reference_email, command.image) if item is not None]
        staged = self.storage.stage(submission_id, files)
        try:
            update = ProjectUpdate(
                id=submission_id,
                idempotency_key=command.idempotency_key,
                request_hash=self._request_hash(command, staged),
                employee_name=command.employee_name,
                employee_email=EmailAddress(command.employee_email),
                reporting_month=ReportingMonth.from_html_month(command.reporting_month),
                team_project=command.team_project,
                achievements=command.achievements,
                initiatives=command.initiatives,
                next_weeks_plan=command.next_weeks_plan,
                attachments=[item.attachment for item in staged],
                created_at=self.clock.now(),
                updated_at=self.clock.now(),
            )
            claimed, is_new = self.unit_of_work.claim(update)
            if not is_new:
                self.storage.discard(submission_id)
                if claimed.request_hash != update.request_hash:
                    raise IdempotencyConflictError("The idempotency key was already used with different content.")
                return SubmitResult(claimed, replayed=True)
            try:
                self.storage.commit(submission_id, staged)
            except Exception:
                self.storage.discard(submission_id)
                claimed.attachments.clear()
                claimed.mark_failed("STORAGE_COMMIT_FAILED", "Managed storage commit failed.")
                self.unit_of_work.save_status(claimed)
                return SubmitResult(claimed, replayed=False)
            try:
                message_id = self.mail_sender.send(claimed)
                claimed.mark_sent(message_id, self.clock.now())
            except Exception:
                claimed.mark_failed("SMTP_DELIVERY_FAILED", "Email delivery failed.")
            self.unit_of_work.save_status(claimed)
            return SubmitResult(claimed, replayed=False)
        except Exception:
            self.storage.discard(submission_id)
            raise

    @staticmethod
    def _request_hash(command: SubmitCommand, staged: list[StagedUpload]) -> str:
        attachments = []
        for item in staged:
            attachment = item.attachment
            attachments.append(
                {
                    "kind": attachment.kind.value,
                    "filename": attachment.original_filename,
                    "media_type": attachment.media_type,
                    "size": attachment.size_bytes,
                    "sha256": attachment.sha256,
                }
            )
        payload = {
            "version": 1,
            "employee_name": command.employee_name.strip(),
            "employee_email": str(EmailAddress(command.employee_email)),
            "reporting_month": str(ReportingMonth.from_html_month(command.reporting_month)),
            "team_project": command.team_project.strip(),
            "achievements": command.achievements.strip(),
            "initiatives": command.initiatives.strip(),
            "next_weeks_plan": command.next_weeks_plan.strip(),
            "attachments": sorted(attachments, key=lambda item: item["kind"]),
        }
        canonical = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class GetProjectUpdate:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, update_id: UUID) -> ProjectUpdate | None:
        return self.unit_of_work.get(update_id)