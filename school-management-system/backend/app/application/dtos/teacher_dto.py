from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TeacherCreateDTO(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[str] = None


class TeacherUpdateDTO(TeacherCreateDTO):
    pass


class TeacherResponseDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
