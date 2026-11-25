from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Supplier:
    """A vendor who supplies inventory."""
    id: Optional[int] = None
    name: str = ""
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Supplier must have a name")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Supplier":
        return cls(**data)
