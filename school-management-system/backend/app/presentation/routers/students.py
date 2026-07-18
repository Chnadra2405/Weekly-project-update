from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.student_repository_impl import StudentRepositoryImpl
from app.application.services.student_service import StudentService
from app.application.dtos.student_dto import StudentCreateDTO, StudentUpdateDTO, StudentResponseDTO

router = APIRouter(prefix="/students", tags=["Students"])


def get_service(db: Session = Depends(get_db)) -> StudentService:
    return StudentService(StudentRepositoryImpl(db))


@router.get("/", response_model=List[StudentResponseDTO])
def list_students(service: StudentService = Depends(get_service)):
    return service.get_all()


@router.get("/{student_id}", response_model=StudentResponseDTO)
def get_student(student_id: int, service: StudentService = Depends(get_service)):
    try:
        return service.get_by_id(student_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/", response_model=StudentResponseDTO, status_code=status.HTTP_201_CREATED)
def create_student(dto: StudentCreateDTO, service: StudentService = Depends(get_service)):
    return service.create(dto)


@router.put("/{student_id}", response_model=StudentResponseDTO)
def update_student(student_id: int, dto: StudentUpdateDTO, service: StudentService = Depends(get_service)):
    try:
        return service.update(student_id, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, service: StudentService = Depends(get_service)):
    if not service.delete(student_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
