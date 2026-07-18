from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.teacher import Teacher


class ITeacherRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Teacher]: ...

    @abstractmethod
    def get_by_id(self, teacher_id: int) -> Optional[Teacher]: ...

    @abstractmethod
    def create(self, teacher: Teacher) -> Teacher: ...

    @abstractmethod
    def update(self, teacher: Teacher) -> Teacher: ...

    @abstractmethod
    def delete(self, teacher_id: int) -> bool: ...
