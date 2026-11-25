from __future__ import annotations
from typing import List, Optional
from app.core.exceptions import NotFoundError
from app.models.menu import MenuItem
from app.repositories.menu_repository import MenuRepository


class MenuService:
    def __init__(self, repo: Optional[MenuRepository] = None) -> None:
        self.repo = repo or MenuRepository()

    def list_menu(self) -> List[MenuItem]:
        return self.repo.list_all()

    def list_available(self) -> List[MenuItem]:
        return self.repo.find_available()

    def list_by_category(self, category: str) -> List[MenuItem]:
        return self.repo.find_by_category(category)

    def get_item(self, item_id: int) -> MenuItem:
        item = self.repo.get_by_id(item_id)
        if item is None:
            raise NotFoundError(f"Menu item {item_id} not found")
        return item

    def add_item(self, item: MenuItem) -> MenuItem:
        return self.repo.create(item)

    def update_item(self, item: MenuItem) -> MenuItem:
        if item.id is None:
            raise ValueError("Cannot update item without id")
        updated = self.repo.update(item)
        if updated is None:
            raise NotFoundError(f"Menu item {item.id} not found")
        return updated
