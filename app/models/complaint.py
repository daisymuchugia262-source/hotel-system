from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Complaint:
    """A customer complaint logged for follow-up."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    subject: str = ""
    details: str = ""
    is_resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("Complaint must have a subject")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Complaint":
        return cls(**data)
