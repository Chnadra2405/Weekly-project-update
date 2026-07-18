from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Grade:
    student_id: int
    subject_id: int
    marks_obtained: float
    exam_date: date
    id: Optional[int] = None
    max_marks: float = 100.0
    exam_type: str = "Final"
    created_at: datetime = field(default_factory=datetime.utcnow)
