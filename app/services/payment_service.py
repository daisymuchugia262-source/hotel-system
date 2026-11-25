from __future__ import annotations
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
