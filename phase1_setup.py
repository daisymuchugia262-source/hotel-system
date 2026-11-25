"""
phase1_setup.py — Completes Phase 1 of the hotel billing system:
  - Creates app/core/constants.py
  - Fills app/core/exceptions.py
  - Fills app/models/__init__.py
  - Fills all 14 model files
  - Fills tests/__init__.py
  - Creates tests/test_models.py
  - Ensures every package folder has __init__.py

Run from: C:\\dev\\hotel-billing\\backend
    python phase1_setup.py

Idempotent — safe to run multiple times.
"""

from pathlib import Path


def write(path: Path, content: str) -> None:
    """Write content to file, creating parent dirs. Overwrites if exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote  {path}")


def touch(path: Path) -> None:
    """Create empty file if it doesn't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()
        print(f"  created {path}")


# ---------------------------------------------------------------------------
# __init__.py for every package folder
# ---------------------------------------------------------------------------
INIT_DIRS = [
    "app",
    "app/core",
    "app/database",
    "app/models",
    "app/schemas",
    "app/api",
    "app/api/v1",
    "app/api/v1/endpoints",
    "app/services",
    "app/repositories",
    "app/websocket",
    "app/utils",
    "app/tasks",
    "tests",
]


# ---------------------------------------------------------------------------
# File contents
# ---------------------------------------------------------------------------
CONSTANTS_PY = '''"""
Shared enums and constants used across the domain.
No imports from models, services, or repositories.
"""
from enum import Enum


class Currency(str, Enum):
    KES = "KES"
    USD = "USD"
    EUR = "EUR"


class OrderStatus(str, Enum):
    PENDING   = "pending"
    PREPARING = "preparing"
    READY     = "ready"
    SERVED    = "served"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CASH  = "cash"
    CARD  = "card"
    MPESA = "mpesa"
    BANK  = "bank"


class PaymentStatus(str, Enum):
    PENDING   = "pending"
    COMPLETED = "completed"
    REFUNDED  = "refunded"


class InvoiceStatus(str, Enum):
    DRAFT  = "draft"
    ISSUED = "issued"
    PAID   = "paid"
    VOID   = "void"


class UserRole(str, Enum):
    ADMIN        = "admin"
    MANAGER      = "manager"
    CASHIER      = "cashier"
    WAITER       = "waiter"
    CHEF         = "chef"
    HOUSEKEEPING = "housekeeping"


class RoomStatus(str, Enum):
    AVAILABLE   = "available"
    OCCUPIED    = "occupied"
    CLEANING    = "cleaning"
    MAINTENANCE = "maintenance"


class TableStatus(str, Enum):
    FREE     = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class EmployeeStatus(str, Enum):
    ACTIVE   = "active"
    ON_LEAVE = "on_leave"
    FIRED    = "fired"


DEFAULT_CURRENCY = Currency.KES
DEFAULT_TAX_RATE = "0.16"     # 16% VAT
MONEY_PLACES     = "0.01"
'''


EXCEPTIONS_PY = '''"""
Domain-specific exceptions.
Used by services to signal business-rule failures.
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class ValidationError(DomainError):
    """Input data fails a business rule."""


class NotFoundError(DomainError):
    """Entity not found."""


class DuplicateError(DomainError):
    """Entity already exists."""


class PaymentError(DomainError):
    """Invalid payment operation."""


class InsufficientPaymentError(PaymentError):
    """Amount paid doesn't clear the balance yet."""


class OverpaymentError(PaymentError):
    """Payment exceeds balance and change isn't allowed."""


class OrderNotPayableError(DomainError):
    """Order can't accept payments (cancelled, etc.)."""


class AuthenticationError(DomainError):
    """Bad credentials."""


class PermissionDeniedError(DomainError):
    """User not allowed to do this."""
'''


