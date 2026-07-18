from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.enrollment import Enrollment
from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.infrastructure.database.models import EnrollmentModel


class EnrollmentRepositoryImpl(IEnrollmentRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: EnrollmentModel) -> Enrollment:
        return Enrollment(
            id=model.id,
            student_id=model.student_id,
            class_id=model.class_id,
            enrolled_at=model.enrolled_at,
        )

    def get_all(self) -> List[Enrollment]:
        rows = self._db.query(EnrollmentModel).all()
        return [self._to_entity(r) for r in rows]

    def get_by_student(self, student_id: int) -> List[Enrollment]:
        rows = self._db.query(EnrollmentModel).filter(EnrollmentModel.student_id == student_id).all()
        return [self._to_entity(r) for r in rows]

    def get_by_class(self, class_id: int) -> List[Enrollment]:
        rows = self._db.query(EnrollmentModel).filter(EnrollmentModel.class_id == class_id).all()
        return [self._to_entity(r) for r in rows]

    def create(self, enrollment: Enrollment) -> Enrollment:
        model = EnrollmentModel(
            student_id=enrollment.student_id,
            class_id=enrollment.class_id,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, enrollment_id: int) -> bool:
        model = self._db.query(EnrollmentModel).filter(EnrollmentModel.id == enrollment_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
