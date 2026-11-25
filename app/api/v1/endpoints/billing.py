"""Billing / receipt / invoice endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.billing_service import BillingService

billing_bp = Blueprint("billing", __name__)


@billing_bp.get("/receipt/<int:order_id>")
def get_receipt(order_id: int):
    return jsonify(BillingService().build_receipt(order_id))


@billing_bp.post("/invoice/<int:order_id>")
def create_invoice(order_id: int):
    body = request.get_json(silent=True) or {}
    number = body.get("invoice_number")
    if not number:
        return jsonify({"error": "invoice_number is required"}), 400
    inv = BillingService().generate_invoice(order_id, number)
    return jsonify(inv.to_dict()), 201
