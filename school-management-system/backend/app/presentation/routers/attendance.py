from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.attendance_repository_impl import AttendanceRepositoryImpl
from app.application.services.attendance_service import AttendanceService
from app.application.dtos.attendance_dto import AttendanceUpsertDTO, AttendanceResponseDTO

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def get_service(db: Session = Depends(get_db)) -> AttendanceService:
    return AttendanceService(AttendanceRepositoryImpl(db))


@router.get("/class/{class_id}", response_model=List[AttendanceResponseDTO])
def get_by_class_and_date(
    class_id: int,
    date: date,
    service: AttendanceService = Depends(get_service),
):
    return service.get_by_class_and_date(class_id, date)


@router.get("/student/{student_id}", response_model=List[AttendanceResponseDTO])
def get_by_student(student_id: int, service: AttendanceService = Depends(get_service)):
    return service.get_by_student(student_id)


@router.post("/", response_model=AttendanceResponseDTO, status_code=status.HTTP_201_CREATED)
def upsert_attendance(dto: AttendanceUpsertDTO, service: AttendanceService = Depends(get_service)):
    return service.upsert(dto)


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(attendance_id: int, service: AttendanceService = Depends(get_service)):
    if not service.delete(attendance_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