MODELS_INIT_PY = '''"""
Domain models — pure data objects.
No imports from services/, repositories/, or api/.
"""
from app.models.user       import User
from app.models.customer   import Customer
from app.models.employee   import Employee
from app.models.menu       import MenuItem
from app.models.order      import Order
from app.models.order_item import OrderItem
from app.models.payment    import Payment
from app.models.invoice    import Invoice
from app.models.table      import RestaurantTable
from app.models.room       import Room
from app.models.inventory  import InventoryItem
from app.models.supplier   import Supplier
from app.models.complaint  import Complaint
from app.models.audit_log  import AuditLog

__all__ = [
    "User", "Customer", "Employee", "MenuItem",
    "Order", "OrderItem", "Payment", "Invoice",
    "RestaurantTable", "Room", "InventoryItem",
    "Supplier", "Complaint", "AuditLog",
]
'''


MODEL_USER_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from app.core.constants import UserRole


@dataclass
class User:
    """A system user (staff member who can log in)."""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.WAITER
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        if self.username and len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email address")
        if isinstance(self.role, str):
            self.role = UserRole(self.role)

    def to_dict(self, include_hash: bool = False) -> dict:
        data = asdict(self)
        data["role"] = self.role.value
        if not include_hash:
            data.pop("password_hash", None)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        data = data.copy()
        if isinstance(data.get("role"), str):
            data["role"] = UserRole(data["role"])
        return cls(**data)
'''


MODEL_CUSTOMER_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """A hotel guest or restaurant customer."""
    id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    email: str = ""
    id_number: str = ""
    address: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        if not self.full_name.strip():
            raise ValueError("Customer must have a full name")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        return cls(**data)
'''


MODEL_EMPLOYEE_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.core.constants import EmployeeStatus, UserRole


@dataclass
class Employee:
    """A staff member (may or may not have a login User account)."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    full_name: str = ""
    position: UserRole = UserRole.WAITER
    phone: str = ""
    salary: Decimal = Decimal("0.00")
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hired_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.salary = Decimal(str(self.salary))
        if isinstance(self.position, str):
            self.position = UserRole(self.position)
        if isinstance(self.status, str):
            self.status = EmployeeStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["salary"] = str(self.salary)
        data["position"] = self.position.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        data = data.copy()
        data["salary"] = Decimal(str(data["salary"]))
        if isinstance(data.get("position"), str):
            data["position"] = UserRole(data["position"])
        if isinstance(data.get("status"), str):
            data["status"] = EmployeeStatus(data["status"])
        return cls(**data)
'''


MODEL_MENU_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class MenuItem:
    """An item on the menu (food, drink, etc.)."""
    id: Optional[int] = None
    name: str = ""
    category: str = "general"
    price: Decimal = Decimal("0.00")
    is_available: bool = True
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Menu item must have a name")
        self.price = Decimal(str(self.price))
        if self.price < 0:
            raise ValueError("Price cannot be negative")

    def to_dict(self) -> dict:
        data = asdict(self)
        data["price"] = str(self.price)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MenuItem":
        data = data.copy()
        data["price"] = Decimal(str(data["price"]))
        return cls(**data)
'''


MODEL_ORDER_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.core.constants import OrderStatus


@dataclass
class Order:
    """A customer order — one bill, made up of many OrderItem objects."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    table_id: Optional[int] = None
    status: OrderStatus = OrderStatus.PENDING
    items: List["OrderItem"] = field(default_factory=list)
    total: Decimal = Decimal("0.00")
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.total = Decimal(str(self.total))
        if isinstance(self.status, str):
            self.status = OrderStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["total"] = str(self.total)
        data["items"] = [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in self.items
        ]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        data = data.copy()
        data.pop("items", None)
        data["total"] = Decimal(str(data["total"]))
        if isinstance(data.get("status"), str):
            data["status"] = OrderStatus(data["status"])
        return cls(**data)
'''


MODEL_ORDER_ITEM_PY = '''from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional


@dataclass
class OrderItem:
    """One line in an order: a menu item + quantity + computed subtotal."""
    id: Optional[int] = None
    order_id: Optional[int] = None
    menu_item_id: Optional[int] = None
    item_name: str = ""
    unit_price: Decimal = Decimal("0.00")
    quantity: int = 1
    subtotal: Decimal = Decimal("0.00")

    def __post_init__(self) -> None:
        self.unit_price = Decimal(str(self.unit_price))
        self.subtotal = Decimal(str(self.subtotal))
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")

    def compute_subtotal(self) -> Decimal:
        self.subtotal = (self.unit_price * self.quantity).quantize(Decimal("0.01"))
        return self.subtotal

    def to_dict(self) -> dict:
        data = asdict(self)
        data["unit_price"] = str(self.unit_price)
        data["subtotal"] = str(self.subtotal)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        data = data.copy()
        data["unit_price"] = Decimal(str(data["unit_price"]))
        data["subtotal"] = Decimal(str(data["subtotal"]))
        return cls(**data)
