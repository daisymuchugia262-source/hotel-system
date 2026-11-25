"""Order repository — persists Order models and their items."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    COLLECTION = "orders"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Order:
        items = [OrderItem.from_dict(i) for i in rec.get("items", [])]
        order = Order.from_dict(rec)
        order.items = items
        return order

    @staticmethod
    def _to_record(m: Order) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Order]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Order]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Order) -> Order:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Order) -> Optional[Order]:
        if model.id is None:
            raise ValueError("Cannot update Order without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_customer(self, customer_id: int) -> List[Order]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, customer_id=customer_id)]

    def find_by_status(self, status: str) -> List[Order]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, status=status)]
