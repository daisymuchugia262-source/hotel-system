from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional


@dataclass
class InventoryItem:
    """A stock item tracked by the hotel."""
    id: Optional[int] = None
    name: str = ""
    unit: str = "pcs"
    quantity_in_stock: Decimal = Decimal("0.00")
    reorder_level: Decimal = Decimal("0.00")
    unit_cost: Decimal = Decimal("0.00")
    supplier_id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Inventory item must have a name")
        for f in ("quantity_in_stock", "reorder_level", "unit_cost"):
            setattr(self, f, Decimal(str(getattr(self, f))))

    def to_dict(self) -> dict:
        data = asdict(self)
        for f in ("quantity_in_stock", "reorder_level", "unit_cost"):
            data[f] = str(data[f])
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryItem":
        data = data.copy()
        for f in ("quantity_in_stock", "reorder_level", "unit_cost"):
            data[f] = Decimal(str(data[f]))
        return cls(**data)
