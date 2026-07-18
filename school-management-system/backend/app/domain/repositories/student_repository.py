from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.student import Student


class IStudentRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Student]: ...

    @abstractmethod
    def get_by_id(self, student_id: int) -> Optional[Student]: ...

    @abstractmethod
    def create(self, student: Student) -> Student: ...

    @abstractmethod
    def update(self, student: Student) -> Student: ...

    @abstractmethod
    def delete(self, student_id: int) -> bool: ...
