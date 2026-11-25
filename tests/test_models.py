"""
Phase 1 smoke tests — verify all domain models import and round-trip.
Run:  pytest tests/test_models.py -v
"""
from decimal import Decimal
import pytest

from app.models import (
    User, Customer, Employee, MenuItem, Order, OrderItem,
    Payment, Invoice, RestaurantTable, Room, InventoryItem,
    Supplier, Complaint, AuditLog,
)
from app.core.constants import (
    UserRole, OrderStatus, PaymentMethod, InvoiceStatus,
    RoomStatus, TableStatus,
)


def test_menu_item_roundtrip():
    item = MenuItem(name="Chicken Biryani", price="450.00", category="food")
    assert item.price == Decimal("450.00")
    assert item.to_dict()["price"] == "450.00"
    assert MenuItem.from_dict(item.to_dict()).price == Decimal("450.00")


def test_order_item_subtotal():
    line = OrderItem(item_name="Chicken Biryani", unit_price="450.00", quantity=2)
    assert line.compute_subtotal() == Decimal("900.00")


def test_order_totals_with_items():
    order = Order(customer_id=1, table_id=3, status=OrderStatus.PENDING)
    order.items.append(OrderItem(item_name="A", unit_price="450.00", quantity=2))
    order.items.append(OrderItem(item_name="B", unit_price="100.00", quantity=3))
    for line in order.items:
        line.compute_subtotal()
    order.total = sum(line.subtotal for line in order.items)
    assert order.total == Decimal("1200.00")
    d = order.to_dict()
    assert d["status"] == "pending"
    assert len(d["items"]) == 2


def test_multiple_payments_accumulate():
    p1 = Payment(order_id=1, amount="500.00", method=PaymentMethod.CASH)
    p2 = Payment(order_id=1, amount="400.00", method=PaymentMethod.MPESA)
    assert p1.amount + p2.amount == Decimal("900.00")


def test_payment_rejects_zero():
    with pytest.raises(ValueError):
        Payment(order_id=1, amount="0")


def test_menu_item_rejects_empty_name():
    with pytest.raises(ValueError):
        MenuItem(name="", price="100")


def test_order_item_rejects_zero_quantity():
    with pytest.raises(ValueError):
        OrderItem(item_name="x", unit_price="10", quantity=0)


def test_all_models_construct():
    User(username="alice", email="a@x.com", role=UserRole.CASHIER)
    Customer(full_name="Bob")
    Employee(full_name="Carol", salary="50000")
    Invoice(order_id=1, invoice_number="INV-001", total="900.00", status=InvoiceStatus.ISSUED)
    RestaurantTable(table_number="T1", seats=4, status=TableStatus.FREE)
    Room(room_number="101", price_per_night="3500", status=RoomStatus.AVAILABLE)
    InventoryItem(name="Rice", unit="kg", quantity_in_stock="50")
    Supplier(name="Acme Ltd")
    Complaint(subject="Cold food")
    AuditLog(action="login", entity="user", entity_id=1)


def test_decimal_math_is_exact():
    """Billing systems must never lose money to float rounding."""
    p1 = Payment(order_id=1, amount="0.1")
    p2 = Payment(order_id=1, amount="0.2")
    assert p1.amount + p2.amount == Decimal("0.3")
