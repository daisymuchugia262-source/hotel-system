from dataclasses import dataclass, asdict
from typing import Optional
from app.core.constants import TableStatus


@dataclass
class RestaurantTable:
    """A physical dining table."""
    id: Optional[int] = None
    table_number: str = ""
    seats: int = 4
    status: TableStatus = TableStatus.FREE
    location: str = ""

    def __post_init__(self) -> None:
        if not self.table_number:
            raise ValueError("Table must have a number")
        if self.seats <= 0:
            raise ValueError("Table must have at least 1 seat")
        if isinstance(self.status, str):
            self.status = TableStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "RestaurantTable":
        data = data.copy()
        if isinstance(data.get("status"), str):
            data["status"] = TableStatus(data["status"])
        return cls(**data)
