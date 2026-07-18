from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.grade_repository_impl import GradeRepositoryImpl
from app.application.services.grade_service import GradeService
from app.application.dtos.grade_dto import GradeCreateDTO, GradeUpdateDTO, GradeResponseDTO

router = APIRouter(prefix="/grades", tags=["Grades"])


def get_service(db: Session = Depends(get_db)) -> GradeService:
    return GradeService(GradeRepositoryImpl(db))


@router.get("/student/{student_id}", response_model=List[GradeResponseDTO])
def get_grades_by_student(student_id: int, service: GradeService = Depends(get_service)):
    return service.get_by_student(student_id)


@router.get("/subject/{subject_id}", response_model=List[GradeResponseDTO])
def get_grades_by_subject(subject_id: int, service: GradeService = Depends(get_service)):
    return service.get_by_subject(subject_id)


@router.post("/", response_model=GradeResponseDTO, status_code=status.HTTP_201_CREATED)
def create_grade(dto: GradeCreateDTO, service: GradeService = Depends(get_service)):
    return service.create(dto)


@router.put("/{grade_id}", response_model=GradeResponseDTO)
def update_grade(grade_id: int, dto: GradeUpdateDTO, service: GradeService = Depends(get_service)):
    try:
        return service.update(grade_id, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(grade_id: int, service: GradeService = Depends(get_service)):
    if not service.delete(grade_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found")
