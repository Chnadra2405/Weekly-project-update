from datetime import datetime
from pydantic import BaseModel


class EnrollmentCreateDTO(BaseModel):
    student_id: int
    class_id: int


class EnrollmentResponseDTO(BaseModel):
    id: int
    student_id: int
    class_id: int
    enrolled_at: datetime

    model_config = {"from_attributes": True}
