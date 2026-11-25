"""
phase3_setup.py — Completes Phase 3 (Business Logic / Services).
"""
from pathlib import Path

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote  {path}")

MENU_SERVICE_PY = r"""from __future__ import annotations
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
"""

ORDER_SERVICE_PY = r"""from __future__ import annotations
from decimal import Decimal
from typing import List, Optional
from app.core.constants import OrderStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.models.menu import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, order_repo: Optional[OrderRepository] = None,
                 menu_repo: Optional[MenuRepository] = None) -> None:
        self.order_repo = order_repo or OrderRepository()
        self.menu_repo = menu_repo or MenuRepository()

    def create_order(self, raw_items: List[dict], customer_id: Optional[int] = None,
                     table_id: Optional[int] = None) -> Order:
        if not raw_items:
            raise ValidationError("Order must contain at least one item")
        order = Order(customer_id=customer_id, table_id=table_id,
                      status=OrderStatus.PENDING)
        for raw in raw_items:
            menu_item_id = raw.get("menu_item_id")
            quantity = raw.get("quantity")
            if menu_item_id is None or quantity is None:
                raise ValidationError("Each order line needs menu_item_id and quantity")
            menu_item = self._fetch_menu_item(menu_item_id)
            line = OrderItem(menu_item_id=menu_item.id, item_name=menu_item.name,
                             unit_price=menu_item.price, quantity=int(quantity))
            line.compute_subtotal()
            order.items.append(line)
        order.total = sum((i.subtotal for i in order.items), Decimal("0.00"))
        return self.order_repo.create(order)

    def get_order(self, order_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        return order

    def list_orders(self) -> List[Order]:
        return self.order_repo.list_all()

    def set_status(self, order_id: int, status: OrderStatus) -> Order:
        order = self.get_order(order_id)
        order.status = status
        updated = self.order_repo.update(order)
        if updated is None:
            raise NotFoundError(f"Order {order_id} not found")
        return updated

    def _fetch_menu_item(self, menu_item_id: int) -> MenuItem:
        item = self.menu_repo.get_by_id(menu_item_id)
        if item is None:
            raise NotFoundError(f"Menu item {menu_item_id} not found")
        if not item.is_available:
            raise ValidationError(f"Menu item '{item.name}' is not available")
        return item
"""

PAYMENT_SERVICE_PY = r"""from __future__ import annotations
from decimal import Decimal
from typing import List, Optional
from app.core.constants import OrderStatus, PaymentMethod
from app.core.exceptions import NotFoundError, OrderNotPayableError, ValidationError
from app.models.payment import Payment
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, payment_repo: Optional[PaymentRepository] = None,
                 order_repo: Optional[OrderRepository] = None) -> None:
        self.payment_repo = payment_repo or PaymentRepository()
        self.order_repo = order_repo or OrderRepository()

    def add_payment(self, order_id: int, amount, method: PaymentMethod = PaymentMethod.CASH,
                    reference: str = "") -> Payment:
        amt = Decimal(str(amount))
        if amt <= 0:
            raise ValidationError("Payment amount must be greater than zero")
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        if order.status == OrderStatus.CANCELLED:
            raise OrderNotPayableError(f"Order {order_id} is cancelled")
        return self.payment_repo.create(
            Payment(order_id=order_id, amount=amt, method=method, reference=reference))

    def total_paid(self, order_id: int) -> Decimal:
        return self.payment_repo.total_paid_for_order(order_id)

    def balance(self, order_id: int) -> Decimal:
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        remaining = order.total - self.total_paid(order_id)
        return remaining if remaining > 0 else Decimal("0.00")

    def change(self, order_id: int) -> Decimal:
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        over = self.total_paid(order_id) - order.total
        return over if over > 0 else Decimal("0.00")

    def is_fully_paid(self, order_id: int) -> bool:
        return self.balance(order_id) == Decimal("0.00")

    def list_payments(self, order_id: int) -> List[Payment]:
        return self.payment_repo.find_by_order(order_id)
"""

