"""Inventory endpoints."""
from flask import Blueprint, jsonify
from app.repositories.inventory_repository import InventoryRepository

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.get("")
@inventory_bp.get("/")
def list_inventory():
    return jsonify([i.to_dict() for i in InventoryRepository().list_all()])

@inventory_bp.get("/low-stock")
def low_stock():
    return jsonify([i.to_dict() for i in InventoryRepository().find_low_stock()])
