from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional
from app.core.constants import RoomStatus


@dataclass
class Room:
    """A hotel room."""
    id: Optional[int] = None
    room_number: str = ""
    room_type: str = "standard"
    price_per_night: Decimal = Decimal("0.00")
    capacity: int = 2
    status: RoomStatus = RoomStatus.AVAILABLE

    def __post_init__(self) -> None:
        if not self.room_number:
            raise ValueError("Room must have a number")
        self.price_per_night = Decimal(str(self.price_per_night))
        if self.price_per_night < 0:
            raise ValueError("Price cannot be negative")
        if isinstance(self.status, str):
            self.status = RoomStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["price_per_night"] = str(self.price_per_night)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Room":
        data = data.copy()
        data["price_per_night"] = Decimal(str(data["price_per_night"]))
        if isinstance(data.get("status"), str):
            data["status"] = RoomStatus(data["status"])
        return cls(**data)
