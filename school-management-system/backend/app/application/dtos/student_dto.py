from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class StudentCreateDTO(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentUpdateDTO(StudentCreateDTO):
    pass


class StudentResponseDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
