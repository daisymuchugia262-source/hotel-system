from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.core.constants import InvoiceStatus


@dataclass
class Invoice:
    """A formal invoice generated from an order."""
    id: Optional[int] = None
    order_id: Optional[int] = None
    invoice_number: str = ""
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issued_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        for f in ("subtotal", "tax", "total"):
            setattr(self, f, Decimal(str(getattr(self, f))))
        if isinstance(self.status, str):
            self.status = InvoiceStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["subtotal"] = str(self.subtotal)
        data["tax"] = str(self.tax)
        data["total"] = str(self.total)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Invoice":
        data = data.copy()
        for f in ("subtotal", "tax", "total"):
            data[f] = Decimal(str(data[f]))
        if isinstance(data.get("status"), str):
            data["status"] = InvoiceStatus(data["status"])
        return cls(**data)
