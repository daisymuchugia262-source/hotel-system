"""User repository — persists User models."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    COLLECTION = "users"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> User:
        return User.from_dict(rec)

    def _to_record(self, m: User) -> dict:
        return m.to_dict(include_hash=True)

    def list_all(self) -> List[User]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[User]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: User) -> User:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: User) -> Optional[User]:
        if model.id is None:
            raise ValueError("Cannot update User without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_username(self, username: str) -> Optional[User]:
        matches = self.store.find(self.COLLECTION, username=username)
        return self._to_model(matches[0]) if matches else None

    def find_by_email(self, email: str) -> Optional[User]:
        matches = self.store.find(self.COLLECTION, email=email)
        return self._to_model(matches[0]) if matches else None
