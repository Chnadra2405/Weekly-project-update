from typing import List
from app.domain.entities.school_class import SchoolClass
from app.domain.repositories.class_repository import IClassRepository
from app.application.dtos.class_dto import ClassCreateDTO, ClassUpdateDTO, ClassResponseDTO


class ClassService:
    def __init__(self, repository: IClassRepository):
        self._repo = repository

    def get_all(self) -> List[ClassResponseDTO]:
        return [self._to_dto(c) for c in self._repo.get_all()]

    def get_by_id(self, class_id: int) -> ClassResponseDTO:
        school_class = self._repo.get_by_id(class_id)
        if not school_class:
            raise ValueError(f"Class {class_id} not found")
        return self._to_dto(school_class)

    def create(self, dto: ClassCreateDTO) -> ClassResponseDTO:
        entity = SchoolClass(
            name=dto.name,
            grade_level=dto.grade_level,
            section=dto.section,
            teacher_id=dto.teacher_id,
            academic_year=dto.academic_year,
        )
        return self._to_dto(self._repo.create(entity))

    def update(self, class_id: int, dto: ClassUpdateDTO) -> ClassResponseDTO:
        entity = SchoolClass(
            id=class_id,
            name=dto.name,
            grade_level=dto.grade_level,
            section=dto.section,
            teacher_id=dto.teacher_id,
            academic_year=dto.academic_year,
        )
        return self._to_dto(self._repo.update(entity))

    def delete(self, class_id: int) -> bool:
        return self._repo.delete(class_id)

    @staticmethod
    def _to_dto(entity: SchoolClass) -> ClassResponseDTO:
        return ClassResponseDTO(
            id=entity.id,
            name=entity.name,
            grade_level=entity.grade_level,
            section=entity.section,
            teacher_id=entity.teacher_id,
            academic_year=entity.academic_year,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
