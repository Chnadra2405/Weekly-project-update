from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.grade import Grade
from app.domain.repositories.grade_repository import IGradeRepository
from app.infrastructure.database.models import GradeModel


class GradeRepositoryImpl(IGradeRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: GradeModel) -> Grade:
        return Grade(
            id=model.id,
            student_id=model.student_id,
            subject_id=model.subject_id,
            marks_obtained=float(model.marks_obtained),
            max_marks=float(model.max_marks),
            exam_type=model.exam_type,
            exam_date=model.exam_date,
            created_at=model.created_at,
        )

    def get_by_student(self, student_id: int) -> List[Grade]:
        rows = self._db.query(GradeModel).filter(GradeModel.student_id == student_id).all()
        return [self._to_entity(r) for r in rows]

    def get_by_subject(self, subject_id: int) -> List[Grade]:
        rows = self._db.query(GradeModel).filter(GradeModel.subject_id == subject_id).all()
        return [self._to_entity(r) for r in rows]

    def create(self, grade: Grade) -> Grade:
        model = GradeModel(
            student_id=grade.student_id,
            subject_id=grade.subject_id,
            marks_obtained=grade.marks_obtained,
            max_marks=grade.max_marks,
            exam_type=grade.exam_type,
            exam_date=grade.exam_date,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, grade: Grade) -> Grade:
        model = self._db.query(GradeModel).filter(GradeModel.id == grade.id).first()
        if not model:
            raise ValueError(f"Grade {grade.id} not found")
        model.marks_obtained = grade.marks_obtained
        model.max_marks = grade.max_marks
        model.exam_type = grade.exam_type
        model.exam_date = grade.exam_date
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, grade_id: int) -> bool:
        model = self._db.query(GradeModel).filter(GradeModel.id == grade_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
