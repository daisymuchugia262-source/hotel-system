"""Menu endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.menu_service import MenuService

menu_bp = Blueprint("menu", __name__)


@menu_bp.get("")
@menu_bp.get("/")
def list_menu():
    category = request.args.get("category")
    only_available = request.args.get("available") == "true"

    svc = MenuService()
    if category:
        items = svc.list_by_category(category)
    elif only_available:
        items = svc.list_available()
    else:
        items = svc.list_menu()

    return jsonify([i.to_dict() for i in items])


@menu_bp.get("/<int:item_id>")
def get_menu_item(item_id: int):
    svc = MenuService()
    return jsonify(svc.get_item(item_id).to_dict())
