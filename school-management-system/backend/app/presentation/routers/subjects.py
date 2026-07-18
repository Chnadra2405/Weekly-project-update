from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.subject_repository_impl import SubjectRepositoryImpl
from app.application.services.subject_service import SubjectService
from app.application.dtos.subject_dto import SubjectCreateDTO, SubjectUpdateDTO, SubjectResponseDTO

router = APIRouter(prefix="/subjects", tags=["Subjects"])


def get_service(db: Session = Depends(get_db)) -> SubjectService:
    return SubjectService(SubjectRepositoryImpl(db))


@router.get("/", response_model=List[SubjectResponseDTO])
def list_subjects(service: SubjectService = Depends(get_service)):
    return service.get_all()


@router.get("/class/{class_id}", response_model=List[SubjectResponseDTO])
def get_subjects_by_class(class_id: int, service: SubjectService = Depends(get_service)):
    return service.get_by_class(class_id)


@router.get("/{subject_id}", response_model=SubjectResponseDTO)
def get_subject(subject_id: int, service: SubjectService = Depends(get_service)):
    try:
        return service.get_by_id(subject_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/", response_model=SubjectResponseDTO, status_code=status.HTTP_201_CREATED)
def create_subject(dto: SubjectCreateDTO, service: SubjectService = Depends(get_service)):
    return service.create(dto)


@router.put("/{subject_id}", response_model=SubjectResponseDTO)
def update_subject(subject_id: int, dto: SubjectUpdateDTO, service: SubjectService = Depends(get_service)):
    try:
        return service.update(subject_id, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, service: SubjectService = Depends(get_service)):
    if not service.delete(subject_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
