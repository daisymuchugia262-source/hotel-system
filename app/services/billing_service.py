from __future__ import annotations
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
