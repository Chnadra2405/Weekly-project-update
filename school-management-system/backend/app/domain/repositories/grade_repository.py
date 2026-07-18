from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.grade import Grade


class IGradeRepository(ABC):
    @abstractmethod
    def get_by_student(self, student_id: int) -> List[Grade]: ...

    @abstractmethod
    def get_by_subject(self, subject_id: int) -> List[Grade]: ...

    @abstractmethod
    def create(self, grade: Grade) -> Grade: ...

    @abstractmethod
    def update(self, grade: Grade) -> Grade: ...

    @abstractmethod
    def delete(self, grade_id: int) -> bool: ...
