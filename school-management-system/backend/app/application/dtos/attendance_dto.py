from datetime import date, datetime
from pydantic import BaseModel


class AttendanceUpsertDTO(BaseModel):
    student_id: int
    class_id: int
    date: date
    status: str = "Present"


class AttendanceResponseDTO(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: date
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
