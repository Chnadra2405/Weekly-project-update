from datetime import date
from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.attendance import Attendance
from app.domain.repositories.attendance_repository import IAttendanceRepository
from app.infrastructure.database.models import AttendanceModel


class AttendanceRepositoryImpl(IAttendanceRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: AttendanceModel) -> Attendance:
        return Attendance(
            id=model.id,
            student_id=model.student_id,
            class_id=model.class_id,
            date=model.date,
            status=model.status,
            created_at=model.created_at,
        )

    def get_by_class_and_date(self, class_id: int, attendance_date: date) -> List[Attendance]:
        rows = (
            self._db.query(AttendanceModel)
            .filter(AttendanceModel.class_id == class_id, AttendanceModel.date == attendance_date)
            .all()
        )
        return [self._to_entity(r) for r in rows]

    def get_by_student(self, student_id: int) -> List[Attendance]:
        rows = self._db.query(AttendanceModel).filter(AttendanceModel.student_id == student_id).all()
        return [self._to_entity(r) for r in rows]

    def upsert(self, attendance: Attendance) -> Attendance:
        existing = (
            self._db.query(AttendanceModel)
            .filter(
                AttendanceModel.student_id == attendance.student_id,
                AttendanceModel.class_id == attendance.class_id,
                AttendanceModel.date == attendance.date,
            )
            .first()
        )
        if existing:
            existing.status = attendance.status
            self._db.commit()
            self._db.refresh(existing)
            return self._to_entity(existing)

        model = AttendanceModel(
            student_id=attendance.student_id,
            class_id=attendance.class_id,
            date=attendance.date,
            status=attendance.status,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, attendance_id: int) -> bool:
        model = self._db.query(AttendanceModel).filter(AttendanceModel.id == attendance_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
