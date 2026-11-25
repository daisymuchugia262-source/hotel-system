"""
phase2_setup.py — Completes Phase 2 (Data Layer / Repositories).

Creates and fills:
  - app/database/session.py
  - app/repositories/base_repository.py
  - app/repositories/__init__.py
  - 10 concrete repositories
  - scripts/seed_menu.py
  - data/menu.json (seeded)
  - tests/test_repositories.py

Run from: C:\\Users\\user\\OneDrive\\Desktop\\scaffold.sh\\backend
    python phase2_setup.py

Idempotent — safe to re-run.
"""

from pathlib import Path
import json


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote  {path}")


def write_json_if_missing(path: Path, initial: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(initial, indent=2), encoding="utf-8")
        print(f"  created {path}")
    else:
        print(f"  exists  {path}")


# ===========================================================================
# FILE CONTENTS
# ===========================================================================

SESSION_PY = r'''"""
JSON file store — generic read/write helper for repositories.

Each collection lives in its own JSON file:
    {
        "next_id": 3,
        "items": [ {...}, {...} ]
    }

No imports from services/ or api/.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class JsonStore:
    """Persists collections to individual JSON files under a data directory."""

    def __init__(self, data_dir: Path | str | None = None) -> None:
        if data_dir is None:
            # default: <backend>/data/
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ---- internal ----
    def _path(self, collection: str) -> Path:
        return self.data_dir / f"{collection}.json"

    def _read_raw(self, collection: str) -> Dict[str, Any]:
        path = self._path(collection)
        if not path.exists():
            return {"next_id": 1, "items": []}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"next_id": 1, "items": []}

    def _write_raw(self, collection: str, data: Dict[str, Any]) -> None:
        path = self._path(collection)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)  # atomic on Windows and POSIX

    # ---- public API ----
    def all(self, collection: str) -> List[Dict[str, Any]]:
        return list(self._read_raw(collection)["items"])

    def get(self, collection: str, record_id: int) -> Dict[str, Any] | None:
        for rec in self._read_raw(collection)["items"]:
            if rec.get("id") == record_id:
                return dict(rec)
        return None

    def create(self, collection: str, record: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read_raw(collection)
        record = dict(record)
        record["id"] = data["next_id"]
        data["next_id"] += 1
        data["items"].append(record)
        self._write_raw(collection, data)
        return dict(record)

    def update(self, collection: str, record_id: int,
               updates: Dict[str, Any]) -> Dict[str, Any] | None:
        data = self._read_raw(collection)
        for i, rec in enumerate(data["items"]):
            if rec.get("id") == record_id:
                rec.update(updates)
                rec["id"] = record_id
                data["items"][i] = rec
                self._write_raw(collection, data)
                return dict(rec)
        return None

    def delete(self, collection: str, record_id: int) -> bool:
        data = self._read_raw(collection)
        before = len(data["items"])
        data["items"] = [r for r in data["items"] if r.get("id") != record_id]
        if len(data["items"]) == before:
            return False
        self._write_raw(collection, data)
        return True

    def find(self, collection: str, **filters) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for rec in self._read_raw(collection)["items"]:
            if all(rec.get(k) == v for k, v in filters.items()):
                results.append(dict(rec))
        return results
'''


BASE_REPOSITORY_PY = r'''"""
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
'''


MENU_REPOSITORY_PY = r'''"""Menu repository — persists MenuItem models."""
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
'''


USER_REPOSITORY_PY = r'''"""User repository — persists User models."""
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
'''


CUSTOMER_REPOSITORY_PY = r'''"""Customer repository."""
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
'''


ORDER_REPOSITORY_PY = r'''"""Order repository — persists Order models and their items."""
from __future__ import annotations

from typing import List, Optional

from app.database.session import JsonStore
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    COLLECTION = "orders"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Order:
        items = [OrderItem.from_dict(i) for i in rec.get("items", [])]
        order = Order.from_dict(rec)
        order.items = items
        return order

    @staticmethod
    def _to_record(m: Order) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Order]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Order]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Order) -> Order:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Order) -> Optional[Order]:
        if model.id is None:
            raise ValueError("Cannot update Order without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_customer(self, customer_id: int) -> List[Order]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, customer_id=customer_id)]

    def find_by_status(self, status: str) -> List[Order]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, status=status)]
'''


