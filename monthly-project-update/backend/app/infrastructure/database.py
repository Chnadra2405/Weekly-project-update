from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, Unicode, UniqueConstraint, Uuid, create_engine, select
from sqlalchemy.dialects import mssql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from app.domain import Attachment, AttachmentKind, DeliveryStatus, EmailAddress, ProjectUpdate, ReportingMonth


class Base(DeclarativeBase):
    pass


class ProjectUpdateModel(Base):
    __tablename__ = "project_updates"
    __table_args__ = (
        CheckConstraint("delivery_status IN ('PENDING','SENT','FAILED')", name="ck_project_updates_status"),
        CheckConstraint("DAY(reporting_month) = 1", name="ck_project_updates_month_first_day"),
        CheckConstraint(
            "(delivery_status = 'PENDING' AND smtp_message_id IS NULL AND failure_code IS NULL AND failure_detail IS NULL AND sent_at IS NULL) OR "
            "(delivery_status = 'SENT' AND smtp_message_id IS NOT NULL AND failure_code IS NULL AND failure_detail IS NULL AND sent_at IS NOT NULL) OR "
            "(delivery_status = 'FAILED' AND smtp_message_id IS NULL AND failure_code IS NOT NULL AND failure_detail IS NOT NULL AND sent_at IS NULL)",
            name="ck_project_updates_terminal_fields",
        ),
        Index("uq_project_updates_idempotency_key", "idempotency_key", unique=True),
        Index("ix_project_updates_employee_month", "employee_email", "reporting_month"),
        Index("ix_project_updates_created_at", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    employee_name: Mapped[str] = mapped_column(Unicode(200), nullable=False)
    employee_email: Mapped[str] = mapped_column(String(320), nullable=False)
    reporting_month: Mapped[date] = mapped_column(mssql.DATE, nullable=False)
    team_project: Mapped[str] = mapped_column(Unicode(300), nullable=False)
    achievements: Mapped[str] = mapped_column(mssql.NVARCHAR(None), nullable=False)
    initiatives: Mapped[str] = mapped_column(mssql.NVARCHAR(None), nullable=False)
    next_weeks_plan: Mapped[str] = mapped_column(mssql.NVARCHAR(None), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="PENDING")
    smtp_message_id: Mapped[str | None] = mapped_column(String(255))
    failure_code: Mapped[str | None] = mapped_column(String(64))
    failure_detail: Mapped[str | None] = mapped_column(String(1000))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attachments: Mapped[list[AttachmentModel]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class AttachmentModel(Base):
    __tablename__ = "attachments"
    __table_args__ = (
        CheckConstraint("kind IN ('REFERENCE_EMAIL','IMAGE')", name="ck_attachments_kind"),
        CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="ck_attachments_size"),
        UniqueConstraint("project_update_id", "kind", name="uq_attachments_update_kind"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    project_update_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("project_updates.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    original_filename: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    stored_relative_path: Mapped[str] = mapped_column(Unicode(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def to_domain(model: ProjectUpdateModel) -> ProjectUpdate:
    return ProjectUpdate(
        id=model.id,
        idempotency_key=model.idempotency_key,
        request_hash=model.request_hash,
        employee_name=model.employee_name,
        employee_email=EmailAddress(model.employee_email),
        reporting_month=ReportingMonth(model.reporting_month),
        team_project=model.team_project,
        achievements=model.achievements,
        initiatives=model.initiatives,
        next_weeks_plan=model.next_weeks_plan,
        delivery_status=DeliveryStatus(model.delivery_status),
        smtp_message_id=model.smtp_message_id,
        failure_code=model.failure_code,
        failure_detail=model.failure_detail,
        sent_at=model.sent_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
        attachments=[
            Attachment(
                item.id,
                AttachmentKind(item.kind),
                item.original_filename,
                item.stored_relative_path,
                item.media_type,
                item.size_bytes,
                item.sha256,
            )
            for item in model.attachments
        ],
    )


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def claim(self, update: ProjectUpdate) -> tuple[ProjectUpdate, bool]:
        if update.created_at is None or update.updated_at is None:
            raise ValueError("Persistence timestamps are required.")
        with self.session_factory() as session:
            model = ProjectUpdateModel(
                id=update.id,
                idempotency_key=update.idempotency_key,
                request_hash=update.request_hash,
                employee_name=update.employee_name,
                employee_email=str(update.employee_email),
                reporting_month=update.reporting_month.value,
                team_project=update.team_project,
                achievements=update.achievements,
                initiatives=update.initiatives,
                next_weeks_plan=update.next_weeks_plan,
                delivery_status=update.delivery_status.value,
                created_at=update.created_at,
                updated_at=update.updated_at,
                attachments=[
                    AttachmentModel(
                        id=item.id,
                        kind=item.kind.value,
                        original_filename=item.original_filename,
                        stored_relative_path=item.stored_relative_path,
                        media_type=item.media_type,
                        size_bytes=item.size_bytes,
                        sha256=item.sha256,
                        created_at=update.created_at,
                    )
                    for item in update.attachments
                ],
            )
            session.add(model)
            try:
                session.commit()
                session.refresh(model)
                return to_domain(model), True
            except IntegrityError:
                session.rollback()
                existing = session.scalar(select(ProjectUpdateModel).where(ProjectUpdateModel.idempotency_key == update.idempotency_key))
                if existing is None:
                    raise
                return to_domain(existing), False

    def get(self, update_id: UUID) -> ProjectUpdate | None:
        with self.session_factory() as session:
            model = session.get(ProjectUpdateModel, update_id)
            return to_domain(model) if model else None

    def save_status(self, update: ProjectUpdate) -> None:
        with self.session_factory() as session:
            model = session.get(ProjectUpdateModel, update.id)
            if model is None:
                raise LookupError("Project update no longer exists.")
            model.delivery_status = update.delivery_status.value
            model.smtp_message_id = update.smtp_message_id
            model.failure_code = update.failure_code
            model.failure_detail = update.failure_detail
            model.sent_at = update.sent_at
            model.updated_at = update.updated_at or update.created_at or datetime.now(UTC)
            if not update.attachments:
                model.attachments.clear()
            session.commit()


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(create_engine(database_url, pool_pre_ping=True), expire_on_commit=False)