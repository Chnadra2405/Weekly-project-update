from typing import List
from app.domain.entities.teacher import Teacher
from app.domain.repositories.teacher_repository import ITeacherRepository
from app.application.dtos.teacher_dto import TeacherCreateDTO, TeacherUpdateDTO, TeacherResponseDTO


class TeacherService:
    def __init__(self, repository: ITeacherRepository):
        self._repo = repository

    def get_all(self) -> List[TeacherResponseDTO]:
        return [self._to_dto(t) for t in self._repo.get_all()]

    def get_by_id(self, teacher_id: int) -> TeacherResponseDTO:
        teacher = self._repo.get_by_id(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher {teacher_id} not found")
        return self._to_dto(teacher)

    def create(self, dto: TeacherCreateDTO) -> TeacherResponseDTO:
        entity = Teacher(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            phone=dto.phone,
            specialization=dto.specialization,
        )
        return self._to_dto(self._repo.create(entity))

    def update(self, teacher_id: int, dto: TeacherUpdateDTO) -> TeacherResponseDTO:
        entity = Teacher(
            id=teacher_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            phone=dto.phone,
            specialization=dto.specialization,
        )
        return self._to_dto(self._repo.update(entity))

    def delete(self, teacher_id: int) -> bool:
        return self._repo.delete(teacher_id)

    @staticmethod
    def _to_dto(entity: Teacher) -> TeacherResponseDTO:
        return TeacherResponseDTO(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            specialization=entity.specialization,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