PAYMENT_REPOSITORY_PY = r'''"""Payment repository."""
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from app.database.session import JsonStore
from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    COLLECTION = "payments"

    def __init__(self, store: Optional[JsonStore] = None) -> None:
        self.store = store or JsonStore()

    @staticmethod
    def _to_model(rec: dict) -> Payment:
        return Payment.from_dict(rec)

    @staticmethod
    def _to_record(m: Payment) -> dict:
        return m.to_dict()

    def list_all(self) -> List[Payment]:
        return [self._to_model(r) for r in self.store.all(self.COLLECTION)]

    def get_by_id(self, record_id: int) -> Optional[Payment]:
        rec = self.store.get(self.COLLECTION, record_id)
        return self._to_model(rec) if rec else None

    def create(self, model: Payment) -> Payment:
        rec = self.store.create(self.COLLECTION, self._to_record(model))
        return self._to_model(rec)

    def update(self, model: Payment) -> Optional[Payment]:
        if model.id is None:
            raise ValueError("Cannot update Payment without id")
        rec = self.store.update(self.COLLECTION, model.id, self._to_record(model))
        return self._to_model(rec) if rec else None

    def delete(self, record_id: int) -> bool:
        return self.store.delete(self.COLLECTION, record_id)

    def find_by_order(self, order_id: int) -> List[Payment]:
        return [self._to_model(r) for r in self.store.find(self.COLLECTION, order_id=order_id)]

    def total_paid_for_order(self, order_id: int) -> Decimal:
        total = Decimal("0.00")
        for p in self.find_by_order(order_id):
            if p.status.value == "completed":
                total += p.amount
        return total
'''


INVOICE_REPOSITORY_PY = r'''"""Invoice repository."""
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
'''


INVENTORY_REPOSITORY_PY = r'''"""Inventory repository."""
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
'''


SUPPLIER_REPOSITORY_PY = r'''"""Supplier repository."""
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
'''


TABLE_REPOSITORY_PY = r'''"""Restaurant table repository."""
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
'''


ROOM_REPOSITORY_PY = r'''"""Room repository."""
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
'''


REPOS_INIT_PY = r'''"""Concrete repositories — one per entity."""
from app.repositories.menu_repository      import MenuRepository
from app.repositories.user_repository      import UserRepository
from app.repositories.customer_repository  import CustomerRepository
from app.repositories.order_repository     import OrderRepository
from app.repositories.payment_repository   import PaymentRepository
from app.repositories.invoice_repository   import InvoiceRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.supplier_repository  import SupplierRepository
from app.repositories.table_repository     import TableRepository
from app.repositories.room_repository      import RoomRepository

__all__ = [
    "MenuRepository", "UserRepository", "CustomerRepository",
    "OrderRepository", "PaymentRepository", "InvoiceRepository",
    "InventoryRepository", "SupplierRepository",
    "TableRepository", "RoomRepository",
]
'''


SEED_MENU_PY = r'''"""
Seed data/menu.json with sample menu items.
Run from backend/:  python scripts/seed_menu.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
from app.repositories.menu_repository import MenuRepository
from app.models.menu import MenuItem


SAMPLE_ITEMS = [
    ("Chicken Biryani", "food",    "450.00"),
    ("Beef Burger",     "food",    "350.00"),
    ("Pizza (Large)",   "food",    "800.00"),
    ("Fried Chicken",   "food",    "600.00"),
    ("Fish & Chips",    "food",    "550.00"),
    ("Soda (500ml)",    "drink",   "100.00"),
    ("Juice (300ml)",   "drink",   "150.00"),
    ("Ice Cream",       "dessert", "200.00"),
    ("Coffee",          "drink",   "120.00"),
    ("Water (1L)",      "drink",    "80.00"),
]


def main() -> None:
    repo = MenuRepository()
    existing = repo.list_all()
    if existing:
        print(f"menu.json already has {len(existing)} items. Skipping seed.")
        return

    for name, category, price in SAMPLE_ITEMS:
        repo.create(MenuItem(name=name, category=category, price=Decimal(price)))

    print(f"Seeded {len(SAMPLE_ITEMS)} menu items into data/menu.json")


if __name__ == "__main__":
    main()
'''


