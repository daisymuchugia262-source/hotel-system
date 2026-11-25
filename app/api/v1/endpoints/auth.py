"""Auth endpoints — stub for Phase 4; full JWT in Phase 8."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.core.constants import UserRole
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")
    role = body.get("role", "waiter")

    if not (username and email and password):
        return jsonify({"error": "username, email, password are required"}), 400

    try:
        role_enum = UserRole(role)
    except ValueError:
        return jsonify({"error": f"Invalid role: {role}"}), 400

    user = AuthService().register(username, email, password, role=role_enum)
    return jsonify({"id": user.id, "username": user.username,
                    "email": user.email, "role": user.role.value}), 201


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    password = body.get("password")

    if not (username and password):
        return jsonify({"error": "username and password are required"}), 400

    user = AuthService().login(username, password)
    return jsonify({"id": user.id, "username": user.username,
                    "email": user.email, "role": user.role.value})
