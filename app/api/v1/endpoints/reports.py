"""Reports endpoints."""
from flask import Blueprint, jsonify
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository

reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/summary")
def summary():
    orders = OrderRepository().list_all()
    payments = PaymentRepository().list_all()
    return jsonify({
        "orders_count": len(orders),
        "payments_count": len(payments),
        "revenue": str(sum(p.amount for p in payments)),
    })
