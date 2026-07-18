from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.school_class import SchoolClass
from app.domain.repositories.class_repository import IClassRepository
from app.infrastructure.database.models import ClassModel


class ClassRepositoryImpl(IClassRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: ClassModel) -> SchoolClass:
        return SchoolClass(
            id=model.id,
            name=model.name,
            grade_level=model.grade_level,
            section=model.section,
            teacher_id=model.teacher_id,
            academic_year=model.academic_year,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_all(self) -> List[SchoolClass]:
        rows = self._db.query(ClassModel).all()
        return [self._to_entity(r) for r in rows]

    def get_by_id(self, class_id: int) -> Optional[SchoolClass]:
        row = self._db.query(ClassModel).filter(ClassModel.id == class_id).first()
        return self._to_entity(row) if row else None

    def create(self, school_class: SchoolClass) -> SchoolClass:
        model = ClassModel(
            name=school_class.name,
            grade_level=school_class.grade_level,
            section=school_class.section,
            teacher_id=school_class.teacher_id,
            academic_year=school_class.academic_year,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, school_class: SchoolClass) -> SchoolClass:
        model = self._db.query(ClassModel).filter(ClassModel.id == school_class.id).first()
        if not model:
            raise ValueError(f"Class {school_class.id} not found")
        model.name = school_class.name
        model.grade_level = school_class.grade_level
        model.section = school_class.section
        model.teacher_id = school_class.teacher_id
        model.academic_year = school_class.academic_year
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, class_id: int) -> bool:
        model = self._db.query(ClassModel).filter(ClassModel.id == class_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
