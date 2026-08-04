from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, Unicode, Uuid, create_engine, select
from sqlalchemy.dialects import mssql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.domain import ProjectUpdate


class Base(DeclarativeBase):
    pass


class ProjectUpdateModel(Base):
    __tablename__ = "project_updates"
    __table_args__ = (
        CheckConstraint(
            "end_of_week = DATEADD(day, 6, start_of_week)",
            name="ck_project_updates_seven_day_week",
        ),
        Index("uq_project_updates_idempotency_key", "idempotency_key", unique=True),
        Index("ix_project_updates_start_of_week", "start_of_week"),
        Index("ix_project_updates_created_at", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    start_of_week: Mapped[date] = mapped_column(mssql.DATE, nullable=False)
    end_of_week: Mapped[date] = mapped_column(mssql.DATE, nullable=False)
    team_project: Mapped[str] = mapped_column(Unicode(300), nullable=False)
    achievements: Mapped[str] = mapped_column(mssql.NVARCHAR(None), nullable=False)
    initiatives: Mapped[str] = mapped_column(mssql.NVARCHAR(None), nullable=False)
    next_weeks_plan: Mapped[str] = mapped_column(mssql.NVARCHAR(None), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def to_domain(model: ProjectUpdateModel) -> ProjectUpdate:
    return ProjectUpdate(
        id=model.id,
        idempotency_key=model.idempotency_key,
        request_hash=model.request_hash,
        start_of_week=model.start_of_week,
        end_of_week=model.end_of_week,
        team_project=model.team_project,
        achievements=model.achievements,
        initiatives=model.initiatives,
        next_weeks_plan=model.next_weeks_plan,
        created_at=model.created_at,
        updated_at=model.updated_at,
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
                start_of_week=update.start_of_week,
                end_of_week=update.end_of_week,
                team_project=update.team_project,
                achievements=update.achievements,
                initiatives=update.initiatives,
                next_weeks_plan=update.next_weeks_plan,
                created_at=update.created_at,
                updated_at=update.updated_at,
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


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(create_engine(database_url, pool_pre_ping=True), expire_on_commit=False)