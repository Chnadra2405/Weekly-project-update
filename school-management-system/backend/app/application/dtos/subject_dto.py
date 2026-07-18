from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SubjectCreateDTO(BaseModel):
    name: str
    code: str
    class_id: int
    teacher_id: Optional[int] = None


class SubjectUpdateDTO(SubjectCreateDTO):
    pass


class SubjectResponseDTO(BaseModel):
    id: int
    name: str
    code: str
    class_id: int
    teacher_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
