from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.enrollment_repository_impl import EnrollmentRepositoryImpl
from app.application.services.enrollment_service import EnrollmentService
from app.application.dtos.enrollment_dto import EnrollmentCreateDTO, EnrollmentResponseDTO

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


def get_service(db: Session = Depends(get_db)) -> EnrollmentService:
    return EnrollmentService(EnrollmentRepositoryImpl(db))


@router.get("/", response_model=List[EnrollmentResponseDTO])
def list_enrollments(service: EnrollmentService = Depends(get_service)):
    return service.get_all()


@router.get("/student/{student_id}", response_model=List[EnrollmentResponseDTO])
def get_by_student(student_id: int, service: EnrollmentService = Depends(get_service)):
    return service.get_by_student(student_id)


@router.get("/class/{class_id}", response_model=List[EnrollmentResponseDTO])
def get_by_class(class_id: int, service: EnrollmentService = Depends(get_service)):
    return service.get_by_class(class_id)


@router.post("/", response_model=EnrollmentResponseDTO, status_code=status.HTTP_201_CREATED)
def create_enrollment(dto: EnrollmentCreateDTO, service: EnrollmentService = Depends(get_service)):
    return service.create(dto)


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, service: EnrollmentService = Depends(get_service)):
    if not service.delete(enrollment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
