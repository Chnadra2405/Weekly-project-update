from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "mssql+pyodbc://sa:ProjectUpdate1!@localhost:1433/ProjectUpdateDB"
        "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    storage_root: Path = Path("./var/storage")
    max_file_bytes: int = 10 * 1024 * 1024
    max_total_bytes: int = 20 * 1024 * 1024
    max_image_pixels: int = 40_000_000
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_address: str = "project-updates@example.com"
    smtp_from_name: str = "Monthly Project Update"
    smtp_to: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["delivery@example.com"])
    smtp_cc: Annotated[list[str], NoDecode] = Field(default_factory=list)
    smtp_bcc: Annotated[list[str], NoDecode] = Field(default_factory=list)
    smtp_use_starttls: bool = False
    smtp_timeout_seconds: float = 10.0
    message_id_domain: str = "example.com"
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["http://localhost:5173"])

    @field_validator("smtp_to", "smtp_cc", "smtp_bcc", "cors_allowed_origins", mode="before")
    @classmethod
    def parse_comma_list(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("smtp_to")
    @classmethod
    def require_recipient(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("SMTP_TO must contain at least one address")
        return value