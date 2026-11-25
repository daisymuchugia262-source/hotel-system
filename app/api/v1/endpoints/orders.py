"""Order endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.order_service import OrderService

orders_bp = Blueprint("orders", __name__)


@orders_bp.post("")
@orders_bp.post("/")
def create_order():
    body = request.get_json(silent=True) or {}
    items = body.get("items") or []
    customer_id = body.get("customer_id")
    table_id = body.get("table_id")

    svc = OrderService()
    order = svc.create_order(items, customer_id=customer_id, table_id=table_id)
    return jsonify(order.to_dict()), 201


@orders_bp.get("")
@orders_bp.get("/")
def list_orders():
    svc = OrderService()
    return jsonify([o.to_dict() for o in svc.list_orders()])


@orders_bp.get("/<int:order_id>")
def get_order(order_id: int):
    svc = OrderService()
    return jsonify(svc.get_order(order_id).to_dict())
