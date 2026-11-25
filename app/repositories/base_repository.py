"""
Abstract base repository — CRUD contract every concrete repo implements.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Repositories accept/return models, not dicts."""

    COLLECTION: str = ""

    @abstractmethod
    def list_all(self) -> List[T]:
        ...

    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[T]:
        ...

    @abstractmethod
    def create(self, model: T) -> T:
        ...

    @abstractmethod
    def update(self, model: T) -> Optional[T]:
        ...

    @abstractmethod
    def delete(self, record_id: int) -> bool:
        ...
