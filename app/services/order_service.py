from __future__ import annotations
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
