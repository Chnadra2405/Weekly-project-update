from typing import List
from app.domain.entities.student import Student
from app.domain.repositories.student_repository import IStudentRepository
from app.application.dtos.student_dto import StudentCreateDTO, StudentUpdateDTO, StudentResponseDTO


class StudentService:
    def __init__(self, repository: IStudentRepository):
        self._repo = repository

    def get_all(self) -> List[StudentResponseDTO]:
        students = self._repo.get_all()
        return [self._to_dto(s) for s in students]

    def get_by_id(self, student_id: int) -> StudentResponseDTO:
        student = self._repo.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        return self._to_dto(student)

    def create(self, dto: StudentCreateDTO) -> StudentResponseDTO:
        entity = Student(
            first_name=dto.first_name,
            last_name=dto.last_name,
            date_of_birth=dto.date_of_birth,
            gender=dto.gender,
            email=dto.email,
            phone=dto.phone,
            address=dto.address,
        )
        created = self._repo.create(entity)
        return self._to_dto(created)

    def update(self, student_id: int, dto: StudentUpdateDTO) -> StudentResponseDTO:
        entity = Student(
            id=student_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            date_of_birth=dto.date_of_birth,
            gender=dto.gender,
            email=dto.email,
            phone=dto.phone,
            address=dto.address,
        )
        updated = self._repo.update(entity)
        return self._to_dto(updated)

    def delete(self, student_id: int) -> bool:
        return self._repo.delete(student_id)

    @staticmethod
    def _to_dto(entity: Student) -> StudentResponseDTO:
        return StudentResponseDTO(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            date_of_birth=entity.date_of_birth,
            gender=entity.gender,
            email=entity.email,
            phone=entity.phone,
            address=entity.address,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
