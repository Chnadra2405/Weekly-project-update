from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.student import Student
from app.domain.repositories.student_repository import IStudentRepository
from app.infrastructure.database.models import StudentModel


class StudentRepositoryImpl(IStudentRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: StudentModel) -> Student:
        return Student(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            date_of_birth=model.date_of_birth,
            gender=model.gender,
            email=model.email,
            phone=model.phone,
            address=model.address,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_all(self) -> List[Student]:
        rows = self._db.query(StudentModel).all()
        return [self._to_entity(r) for r in rows]

    def get_by_id(self, student_id: int) -> Optional[Student]:
        row = self._db.query(StudentModel).filter(StudentModel.id == student_id).first()
        return self._to_entity(row) if row else None

    def create(self, student: Student) -> Student:
        model = StudentModel(
            first_name=student.first_name,
            last_name=student.last_name,
            date_of_birth=student.date_of_birth,
            gender=student.gender,
            email=student.email,
            phone=student.phone,
            address=student.address,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, student: Student) -> Student:
        model = self._db.query(StudentModel).filter(StudentModel.id == student.id).first()
        if not model:
            raise ValueError(f"Student {student.id} not found")
        model.first_name = student.first_name
        model.last_name = student.last_name
        model.date_of_birth = student.date_of_birth
        model.gender = student.gender
        model.email = student.email
        model.phone = student.phone
        model.address = student.address
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, student_id: int) -> bool:
        model = self._db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
