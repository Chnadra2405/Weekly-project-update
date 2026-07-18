from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.subject import Subject


class ISubjectRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Subject]: ...

    @abstractmethod
    def get_by_id(self, subject_id: int) -> Optional[Subject]: ...

    @abstractmethod
    def get_by_class(self, class_id: int) -> List[Subject]: ...

    @abstractmethod
    def create(self, subject: Subject) -> Subject: ...

    @abstractmethod
    def update(self, subject: Subject) -> Subject: ...

    @abstractmethod
    def delete(self, subject_id: int) -> bool: ...
