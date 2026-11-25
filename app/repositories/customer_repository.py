"""Customer repository."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    COLLECTION = "customers"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Customer:
        return Customer.from_dict(rec)

    @staticmethod
    def _to_record(m: Customer) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Customer]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Customer]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Customer) -> Customer:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Customer) -> Optional[Customer]:
        if model.id is None:
            raise ValueError("Cannot update Customer without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_phone(self, phone: str) -> Optional[Customer]:
        matches = self.store.find(self.COLLECTION, phone=phone)
        return self._to_model(matches[0]) if matches else None
