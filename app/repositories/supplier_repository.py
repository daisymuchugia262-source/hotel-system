"""Supplier repository."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.supplier import Supplier
from app.repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    COLLECTION = "suppliers"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Supplier:
        return Supplier.from_dict(rec)

    @staticmethod
    def _to_record(m: Supplier) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Supplier]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Supplier]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Supplier) -> Supplier:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Supplier) -> Optional[Supplier]:
        if model.id is None:
            raise ValueError("Cannot update Supplier without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)
