"""Menu repository — persists MenuItem models."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.menu import MenuItem
from app.repositories.base_repository import BaseRepository


class MenuRepository(BaseRepository[MenuItem]):
    COLLECTION = "menu"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> MenuItem:
        return MenuItem.from_dict(rec)

    @staticmethod
    def _to_record(m: MenuItem) -> dict:
        return m.to_dict()

    def list_all(self) -> List[MenuItem]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[MenuItem]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: MenuItem) -> MenuItem:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: MenuItem) -> Optional[MenuItem]:
        if model.id is None:
            raise ValueError("Cannot update MenuItem without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_category(self, category: str) -> List[MenuItem]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, category=category)]

    def find_available(self) -> List[MenuItem]:
        return [m for m in self.list_all() if m.is_available]
