"""
Phase 3 tests — business rules.
Run:  python -m pytest tests/test_services.py -v
"""
from decimal import Decimal
import pytest

from app.database.session import JsonStore
from app.models.menu import MenuItem
from app.repositories.menu_repository      import MenuRepository
from app.repositories.order_repository     import OrderRepository
from app.repositories.payment_repository   import PaymentRepository
from app.repositories.invoice_repository   import InvoiceRepository
from app.repositories.user_repository      import UserRepository
from app.services.menu_service      import MenuService
from app.services.order_service     import OrderService
from app.services.payment_service   import PaymentService
from app.services.billing_service   import BillingService
from app.services.auth_service      import AuthService
from app.core.constants import OrderStatus, PaymentMethod, UserRole
from app.core.exceptions import (
    NotFoundError, ValidationError, OrderNotPayableError, AuthenticationError,
)


@pytest.fixture
def stores(tmp_path):
    s = JsonStore(data_dir=tmp_path)
    return {
        "menu":     MenuRepository(store=s),
        "orders":   OrderRepository(store=s),
        "payments": PaymentRepository(store=s),
        "invoices": InvoiceRepository(store=s),
        "users":    UserRepository(store=s),
    }


@pytest.fixture
def menu_with_items(stores):
    repo = stores["menu"]
    return [
        repo.create(MenuItem(name="Biryani", price="450.00", category="food")),
        repo.create(MenuItem(name="Burger",  price="350.00", category="food")),
        repo.create(MenuItem(name="Soda",    price="100.00", category="drink")),
    ]


def test_menu_service_lists_and_gets(stores, menu_with_items):
    svc = MenuService(repo=stores["menu"])
    assert len(svc.list_menu()) == 3
    assert svc.get_item(menu_with_items[0].id).name == "Biryani"


def test_menu_service_raises_on_missing(stores):
    svc = MenuService(repo=stores["menu"])
    with pytest.raises(NotFoundError):
        svc.get_item(999)


def test_create_order_computes_total(stores, menu_with_items):
    svc = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    biryani, burger, _ = menu_with_items
    order = svc.create_order([
        {"menu_item_id": biryani.id, "quantity": 2},
        {"menu_item_id": burger.id,  "quantity": 3},
    ])
    assert len(order.items) == 2
    assert order.total == Decimal("1950.00")
    assert order.items[0].subtotal == Decimal("900.00")
    assert order.items[1].subtotal == Decimal("1050.00")


def test_create_order_rejects_empty(stores, menu_with_items):
    svc = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    with pytest.raises(ValidationError):
        svc.create_order([])


def test_create_order_rejects_unknown_item(stores):
    svc = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    with pytest.raises(NotFoundError):
        svc.create_order([{"menu_item_id": 999, "quantity": 1}])


def test_create_order_rejects_zero_qty(stores, menu_with_items):
    svc = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    with pytest.raises(ValueError):
        svc.create_order([{"menu_item_id": menu_with_items[0].id, "quantity": 0}])


def test_set_status(stores, menu_with_items):
    svc = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    order = svc.create_order([{"menu_item_id": menu_with_items[0].id, "quantity": 1}])
    updated = svc.set_status(order.id, OrderStatus.PREPARING)
    assert updated.status == OrderStatus.PREPARING


def _make_order(stores, menu_with_items, qty_biryani=2, qty_burger=3):
    svc = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    return svc.create_order([
        {"menu_item_id": menu_with_items[0].id, "quantity": qty_biryani},
        {"menu_item_id": menu_with_items[1].id, "quantity": qty_burger},
    ])


def test_partial_payment_keeps_balance(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    svc = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])
    svc.add_payment(order.id, "500")
    assert svc.balance(order.id) == Decimal("1450.00")
    assert svc.is_fully_paid(order.id) is False


def test_exact_payment_clears_balance(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    svc = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])
    svc.add_payment(order.id, "1950")
    assert svc.balance(order.id) == Decimal("0.00")
    assert svc.is_fully_paid(order.id) is True