'''


MODEL_PAYMENT_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.core.constants import PaymentMethod, PaymentStatus


@dataclass
class Payment:
    """A single payment attempt against an order. May be partial."""
    id: Optional[int] = None
    order_id: Optional[int] = None
    amount: Decimal = Decimal("0.00")
    method: PaymentMethod = PaymentMethod.CASH
    status: PaymentStatus = PaymentStatus.COMPLETED
    reference: str = ""
    paid_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.amount = Decimal(str(self.amount))
        if self.amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if isinstance(self.method, str):
            self.method = PaymentMethod(self.method)
        if isinstance(self.status, str):
            self.status = PaymentStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["amount"] = str(self.amount)
        data["method"] = self.method.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        data = data.copy()
        data["amount"] = Decimal(str(data["amount"]))
        if isinstance(data.get("method"), str):
            data["method"] = PaymentMethod(data["method"])
        if isinstance(data.get("status"), str):
            data["status"] = PaymentStatus(data["status"])
        return cls(**data)
'''


MODEL_INVOICE_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.core.constants import InvoiceStatus


@dataclass
class Invoice:
    """A formal invoice generated from an order."""
    id: Optional[int] = None
    order_id: Optional[int] = None
    invoice_number: str = ""
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issued_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        for f in ("subtotal", "tax", "total"):
            setattr(self, f, Decimal(str(getattr(self, f))))
        if isinstance(self.status, str):
            self.status = InvoiceStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["subtotal"] = str(self.subtotal)
        data["tax"] = str(self.tax)
        data["total"] = str(self.total)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Invoice":
        data = data.copy()
        for f in ("subtotal", "tax", "total"):
            data[f] = Decimal(str(data[f]))
        if isinstance(data.get("status"), str):
            data["status"] = InvoiceStatus(data["status"])
        return cls(**data)
'''


MODEL_TABLE_PY = '''from dataclasses import dataclass, asdict
from typing import Optional
from app.core.constants import TableStatus


@dataclass
class RestaurantTable:
    """A physical dining table."""
    id: Optional[int] = None
    table_number: str = ""
    seats: int = 4
    status: TableStatus = TableStatus.FREE
    location: str = ""

    def __post_init__(self) -> None:
        if not self.table_number:
            raise ValueError("Table must have a number")
        if self.seats <= 0:
            raise ValueError("Table must have at least 1 seat")
        if isinstance(self.status, str):
            self.status = TableStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "RestaurantTable":
        data = data.copy()
        if isinstance(data.get("status"), str):
            data["status"] = TableStatus(data["status"])
        return cls(**data)
'''


MODEL_ROOM_PY = '''from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional
from app.core.constants import RoomStatus


@dataclass
class Room:
    """A hotel room."""
    id: Optional[int] = None
    room_number: str = ""
    room_type: str = "standard"
    price_per_night: Decimal = Decimal("0.00")
    capacity: int = 2
    status: RoomStatus = RoomStatus.AVAILABLE

    def __post_init__(self) -> None:
        if not self.room_number:
            raise ValueError("Room must have a number")
        self.price_per_night = Decimal(str(self.price_per_night))
        if self.price_per_night < 0:
            raise ValueError("Price cannot be negative")
        if isinstance(self.status, str):
            self.status = RoomStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["price_per_night"] = str(self.price_per_night)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Room":
        data = data.copy()
        data["price_per_night"] = Decimal(str(data["price_per_night"]))
        if isinstance(data.get("status"), str):
            data["status"] = RoomStatus(data["status"])
        return cls(**data)
'''


MODEL_INVENTORY_PY = '''from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional


