from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class MenuItem:
    """An item on the menu (food, drink, etc.)."""
    id: Optional[int] = None
    name: str = ""
    category: str = "general"
    price: Decimal = Decimal("0.00")
    is_available: bool = True
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Menu item must have a name")
        self.price = Decimal(str(self.price))
        if self.price < 0:
            raise ValueError("Price cannot be negative")

    def to_dict(self) -> dict:
        data = asdict(self)
        data["price"] = str(self.price)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MenuItem":
        data = data.copy()
        data["price"] = Decimal(str(data["price"]))
        return cls(**data)
