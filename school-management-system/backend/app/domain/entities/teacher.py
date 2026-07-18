from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Teacher:
    first_name: str
    last_name: str
    email: str
    id: Optional[int] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
