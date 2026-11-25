"""
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
