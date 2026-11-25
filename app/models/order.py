from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.core.constants import OrderStatus


@dataclass
class Order:
    """A customer order — one bill, made up of many OrderItem objects."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    table_id: Optional[int] = None
    status: OrderStatus = OrderStatus.PENDING
    items: List["OrderItem"] = field(default_factory=list)
    total: Decimal = Decimal("0.00")
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.total = Decimal(str(self.total))
        if isinstance(self.status, str):
            self.status = OrderStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["total"] = str(self.total)
        data["items"] = [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in self.items
        ]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        data = data.copy()
        data.pop("items", None)
        data["total"] = Decimal(str(data["total"]))
        if isinstance(data.get("status"), str):
            data["status"] = OrderStatus(data["status"])
        return cls(**data)
