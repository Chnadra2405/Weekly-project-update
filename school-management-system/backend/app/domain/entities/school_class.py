from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SchoolClass:
    name: str
    grade_level: int
    academic_year: str
    id: Optional[int] = None
    section: str = "A"
    teacher_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
