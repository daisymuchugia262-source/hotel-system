"""Invoice repository."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.invoice import Invoice
from app.repositories.base_repository import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    COLLECTION = "invoices"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Invoice:
        return Invoice.from_dict(rec)

    @staticmethod
    def _to_record(m: Invoice) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Invoice]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Invoice]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Invoice) -> Invoice:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Invoice) -> Optional[Invoice]:
        if model.id is None:
            raise ValueError("Cannot update Invoice without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_order(self, order_id: int) -> Optional[Invoice]:
        matches = self.store.find(self.COLLECTION, order_id=order_id)
        return self._to_model(matches[0]) if matches else None
