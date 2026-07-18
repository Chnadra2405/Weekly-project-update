from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Enrollment:
    student_id: int
    class_id: int
    id: Optional[int] = None
    enrolled_at: datetime = field(default_factory=datetime.utcnow)
