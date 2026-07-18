from datetime import date, datetime
from pydantic import BaseModel


class GradeCreateDTO(BaseModel):
    student_id: int
    subject_id: int
    marks_obtained: float
    max_marks: float = 100.0
    exam_type: str = "Final"
    exam_date: date


class GradeUpdateDTO(BaseModel):
    marks_obtained: float
    max_marks: float
    exam_type: str
    exam_date: date


class GradeResponseDTO(BaseModel):
    id: int
    student_id: int
    subject_id: int
    marks_obtained: float
    max_marks: float
    exam_type: str
    exam_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
