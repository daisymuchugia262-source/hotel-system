"""Inventory repository."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.inventory import InventoryItem
from app.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    COLLECTION = "inventory"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> InventoryItem:
        return InventoryItem.from_dict(rec)

    @staticmethod
    def _to_record(m: InventoryItem) -> dict:
        return m.to_dict()

    def list_all(self) -> List[InventoryItem]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[InventoryItem]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: InventoryItem) -> InventoryItem:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: InventoryItem) -> Optional[InventoryItem]:
        if model.id is None:
            raise ValueError("Cannot update InventoryItem without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_low_stock(self) -> List[InventoryItem]:
        return [i for i in self.list_all() if i.quantity_in_stock <= i.reorder_level]
