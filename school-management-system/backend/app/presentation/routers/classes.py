from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.class_repository_impl import ClassRepositoryImpl
from app.application.services.class_service import ClassService
from app.application.dtos.class_dto import ClassCreateDTO, ClassUpdateDTO, ClassResponseDTO

router = APIRouter(prefix="/classes", tags=["Classes"])


def get_service(db: Session = Depends(get_db)) -> ClassService:
    return ClassService(ClassRepositoryImpl(db))


@router.get("/", response_model=List[ClassResponseDTO])
def list_classes(service: ClassService = Depends(get_service)):
    return service.get_all()


@router.get("/{class_id}", response_model=ClassResponseDTO)
def get_class(class_id: int, service: ClassService = Depends(get_service)):
    try:
        return service.get_by_id(class_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/", response_model=ClassResponseDTO, status_code=status.HTTP_201_CREATED)
def create_class(dto: ClassCreateDTO, service: ClassService = Depends(get_service)):
    return service.create(dto)


@router.put("/{class_id}", response_model=ClassResponseDTO)
def update_class(class_id: int, dto: ClassUpdateDTO, service: ClassService = Depends(get_service)):
    try:
        return service.update(class_id, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(class_id: int, service: ClassService = Depends(get_service)):
    if not service.delete(class_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
