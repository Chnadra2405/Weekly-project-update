from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.teacher_repository_impl import TeacherRepositoryImpl
from app.application.services.teacher_service import TeacherService
from app.application.dtos.teacher_dto import TeacherCreateDTO, TeacherUpdateDTO, TeacherResponseDTO

router = APIRouter(prefix="/teachers", tags=["Teachers"])


def get_service(db: Session = Depends(get_db)) -> TeacherService:
    return TeacherService(TeacherRepositoryImpl(db))


@router.get("/", response_model=List[TeacherResponseDTO])
def list_teachers(service: TeacherService = Depends(get_service)):
    return service.get_all()


@router.get("/{teacher_id}", response_model=TeacherResponseDTO)
def get_teacher(teacher_id: int, service: TeacherService = Depends(get_service)):
    try:
        return service.get_by_id(teacher_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/", response_model=TeacherResponseDTO, status_code=status.HTTP_201_CREATED)
def create_teacher(dto: TeacherCreateDTO, service: TeacherService = Depends(get_service)):
    return service.create(dto)


@router.put("/{teacher_id}", response_model=TeacherResponseDTO)
def update_teacher(teacher_id: int, dto: TeacherUpdateDTO, service: TeacherService = Depends(get_service)):
    try:
        return service.update(teacher_id, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, service: TeacherService = Depends(get_service)):
    if not service.delete(teacher_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
