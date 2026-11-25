from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """A hotel guest or restaurant customer."""
    id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    email: str = ""
    id_number: str = ""
    address: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        if not self.full_name.strip():
            raise ValueError("Customer must have a full name")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        return cls(**data)
