"""
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
