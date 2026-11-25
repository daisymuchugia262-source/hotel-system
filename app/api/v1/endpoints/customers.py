"""Customer endpoints."""
from flask import Blueprint, jsonify, request
from app.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer

customers_bp = Blueprint("customers", __name__)

@customers_bp.get("")
@customers_bp.get("/")
def list_customers():
    return jsonify([c.to_dict() for c in CustomerRepository().list_all()])

@customers_bp.post("")
@customers_bp.post("/")
def create_customer():
    body = request.get_json(silent=True) or {}
    c = CustomerRepository().create(Customer(
        full_name=body.get("full_name", ""),
        phone=body.get("phone", ""),
        email=body.get("email", ""),
    ))
    return jsonify(c.to_dict()), 201
