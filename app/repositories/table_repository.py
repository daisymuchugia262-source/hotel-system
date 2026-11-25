"""Restaurant table repository."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.table import RestaurantTable
from app.repositories.base_repository import BaseRepository


class TableRepository(BaseRepository[RestaurantTable]):
    COLLECTION = "tables"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> RestaurantTable:
        return RestaurantTable.from_dict(rec)

    @staticmethod
    def _to_record(m: RestaurantTable) -> dict:
        return m.to_dict()

    def list_all(self) -> List[RestaurantTable]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[RestaurantTable]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: RestaurantTable) -> RestaurantTable:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: RestaurantTable) -> Optional[RestaurantTable]:
        if model.id is None:
            raise ValueError("Cannot update RestaurantTable without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)
