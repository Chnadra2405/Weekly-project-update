from typing import List
from app.domain.entities.grade import Grade
from app.domain.repositories.grade_repository import IGradeRepository
from app.application.dtos.grade_dto import GradeCreateDTO, GradeUpdateDTO, GradeResponseDTO


class GradeService:
    def __init__(self, repository: IGradeRepository):
        self._repo = repository

    def get_by_student(self, student_id: int) -> List[GradeResponseDTO]:
        return [self._to_dto(g) for g in self._repo.get_by_student(student_id)]

    def get_by_subject(self, subject_id: int) -> List[GradeResponseDTO]:
        return [self._to_dto(g) for g in self._repo.get_by_subject(subject_id)]

    def create(self, dto: GradeCreateDTO) -> GradeResponseDTO:
        entity = Grade(
            student_id=dto.student_id,
            subject_id=dto.subject_id,
            marks_obtained=dto.marks_obtained,
            max_marks=dto.max_marks,
            exam_type=dto.exam_type,
            exam_date=dto.exam_date,
        )
        return self._to_dto(self._repo.create(entity))

    def update(self, grade_id: int, dto: GradeUpdateDTO) -> GradeResponseDTO:
        entity = Grade(
            id=grade_id,
            student_id=0,
            subject_id=0,
            marks_obtained=dto.marks_obtained,
            max_marks=dto.max_marks,
            exam_type=dto.exam_type,
            exam_date=dto.exam_date,
        )
        return self._to_dto(self._repo.update(entity))

    def delete(self, grade_id: int) -> bool:
        return self._repo.delete(grade_id)

    @staticmethod
    def _to_dto(entity: Grade) -> GradeResponseDTO:
        return GradeResponseDTO(
            id=entity.id,
            student_id=entity.student_id,
            subject_id=entity.subject_id,
            marks_obtained=entity.marks_obtained,
            max_marks=entity.max_marks,
            exam_type=entity.exam_type,
            exam_date=entity.exam_date,
            created_at=entity.created_at,
        )
