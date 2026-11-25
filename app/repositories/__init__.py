"""Concrete repositories — one per entity."""
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
