from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.core.constants import PaymentMethod, PaymentStatus


@dataclass
class Payment:
    """A single payment attempt against an order. May be partial."""
    id: Optional[int] = None
    order_id: Optional[int] = None
    amount: Decimal = Decimal("0.00")
    method: PaymentMethod = PaymentMethod.CASH
    status: PaymentStatus = PaymentStatus.COMPLETED
    reference: str = ""
    paid_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.amount = Decimal(str(self.amount))
        if self.amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if isinstance(self.method, str):
            self.method = PaymentMethod(self.method)
        if isinstance(self.status, str):
            self.status = PaymentStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["amount"] = str(self.amount)
        data["method"] = self.method.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        data = data.copy()
        data["amount"] = Decimal(str(data["amount"]))
        if isinstance(data.get("method"), str):
            data["method"] = PaymentMethod(data["method"])
        if isinstance(data.get("status"), str):
            data["status"] = PaymentStatus(data["status"])
        return cls(**data)
