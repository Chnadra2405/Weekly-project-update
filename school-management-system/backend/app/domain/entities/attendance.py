from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Attendance:
    student_id: int
    class_id: int
    date: date
    id: Optional[int] = None
    status: str = "Present"
    created_at: datetime = field(default_factory=datetime.utcnow)
