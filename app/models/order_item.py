from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional


@dataclass
class OrderItem:
    """One line in an order: a menu item + quantity + computed subtotal."""
    id: Optional[int] = None
    order_id: Optional[int] = None
    menu_item_id: Optional[int] = None
    item_name: str = ""
    unit_price: Decimal = Decimal("0.00")
    quantity: int = 1
    subtotal: Decimal = Decimal("0.00")

    def __post_init__(self) -> None:
        self.unit_price = Decimal(str(self.unit_price))
        self.subtotal = Decimal(str(self.subtotal))
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")

    def compute_subtotal(self) -> Decimal:
        self.subtotal = (self.unit_price * self.quantity).quantize(Decimal("0.01"))
        return self.subtotal

    def to_dict(self) -> dict:
        data = asdict(self)
        data["unit_price"] = str(self.unit_price)
        data["subtotal"] = str(self.subtotal)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        data = data.copy()
        data["unit_price"] = Decimal(str(data["unit_price"]))
        data["subtotal"] = Decimal(str(data["subtotal"]))
        return cls(**data)