TEST_REPOSITORIES_PY = r'''"""
Phase 2 tests — repositories persist models correctly.
Run:  pytest tests/test_repositories.py -v
"""
from decimal import Decimal
import json
import pytest

from app.database.session import JsonStore
from app.models.menu import MenuItem
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.inventory import InventoryItem
from app.models.supplier import Supplier
from app.models.table import RestaurantTable
from app.models.room import Room
from app.repositories.menu_repository      import MenuRepository
from app.repositories.user_repository      import UserRepository
from app.repositories.customer_repository  import CustomerRepository
from app.repositories.order_repository     import OrderRepository
from app.repositories.payment_repository   import PaymentRepository
from app.repositories.invoice_repository   import InvoiceRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.supplier_repository  import SupplierRepository
from app.repositories.table_repository     import TableRepository
from app.repositories.room_repository      import RoomRepository
from app.core.constants import (
    OrderStatus, PaymentMethod, InvoiceStatus, UserRole,
)


@pytest.fixture
def temp_store(tmp_path):
    return JsonStore(data_dir=tmp_path)


# -------------------- Menu --------------------
def test_menu_crud(temp_store):
    repo = MenuRepository(store=temp_store)
    created = repo.create(MenuItem(name="Biryani", price="450.00", category="food"))
    assert created.id is not None

    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.price == Decimal("450.00")

    fetched.price = Decimal("500.00")
    updated = repo.update(fetched)
    assert updated.price == Decimal("500.00")

    assert repo.delete(created.id) is True
    assert repo.get_by_id(created.id) is None


def test_menu_find_by_category(temp_store):
    repo = MenuRepository(store=temp_store)
    repo.create(MenuItem(name="A", price="100", category="food"))
    repo.create(MenuItem(name="B", price="120", category="drink"))
    repo.create(MenuItem(name="C", price="150", category="drink"))
    assert len(repo.list_all()) == 3
    assert len(repo.find_by_category("drink")) == 2


# -------------------- User --------------------
def test_user_create_and_find(temp_store):
    repo = UserRepository(store=temp_store)
    u = User(username="alice", email="a@x.com",
             role=UserRole.CASHIER, password_hash="hashed_pw")
    created = repo.create(u)
    assert created.id is not None

    # password_hash must be persisted
    raw = json.loads((temp_store.data_dir / "users.json").read_text())
    assert raw["items"][0]["password_hash"] == "hashed_pw"

    assert repo.find_by_username("alice").id == created.id
    assert repo.find_by_email("a@x.com").id == created.id


# -------------------- Customer --------------------
def test_customer_crud(temp_store):
    repo = CustomerRepository(store=temp_store)
    c = repo.create(Customer(full_name="Bob", phone="+254700000000"))
    assert c.id is not None
    assert repo.find_by_phone("+254700000000").id == c.id


# -------------------- Order + items --------------------
def test_order_with_items(temp_store):
    repo = OrderRepository(store=temp_store)
    o = Order(customer_id=1, table_id=2, status=OrderStatus.PENDING)

    line1 = OrderItem(item_name="Biryani", unit_price="450", quantity=2)
    line1.compute_subtotal()
    line2 = OrderItem(item_name="Soda", unit_price="100", quantity=3)
    line2.compute_subtotal()
    o.items = [line1, line2]
    o.total = sum(i.subtotal for i in o.items)

    created = repo.create(o)
    assert created.id is not None

    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert len(fetched.items) == 2
    assert fetched.items[0].item_name == "Biryani"
    assert fetched.total == Decimal("1200.00")


# -------------------- Payment --------------------
def test_payment_multi_and_total(temp_store):
    repo = PaymentRepository(store=temp_store)
    repo.create(Payment(order_id=1, amount="500", method=PaymentMethod.CASH))
    repo.create(Payment(order_id=1, amount="400", method=PaymentMethod.MPESA))
    repo.create(Payment(order_id=2, amount="200", method=PaymentMethod.CASH))

    assert len(repo.find_by_order(1)) == 2
    assert repo.total_paid_for_order(1) == Decimal("900.00")
    assert repo.total_paid_for_order(2) == Decimal("200.00")


# -------------------- Invoice --------------------
def test_invoice_crud(temp_store):
    repo = InvoiceRepository(store=temp_store)
    inv = repo.create(Invoice(
        order_id=1, invoice_number="INV-001",
        subtotal="900", tax="144", total="1044",
        status=InvoiceStatus.ISSUED,
    ))
    assert inv.id is not None
    assert repo.find_by_order(1).total == Decimal("1044")


# -------------------- Inventory --------------------
def test_inventory_low_stock(temp_store):
    repo = InventoryRepository(store=temp_store)
    repo.create(InventoryItem(name="Rice", unit="kg",
                              quantity_in_stock="50", reorder_level="10"))
    repo.create(InventoryItem(name="Oil", unit="litre",
                              quantity_in_stock="2", reorder_level="5"))

    low = repo.find_low_stock()
    assert len(low) == 1
    assert low[0].name == "Oil"


# -------------------- Supplier --------------------
def test_supplier_crud(temp_store):
    repo = SupplierRepository(store=temp_store)
    s = repo.create(Supplier(name="Acme Ltd", phone="+254711"))
    assert s.id is not None
    assert repo.get_by_id(s.id).name == "Acme Ltd"


# -------------------- Table --------------------
def test_table_crud(temp_store):
    repo = TableRepository(store=temp_store)
    t = repo.create(RestaurantTable(table_number="T1", seats=4))
    assert t.id is not None
    assert repo.list_all()[0].table_number == "T1"


# -------------------- Room --------------------
def test_room_available(temp_store):
    repo = RoomRepository(store=temp_store)
    r = repo.create(Room(room_number="101", price_per_night="3500"))
    assert r.id is not None
    assert len(repo.find_available()) == 1


# -------------------- Persistence across instances --------------------
def test_data_survives_new_store_instance(temp_store):
    """A new repo with the same data_dir must see the same records."""
    repo1 = MenuRepository(store=temp_store)
    repo1.create(MenuItem(name="Item A", price="100"))

    repo2 = MenuRepository(store=JsonStore(data_dir=temp_store.data_dir))
    assert len(repo2.list_all()) == 1
    assert repo2.list_all()[0].name == "Item A"
'''


