from typing import List
from app.domain.entities.enrollment import Enrollment
from app.domain.repositories.enrollment_repository import IEnrollmentRepository
from app.application.dtos.enrollment_dto import EnrollmentCreateDTO, EnrollmentResponseDTO


class EnrollmentService:
    def __init__(self, repository: IEnrollmentRepository):
        self._repo = repository

    def get_all(self) -> List[EnrollmentResponseDTO]:
        return [self._to_dto(e) for e in self._repo.get_all()]

    def get_by_student(self, student_id: int) -> List[EnrollmentResponseDTO]:
        return [self._to_dto(e) for e in self._repo.get_by_student(student_id)]

    def get_by_class(self, class_id: int) -> List[EnrollmentResponseDTO]:
        return [self._to_dto(e) for e in self._repo.get_by_class(class_id)]

    def create(self, dto: EnrollmentCreateDTO) -> EnrollmentResponseDTO:
        entity = Enrollment(student_id=dto.student_id, class_id=dto.class_id)
        return self._to_dto(self._repo.create(entity))

    def delete(self, enrollment_id: int) -> bool:
        return self._repo.delete(enrollment_id)

    @staticmethod
    def _to_dto(entity: Enrollment) -> EnrollmentResponseDTO:
        return EnrollmentResponseDTO(
            id=entity.id,
            student_id=entity.student_id,
            class_id=entity.class_id,
            enrolled_at=entity.enrolled_at,
        )
