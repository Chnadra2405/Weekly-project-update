from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, Date, ForeignKey, Index, String, Text, Unicode, Uuid, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.domain import ProjectUpdate


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('EMPLOYEE', 'MANAGER', 'ADMIN')",
            name="ck_users_role",
        ),
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="EMPLOYEE")
    team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TeamAssignmentModel(Base):
    __tablename__ = "team_assignments"
    __table_args__ = (
        Index("ix_team_assignments_manager_id", "manager_id"),
        Index("ix_team_assignments_employee_id", "employee_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    manager_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProjectUpdateModel(Base):
    __tablename__ = "project_updates"
    __table_args__ = (
        Index("uq_project_updates_idempotency_key", "idempotency_key", unique=True),
        Index("ix_project_updates_start_of_week", "start_of_week"),
        Index("ix_project_updates_created_at", "created_at"),
        Index("ix_project_updates_user_start_week", "user_id", "start_of_week"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    start_of_week: Mapped[date] = mapped_column(Date, nullable=False)
    end_of_week: Mapped[date] = mapped_column(Date, nullable=False)
    team_project: Mapped[str] = mapped_column(String(300), nullable=False)
    achievements: Mapped[str] = mapped_column(Text, nullable=False)
    initiatives: Mapped[str] = mapped_column(Text, nullable=False)
    next_weeks_plan: Mapped[str] = mapped_column(Text, nullable=False)
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
        user_id=model.user_id,
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
                user_id=update.user_id,
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

    def list(self, user_ids: set[UUID] | None = None) -> list[ProjectUpdate]:
        with self.session_factory() as session:
            statement = select(ProjectUpdateModel).order_by(
                ProjectUpdateModel.start_of_week.desc(),
                ProjectUpdateModel.created_at.desc(),
            )
            if user_ids is not None:
                if not user_ids:
                    return []
                statement = statement.where(ProjectUpdateModel.user_id.in_(user_ids))
            return [to_domain(model) for model in session.scalars(statement).all()]

    def save(self, update: ProjectUpdate) -> ProjectUpdate:
        with self.session_factory() as session:
            model = session.get(ProjectUpdateModel, update.id)
            if model is None:
                raise ValueError("Project update does not exist.")
            model.request_hash = update.request_hash
            model.start_of_week = update.start_of_week
            model.end_of_week = update.end_of_week
            model.team_project = update.team_project
            model.achievements = update.achievements
            model.initiatives = update.initiatives
            model.next_weeks_plan = update.next_weeks_plan
            model.updated_at = update.updated_at
            session.commit()
            session.refresh(model)
            return to_domain(model)

    def find_by_week_and_team(
        self,
        user_id: UUID,
        start_of_week: date,
        team_project: str,
    ) -> ProjectUpdate | None:
        with self.session_factory() as session:
            model = session.scalar(
                select(ProjectUpdateModel).where(
                    ProjectUpdateModel.start_of_week == start_of_week,
                    ProjectUpdateModel.team_project == team_project,
                )
            )
            return to_domain(model) if model else None


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)