from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.enrollment import Enrollment


class IEnrollmentRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Enrollment]: ...

    @abstractmethod
    def get_by_student(self, student_id: int) -> List[Enrollment]: ...

    @abstractmethod
    def get_by_class(self, class_id: int) -> List[Enrollment]: ...

    @abstractmethod
    def create(self, enrollment: Enrollment) -> Enrollment: ...

    @abstractmethod
    def delete(self, enrollment_id: int) -> bool: ...
