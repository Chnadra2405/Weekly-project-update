from typing import List
from app.domain.entities.subject import Subject
from app.domain.repositories.subject_repository import ISubjectRepository
from app.application.dtos.subject_dto import SubjectCreateDTO, SubjectUpdateDTO, SubjectResponseDTO


class SubjectService:
    def __init__(self, repository: ISubjectRepository):
        self._repo = repository

    def get_all(self) -> List[SubjectResponseDTO]:
        return [self._to_dto(s) for s in self._repo.get_all()]

    def get_by_id(self, subject_id: int) -> SubjectResponseDTO:
        subject = self._repo.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Subject {subject_id} not found")
        return self._to_dto(subject)

    def get_by_class(self, class_id: int) -> List[SubjectResponseDTO]:
        return [self._to_dto(s) for s in self._repo.get_by_class(class_id)]

    def create(self, dto: SubjectCreateDTO) -> SubjectResponseDTO:
        entity = Subject(
            name=dto.name,
            code=dto.code,
            class_id=dto.class_id,
            teacher_id=dto.teacher_id,
        )
        return self._to_dto(self._repo.create(entity))

    def update(self, subject_id: int, dto: SubjectUpdateDTO) -> SubjectResponseDTO:
        entity = Subject(
            id=subject_id,
            name=dto.name,
            code=dto.code,
            class_id=dto.class_id,
            teacher_id=dto.teacher_id,
        )
        return self._to_dto(self._repo.update(entity))

    def delete(self, subject_id: int) -> bool:
        return self._repo.delete(subject_id)

    @staticmethod
    def _to_dto(entity: Subject) -> SubjectResponseDTO:
        return SubjectResponseDTO(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            class_id=entity.class_id,
            teacher_id=entity.teacher_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
