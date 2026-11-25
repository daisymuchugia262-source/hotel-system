"""Table endpoints."""
from flask import Blueprint, jsonify
from app.repositories.table_repository import TableRepository

tables_bp = Blueprint("tables", __name__)

@tables_bp.get("")
@tables_bp.get("/")
def list_tables():
    return jsonify([t.to_dict() for t in TableRepository().list_all()])