def test_overpayment_gives_change(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    svc = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])
    svc.add_payment(order.id, "2000")
    assert svc.balance(order.id) == Decimal("0.00")
    assert svc.change(order.id) == Decimal("50.00")


def test_multiple_payments_accumulate(stores, menu_with_items):
    """Your original requirement: pay more than once if balance remains."""
    order = _make_order(stores, menu_with_items)
    svc = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])

    svc.add_payment(order.id, "500")
    assert svc.balance(order.id) == Decimal("1450.00")

    svc.add_payment(order.id, "700")
    assert svc.balance(order.id) == Decimal("750.00")

    svc.add_payment(order.id, "800")
    assert svc.balance(order.id) == Decimal("0.00")
    assert svc.change(order.id) == Decimal("50.00")
    assert svc.total_paid(order.id) == Decimal("2000.00")


def test_payment_rejects_zero(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    svc = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])
    with pytest.raises(ValidationError):
        svc.add_payment(order.id, "0")


def test_payment_rejects_cancelled_order(stores, menu_with_items):
    svc_order = OrderService(order_repo=stores["orders"], menu_repo=stores["menu"])
    order = _make_order(stores, menu_with_items)
    svc_order.set_status(order.id, OrderStatus.CANCELLED)

    svc_pay = PaymentService(payment_repo=stores["payments"],
                             order_repo=stores["orders"])
    with pytest.raises(OrderNotPayableError):
        svc_pay.add_payment(order.id, "100")


def test_receipt_contains_everything(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    pay = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])
    pay.add_payment(order.id, "500")
    pay.add_payment(order.id, "1600")

    billing = BillingService(
        order_repo=stores["orders"],
        invoice_repo=stores["invoices"],
        payment_service=pay,
    )
    receipt = billing.build_receipt(order.id)

    assert receipt["order_id"] == order.id
    assert len(receipt["items"]) == 2
    assert receipt["items"][0]["name"] == "Biryani"
    assert receipt["items"][0]["qty"] == 2
    assert receipt["items"][0]["subtotal"] == "900.00"
    assert receipt["total"] == "1950.00"
    assert receipt["total_paid"] == "2100.00"
    assert receipt["balance"] == "0.00"
    assert receipt["change"] == "150.00"
    assert receipt["is_fully_paid"] is True
    assert len(receipt["payments"]) == 2


def test_receipt_before_full_payment(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    pay = PaymentService(payment_repo=stores["payments"],
                         order_repo=stores["orders"])
    pay.add_payment(order.id, "500")

    billing = BillingService(order_repo=stores["orders"],
                             invoice_repo=stores["invoices"],
                             payment_service=pay)
    receipt = billing.build_receipt(order.id)
    assert receipt["balance"] == "1450.00"
    assert receipt["is_fully_paid"] is False


def test_generate_invoice_applies_tax(stores, menu_with_items):
    order = _make_order(stores, menu_with_items)
    billing = BillingService(order_repo=stores["orders"],
                             invoice_repo=stores["invoices"])
    inv = billing.generate_invoice(order.id, "INV-001")
    assert inv.subtotal == Decimal("1950.00")
    assert inv.tax == Decimal("312.00")
    assert inv.total == Decimal("2262.00")


def test_register_and_login(stores):
    svc = AuthService(user_repo=stores["users"])
    svc.register("alice", "a@x.com", "s3cret", role=UserRole.CASHIER)
    user = svc.login("alice", "s3cret")
    assert user.username == "alice"
    assert user.role == UserRole.CASHIER


def test_login_rejects_bad_password(stores):
    svc = AuthService(user_repo=stores["users"])
    svc.register("alice", "a@x.com", "s3cret")
    with pytest.raises(AuthenticationError):
        svc.login("alice", "wrong")


def test_password_hashing_roundtrip():
    h = AuthService.hash_password("hello123")
    assert AuthService.verify_password("hello123", h) is True
    assert AuthService.verify_password("wrong", h) is False