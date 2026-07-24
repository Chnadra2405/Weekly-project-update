from __future__ import annotations

import html
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.domain import ProjectUpdate
from app.infrastructure.settings import Settings
from app.infrastructure.storage import LocalFileStorage


def build_message(update: ProjectUpdate, settings: Settings, storage: LocalFileStorage) -> EmailMessage:
    message = EmailMessage()
    message_id = f"<{update.id}@{settings.message_id_domain}>"
    message["Message-ID"] = message_id
    message["Subject"] = f"Monthly Project Update - {update.employee_name} - {update.reporting_month} - {update.team_project}"
    message["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_address))
    message["To"] = ", ".join(settings.smtp_to)
    if settings.smtp_cc:
        message["Cc"] = ", ".join(settings.smtp_cc)
    fields = [
        ("Employee", f"{update.employee_name} <{update.employee_email}>"),
        ("Reporting month", str(update.reporting_month)),
        ("Team / project", update.team_project),
        ("Achievements", update.achievements),
        ("Initiatives", update.initiatives),
        ("Next week's plan", update.next_weeks_plan),
    ]
    message.set_content("\n\n".join(f"{label}\n{value}" for label, value in fields))
    rows = "".join(
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(value).replace(chr(10), '<br>')}</td></tr>"
        for label, value in fields
    )
    message.add_alternative(
        "<!doctype html><html><body><h1>Monthly Project Update</h1>"
        f"<table><tbody>{rows}</tbody></table></body></html>",
        subtype="html",
    )
    for attachment in update.attachments:
        maintype, subtype = attachment.media_type.split("/", maxsplit=1)
        message.add_attachment(
            storage.absolute_path(attachment).read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=attachment.original_filename,
        )
    return message


class SmtpMailSender:
    def __init__(self, settings: Settings, storage: LocalFileStorage) -> None:
        self.settings = settings
        self.storage = storage

    def send(self, update: ProjectUpdate) -> str:
        message = build_message(update, self.settings, self.storage)
        recipients = self.settings.smtp_to + self.settings.smtp_cc + self.settings.smtp_bcc
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=self.settings.smtp_timeout_seconds) as smtp:
            if self.settings.smtp_use_starttls:
                smtp.starttls()
            if self.settings.smtp_username:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password or "")
            smtp.send_message(message, to_addrs=recipients)
        return str(message["Message-ID"])