BILLING_SERVICE_PY = r"""from __future__ import annotations
from decimal import Decimal
from typing import Optional
from app.core.constants import DEFAULT_TAX_RATE, InvoiceStatus
from app.core.exceptions import NotFoundError
from app.models.invoice import Invoice
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.order_repository import OrderRepository
from app.services.payment_service import PaymentService


class BillingService:
    def __init__(self, order_repo: Optional[OrderRepository] = None,
                 invoice_repo: Optional[InvoiceRepository] = None,
                 payment_service: Optional[PaymentService] = None) -> None:
        self.order_repo = order_repo or OrderRepository()
        self.invoice_repo = invoice_repo or InvoiceRepository()
        self.payment_service = payment_service or PaymentService()

    def build_receipt(self, order_id: int) -> dict:
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        items = [{"name": i.item_name, "price": str(i.unit_price),
                  "qty": i.quantity, "subtotal": str(i.subtotal)} for i in order.items]
        payments = [{"id": p.id, "amount": str(p.amount), "method": p.method.value,
                     "status": p.status.value} for p in self.payment_service.list_payments(order_id)]
        total_paid = self.payment_service.total_paid(order_id)
        balance = self.payment_service.balance(order_id)
        change = self.payment_service.change(order_id)
        return {"order_id": order.id, "customer_id": order.customer_id,
                "table_id": order.table_id, "status": order.status.value,
                "items": items, "total": str(order.total),
                "payments": payments, "total_paid": str(total_paid),
                "balance": str(balance), "change": str(change),
                "is_fully_paid": balance == Decimal("0.00")}

    def generate_invoice(self, order_id: int, invoice_number: str) -> Invoice:
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        tax_rate = Decimal(DEFAULT_TAX_RATE)
        subtotal = order.total
        tax = (subtotal * tax_rate).quantize(Decimal("0.01"))
        total = subtotal + tax
        existing = self.invoice_repo.find_by_order(order_id)
        if existing:
            return existing
        return self.invoice_repo.create(Invoice(order_id=order_id,
            invoice_number=invoice_number, subtotal=subtotal, tax=tax,
            total=total, status=InvoiceStatus.ISSUED))
"""

AUTH_SERVICE_PY = r"""from __future__ import annotations
import hashlib
import hmac
import os
from typing import Optional
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, DuplicateError
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: Optional[UserRepository] = None) -> None:
        self.user_repo = user_repo or UserRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return f"{salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        try:
            salt_hex, digest_hex = stored.split("$")
        except ValueError:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return hmac.compare_digest(actual, expected)

    def register(self, username: str, email: str, password: str,
                 role: UserRole = UserRole.WAITER) -> User:
        if self.user_repo.find_by_username(username):
            raise DuplicateError(f"Username '{username}' is taken")
        if self.user_repo.find_by_email(email):
            raise DuplicateError(f"Email '{email}' is already registered")
        user = User(username=username, email=email,
                    password_hash=self.hash_password(password), role=role)
        return self.user_repo.create(user)

    def login(self, username: str, password: str) -> User:
        user = self.user_repo.find_by_username(username)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid credentials")
        if not self.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        return user
"""

SERVICES_INIT_PY = r"""from app.services.menu_service    import MenuService
from app.services.order_service   import OrderService
from app.services.payment_service import PaymentService
from app.services.billing_service import BillingService
from app.services.auth_service    import AuthService

__all__ = ["MenuService", "OrderService", "PaymentService",
           "BillingService", "AuthService"]
"""


def build() -> None:
    root = Path.cwd()
    if not (root / "app").exists():
        print(f"ERROR: no 'app' folder in {root}")
        return
    print(f"\nPhase 3 setup in: {root}\n")
    print("[1/3] Services (5 files)...")
    svc = root / "app" / "services"
    write(svc / "menu_service.py",    MENU_SERVICE_PY)
    write(svc / "order_service.py",   ORDER_SERVICE_PY)
    write(svc / "payment_service.py", PAYMENT_SERVICE_PY)
    write(svc / "billing_service.py", BILLING_SERVICE_PY)
    write(svc / "auth_service.py",    AUTH_SERVICE_PY)
    write(svc / "__init__.py",        SERVICES_INIT_PY)
    print("\n[2/3] Tests — copy from the full script message")
    print("[3/3] Done.\n")


if __name__ == "__main__":
    build()
