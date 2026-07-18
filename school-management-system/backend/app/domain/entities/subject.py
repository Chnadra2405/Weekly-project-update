from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Subject:
    name: str
    code: str
    class_id: int
    id: Optional[int] = None
    teacher_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
