from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class AuditLog:
    """Record of an important action (for traceability)."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: str = ""
    entity: str = ""
    entity_id: Optional[int] = None
    details: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLog":
        return cls(**data)
