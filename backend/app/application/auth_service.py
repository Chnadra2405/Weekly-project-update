from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.database import UserModel, TeamAssignmentModel


class AuthService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        self.session_factory = session_factory
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def create_access_token(self, user_id: UUID, username: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "iat": now,
            "exp": expires,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.InvalidTokenError:
            return None

    def register_user(
        self, username: str, email: str, password: str, role: str = "EMPLOYEE", team: str | None = None
    ) -> UserModel | None:
        with self.session_factory() as session:
            existing = session.scalar(
                select(UserModel).where((UserModel.username == username) | (UserModel.email == email))
            )
            if existing:
                return None

            now = datetime.now(timezone.utc)
            user = UserModel(
                id=uuid4(),
                username=username,
                email=email,
                hashed_password=self.hash_password(password),
                role=role,
                team=team,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def authenticate_user(self, username: str, password: str) -> UserModel | None:
        with self.session_factory() as session:
            user = session.scalar(select(UserModel).where(UserModel.username == username))
            if not user or not self.verify_password(password, user.hashed_password):
                return None
            return user

    def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        with self.session_factory() as session:
            user = session.get(UserModel, user_id)
            return user

    def get_usernames_by_ids(self, user_ids: set[UUID]) -> dict[UUID, str]:
        if not user_ids:
            return {}
        with self.session_factory() as session:
            users = session.scalars(select(UserModel).where(UserModel.id.in_(user_ids))).all()
            return {user.id: user.username for user in users}

    def get_team_members(self, manager_id: UUID) -> list[UUID]:
        """Get all employee IDs assigned to a manager."""
        with self.session_factory() as session:
            assignments = session.scalars(
                select(TeamAssignmentModel.employee_id).where(TeamAssignmentModel.manager_id == manager_id)
            ).all()
            return list(assignments)

    def assign_employee_to_manager(self, manager_id: UUID, employee_id: UUID) -> bool:
        """Assign an employee to a manager."""
        with self.session_factory() as session:
            existing = session.scalar(
                select(TeamAssignmentModel).where(
                    (TeamAssignmentModel.manager_id == manager_id)
                    & (TeamAssignmentModel.employee_id == employee_id)
                )
            )
            if existing:
                return False

            now = datetime.now(timezone.utc)
            assignment = TeamAssignmentModel(
                id=uuid4(),
                manager_id=manager_id,
                employee_id=employee_id,
                created_at=now,
            )
            session.add(assignment)
            session.commit()
            return True
