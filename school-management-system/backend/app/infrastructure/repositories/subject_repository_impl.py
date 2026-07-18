from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.subject import Subject
from app.domain.repositories.subject_repository import ISubjectRepository
from app.infrastructure.database.models import SubjectModel


class SubjectRepositoryImpl(ISubjectRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: SubjectModel) -> Subject:
        return Subject(
            id=model.id,
            name=model.name,
            code=model.code,
            class_id=model.class_id,
            teacher_id=model.teacher_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_all(self) -> List[Subject]:
        rows = self._db.query(SubjectModel).all()
        return [self._to_entity(r) for r in rows]

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        row = self._db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
        return self._to_entity(row) if row else None

    def get_by_class(self, class_id: int) -> List[Subject]:
        rows = self._db.query(SubjectModel).filter(SubjectModel.class_id == class_id).all()
        return [self._to_entity(r) for r in rows]

    def create(self, subject: Subject) -> Subject:
        model = SubjectModel(
            name=subject.name,
            code=subject.code,
            class_id=subject.class_id,
            teacher_id=subject.teacher_id,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, subject: Subject) -> Subject:
        model = self._db.query(SubjectModel).filter(SubjectModel.id == subject.id).first()
        if not model:
            raise ValueError(f"Subject {subject.id} not found")
        model.name = subject.name
        model.code = subject.code
        model.class_id = subject.class_id
        model.teacher_id = subject.teacher_id
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, subject_id: int) -> bool:
        model = self._db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
