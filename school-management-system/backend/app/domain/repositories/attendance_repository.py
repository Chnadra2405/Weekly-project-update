from abc import ABC, abstractmethod
from datetime import date
from typing import List
from app.domain.entities.attendance import Attendance


class IAttendanceRepository(ABC):
    @abstractmethod
    def get_by_class_and_date(self, class_id: int, attendance_date: date) -> List[Attendance]: ...

    @abstractmethod
    def get_by_student(self, student_id: int) -> List[Attendance]: ...

    @abstractmethod
    def upsert(self, attendance: Attendance) -> Attendance: ...

    @abstractmethod
    def delete(self, attendance_id: int) -> bool: ...