@dataclass
class InventoryItem:
    """A stock item tracked by the hotel."""
    id: Optional[int] = None
    name: str = ""
    unit: str = "pcs"
    quantity_in_stock: Decimal = Decimal("0.00")
    reorder_level: Decimal = Decimal("0.00")
    unit_cost: Decimal = Decimal("0.00")
    supplier_id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Inventory item must have a name")
        for f in ("quantity_in_stock", "reorder_level", "unit_cost"):
            setattr(self, f, Decimal(str(getattr(self, f))))

    def to_dict(self) -> dict:
        data = asdict(self)
        for f in ("quantity_in_stock", "reorder_level", "unit_cost"):
            data[f] = str(data[f])
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryItem":
        data = data.copy()
        for f in ("quantity_in_stock", "reorder_level", "unit_cost"):
            data[f] = Decimal(str(data[f]))
        return cls(**data)
'''


MODEL_SUPPLIER_PY = '''from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Supplier:
    """A vendor who supplies inventory."""
    id: Optional[int] = None
    name: str = ""
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Supplier must have a name")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Supplier":
        return cls(**data)
'''


MODEL_COMPLAINT_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Complaint:
    """A customer complaint logged for follow-up."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    subject: str = ""
    details: str = ""
    is_resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("Complaint must have a subject")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Complaint":
        return cls(**data)
'''


MODEL_AUDIT_LOG_PY = '''from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class AuditLog:
    """Record of an important action (for traceability)."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: str = ""
    entity: str = ""
    entity_id: Optional[int] = None
    details: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLog":
        return cls(**data)
'''


TEST_MODELS_PY = '''"""
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
'''


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build() -> None:
    root = Path.cwd()

    if not (root / "app").exists():
        print(f"ERROR: no 'app' folder in {root}")
        print("       Run this script from C:\\dev\\hotel-billing\\backend")
        return

    print(f"\nPhase 1 setup in: {root}\n")

    # 1. __init__.py everywhere
    print("[1/4] Ensuring __init__.py in every package...")
    for d in INIT_DIRS:
        path = root / d
        if path.exists() and path.is_dir():
            touch(path / "__init__.py")

    # 2. Constants + exceptions
    print("\n[2/4] Core enums and exceptions...")
    write(root / "app" / "core" / "constants.py", CONSTANTS_PY)
    write(root / "app" / "core" / "exceptions.py", EXCEPTIONS_PY)

    # 3. All models
    print("\n[3/4] Domain models (14 files)...")
    write(root / "app" / "models" / "__init__.py",     MODELS_INIT_PY)
    write(root / "app" / "models" / "user.py",         MODEL_USER_PY)
    write(root / "app" / "models" / "customer.py",     MODEL_CUSTOMER_PY)
    write(root / "app" / "models" / "employee.py",     MODEL_EMPLOYEE_PY)
    write(root / "app" / "models" / "menu.py",         MODEL_MENU_PY)
    write(root / "app" / "models" / "order.py",        MODEL_ORDER_PY)
    write(root / "app" / "models" / "order_item.py",   MODEL_ORDER_ITEM_PY)
    write(root / "app" / "models" / "payment.py",      MODEL_PAYMENT_PY)
    write(root / "app" / "models" / "invoice.py",      MODEL_INVOICE_PY)
    write(root / "app" / "models" / "table.py",        MODEL_TABLE_PY)
    write(root / "app" / "models" / "room.py",         MODEL_ROOM_PY)
    write(root / "app" / "models" / "inventory.py",    MODEL_INVENTORY_PY)
    write(root / "app" / "models" / "supplier.py",     MODEL_SUPPLIER_PY)
    write(root / "app" / "models" / "complaint.py",    MODEL_COMPLAINT_PY)
    write(root / "app" / "models" / "audit_log.py",    MODEL_AUDIT_LOG_PY)

    # 4. Tests
    print("\n[4/4] Tests...")
    write(root / "tests" / "__init__.py",     "")
    write(root / "tests" / "test_models.py",  TEST_MODELS_PY)

    print("\nPhase 1 setup complete.")
    print("\nNext steps:")
    print("  1) python -c \"from app.models import Order, Payment; print('OK')\"")
    print("  2) pip install pytest   (if not installed)")
    print("  3) pytest tests/test_models.py -v")
    print("  4) Expect: 9 passed\n")


if __name__ == "__main__":
    build()