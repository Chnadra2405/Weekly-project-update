from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.school_class import SchoolClass


class IClassRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[SchoolClass]: ...

    @abstractmethod
    def get_by_id(self, class_id: int) -> Optional[SchoolClass]: ...

    @abstractmethod
    def create(self, school_class: SchoolClass) -> SchoolClass: ...

    @abstractmethod
    def update(self, school_class: SchoolClass) -> SchoolClass: ...

    @abstractmethod
    def delete(self, class_id: int) -> bool: ...
