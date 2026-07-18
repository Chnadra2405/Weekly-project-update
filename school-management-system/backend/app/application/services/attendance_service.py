from datetime import date
from typing import List
from app.domain.entities.attendance import Attendance
from app.domain.repositories.attendance_repository import IAttendanceRepository
from app.application.dtos.attendance_dto import AttendanceUpsertDTO, AttendanceResponseDTO


class AttendanceService:
    def __init__(self, repository: IAttendanceRepository):
        self._repo = repository

    def get_by_class_and_date(self, class_id: int, attendance_date: date) -> List[AttendanceResponseDTO]:
        return [self._to_dto(a) for a in self._repo.get_by_class_and_date(class_id, attendance_date)]

    def get_by_student(self, student_id: int) -> List[AttendanceResponseDTO]:
        return [self._to_dto(a) for a in self._repo.get_by_student(student_id)]

    def upsert(self, dto: AttendanceUpsertDTO) -> AttendanceResponseDTO:
        entity = Attendance(
            student_id=dto.student_id,
            class_id=dto.class_id,
            date=dto.date,
            status=dto.status,
        )
        return self._to_dto(self._repo.upsert(entity))

    def delete(self, attendance_id: int) -> bool:
        return self._repo.delete(attendance_id)

    @staticmethod
    def _to_dto(entity: Attendance) -> AttendanceResponseDTO:
        return AttendanceResponseDTO(
            id=entity.id,
            student_id=entity.student_id,
            class_id=entity.class_id,
            date=entity.date,
            status=entity.status,
            created_at=entity.created_at,
        )
