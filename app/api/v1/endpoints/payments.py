"""Payment endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.constants import PaymentMethod
from app.services.payment_service import PaymentService

payments_bp = Blueprint("payments", __name__)


@payments_bp.post("")
@payments_bp.post("/")
def add_payment():
    body = request.get_json(silent=True) or {}
    order_id = body.get("order_id")
    amount = body.get("amount")
    method = body.get("method", "cash")
    reference = body.get("reference", "")

    if order_id is None or amount is None:
        return jsonify({"error": "order_id and amount are required"}), 400

    try:
        pm = PaymentMethod(method)
    except ValueError:
        return jsonify({"error": f"Invalid payment method: {method}"}), 400

    svc = PaymentService()
    payment = svc.add_payment(order_id, amount, method=pm, reference=reference)

    return jsonify({
        "payment": payment.to_dict(),
        "balance": str(svc.balance(order_id)),
        "change": str(svc.change(order_id)),
        "is_fully_paid": svc.is_fully_paid(order_id),
    }), 201


@payments_bp.get("/order/<int:order_id>")
def list_for_order(order_id: int):
    svc = PaymentService()
    return jsonify([p.to_dict() for p in svc.list_payments(order_id)])
