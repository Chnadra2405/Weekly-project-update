from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from email.utils import parseaddr

from app.domain.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        parsed = parseaddr(normalized)[1]
        if parsed != normalized or "@" not in normalized or normalized.startswith("@"):
            raise DomainValidationError("A valid email address is required.")
        local, domain = normalized.rsplit("@", 1)
        if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise DomainValidationError("A valid email address is required.")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ReportingMonth:
    value: date

    @classmethod
    def from_html_month(cls, raw_value: str) -> ReportingMonth:
        try:
            year_text, month_text = raw_value.strip().split("-", maxsplit=1)
            value = date(int(year_text), int(month_text), 1)
        except (TypeError, ValueError) as error:
            raise DomainValidationError("Reporting month must use YYYY-MM format.") from error
        if len(year_text) != 4 or len(month_text) != 2:
            raise DomainValidationError("Reporting month must use YYYY-MM format.")
        return cls(value)

    def __post_init__(self) -> None:
        if self.value.day != 1:
            object.__setattr__(self, "value", self.value.replace(day=1))

    def __str__(self) -> str:
        return self.value.strftime("%Y-%m")