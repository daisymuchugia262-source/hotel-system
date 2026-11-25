"""Room repository."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.room import Room
from app.repositories.base_repository import BaseRepository


class RoomRepository(BaseRepository[Room]):
    COLLECTION = "rooms"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Room:
        return Room.from_dict(rec)

    @staticmethod
    def _to_record(m: Room) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Room]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Room]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Room) -> Room:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Room) -> Optional[Room]:
        if model.id is None:
            raise ValueError("Cannot update Room without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_available(self) -> List[Room]:
        return [r for r in self.list_all() if r.status.value == "available"]
