from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClassCreateDTO(BaseModel):
    name: str
    grade_level: int
    section: str = "A"
    teacher_id: Optional[int] = None
    academic_year: str


class ClassUpdateDTO(ClassCreateDTO):
    pass


class ClassResponseDTO(BaseModel):
    id: int
    name: str
    grade_level: int
    section: str
    teacher_id: Optional[int] = None
    academic_year: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