# ===========================================================================
# BUILD
# ===========================================================================
def build() -> None:
    root = Path.cwd()

    if not (root / "app").exists():
        print(f"ERROR: no 'app' folder in {root}")
        print("       Run from C:\\Users\\user\\OneDrive\\Desktop\\scaffold.sh\\backend")
        return

    print(f"\nPhase 2 setup in: {root}\n")

    # 1. Database session
    print("[1/5] Database session (JSON store)...")
    write(root / "app" / "database" / "session.py", SESSION_PY)

    # 2. Base repository
    print("\n[2/5] Base repository (abstract CRUD)...")
    write(root / "app" / "repositories" / "base_repository.py", BASE_REPOSITORY_PY)

    # 3. Concrete repositories
    print("\n[3/5] Concrete repositories (10 files)...")
    repo_dir = root / "app" / "repositories"
    write(repo_dir / "menu_repository.py",      MENU_REPOSITORY_PY)
    write(repo_dir / "user_repository.py",      USER_REPOSITORY_PY)
    write(repo_dir / "customer_repository.py",  CUSTOMER_REPOSITORY_PY)
    write(repo_dir / "order_repository.py",     ORDER_REPOSITORY_PY)
    write(repo_dir / "payment_repository.py",   PAYMENT_REPOSITORY_PY)
    write(repo_dir / "invoice_repository.py",   INVOICE_REPOSITORY_PY)
    write(repo_dir / "inventory_repository.py", INVENTORY_REPOSITORY_PY)
    write(repo_dir / "supplier_repository.py",  SUPPLIER_REPOSITORY_PY)
    write(repo_dir / "table_repository.py",     TABLE_REPOSITORY_PY)
    write(repo_dir / "room_repository.py",      ROOM_REPOSITORY_PY)
    write(repo_dir / "__init__.py",             REPOS_INIT_PY)

    # 4. Scripts + data
    print("\n[4/5] Scripts and seed data...")
    write(root / "scripts" / "seed_menu.py", SEED_MENU_PY)
    for coll in ["menu", "users", "customers", "orders", "payments",
                 "invoices", "inventory", "suppliers", "tables", "rooms"]:
        write_json_if_missing(root / "data" / f"{coll}.json",
                              {"next_id": 1, "items": []})

    # 5. Tests
    print("\n[5/5] Tests...")
    write(root / "tests" / "test_repositories.py", TEST_REPOSITORIES_PY)

    print("\nPhase 2 setup complete.")
    print("\nNext steps:")
    print("  1) python scripts\\seed_menu.py")
    print("  2) pytest tests\\test_repositories.py -v")
    print("  3) Expect: 12 passed\n")


if __name__ == "__main__":
    build()