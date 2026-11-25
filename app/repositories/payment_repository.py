"""Payment repository."""
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from app.database.session import JsonStore
from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    COLLECTION = "payments"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Payment:
        return Payment.from_dict(rec)

    @staticmethod
    def _to_record(m: Payment) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Payment]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Payment]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Payment) -> Payment:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Payment) -> Optional[Payment]:
        if model.id is None:
            raise ValueError("Cannot update Payment without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_order(self, order_id: int) -> List[Payment]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, order_id=order_id)]

    def total_paid_for_order(self, order_id: int) -> Decimal:
        total = Decimal("0.00")
        for p in self.find_by_order(order_id):
            if p.status.value == "completed":
                total += p.amount
        return total
