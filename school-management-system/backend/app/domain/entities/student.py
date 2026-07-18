from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Student:
    first_name: str
    last_name: str
    id: Optional[int] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
