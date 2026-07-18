from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.teacher import Teacher
from app.domain.repositories.teacher_repository import ITeacherRepository
from app.infrastructure.database.models import TeacherModel


class TeacherRepositoryImpl(ITeacherRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: TeacherModel) -> Teacher:
        return Teacher(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            specialization=model.specialization,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_all(self) -> List[Teacher]:
        rows = self._db.query(TeacherModel).all()
        return [self._to_entity(r) for r in rows]

    def get_by_id(self, teacher_id: int) -> Optional[Teacher]:
        row = self._db.query(TeacherModel).filter(TeacherModel.id == teacher_id).first()
        return self._to_entity(row) if row else None

    def create(self, teacher: Teacher) -> Teacher:
        model = TeacherModel(
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            email=teacher.email,
            phone=teacher.phone,
            specialization=teacher.specialization,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, teacher: Teacher) -> Teacher:
        model = self._db.query(TeacherModel).filter(TeacherModel.id == teacher.id).first()
        if not model:
            raise ValueError(f"Teacher {teacher.id} not found")
        model.first_name = teacher.first_name
        model.last_name = teacher.last_name
        model.email = teacher.email
        model.phone = teacher.phone
        model.specialization = teacher.specialization
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, teacher_id: int) -> bool:
        model = self._db.query(TeacherModel).filter(TeacherModel.id == teacher_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
