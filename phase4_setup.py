"""
phase4_setup.py — Completes Phase 4 (HTTP API / Routes).

Creates and fills:
  - app/main.py                       (app factory with CORS + blueprints)
  - app/api/__init__.py
  - app/api/v1/__init__.py
  - app/api/v1/router.py              (blueprint aggregator)
  - app/api/v1/endpoints/__init__.py
  - app/api/v1/endpoints/menu.py
  - app/api/v1/endpoints/orders.py
  - app/api/v1/endpoints/payments.py
  - app/api/v1/endpoints/billing.py
  - app/api/v1/endpoints/auth.py
  - run.py                            (entry point)
  - tests/test_api.py

Run from: C:\\Users\\user\\OneDrive\\Desktop\\scaffold.sh\\backend
    python phase4_setup.py
"""

from pathlib import Path


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote  {path}")


# ===========================================================================
# FILE CONTENTS
# ===========================================================================

MAIN_PY = r'''"""
App factory — creates the Flask application.
No business logic here — just wiring.
"""
from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS

from app.api.v1.router import register_blueprints
from app.core.exceptions import (
    DomainError, NotFoundError, ValidationError,
    AuthenticationError, PaymentError, OrderNotPayableError,
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    CORS(app)

    register_blueprints(app)
    _register_error_handlers(app)

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok", "service": "hotel-billing"}

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(NotFoundError)
    def _not_found(e):
        return jsonify({"error": str(e), "type": "not_found"}), 404

    @app.errorhandler(ValidationError)
    def _validation(e):
        return jsonify({"error": str(e), "type": "validation"}), 400

    @app.errorhandler(AuthenticationError)
    def _auth(e):
        return jsonify({"error": str(e), "type": "auth"}), 401

    @app.errorhandler(OrderNotPayableError)
    def _not_payable(e):
        return jsonify({"error": str(e), "type": "order_not_payable"}), 409

    @app.errorhandler(PaymentError)
    def _payment(e):
        return jsonify({"error": str(e), "type": "payment"}), 400

    @app.errorhandler(DomainError)
    def _domain(e):
        return jsonify({"error": str(e), "type": "domain"}), 400

    @app.errorhandler(404)
    def _404(e):
        return jsonify({"error": "Endpoint not found", "type": "not_found"}), 404

    @app.errorhandler(500)
    def _500(e):
        return jsonify({"error": "Internal server error", "type": "server_error"}), 500
'''


API_INIT_PY = r'''"""HTTP API layer."""
'''


V1_INIT_PY = r'''"""API v1."""
'''


ENDPOINTS_INIT_PY = r'''"""API v1 endpoints."""
'''


ROUTER_PY = r'''"""Registers all API blueprints under /api/v1."""
from __future__ import annotations

from flask import Flask

from app.api.v1.endpoints.menu     import menu_bp
from app.api.v1.endpoints.orders   import orders_bp
from app.api.v1.endpoints.payments import payments_bp
from app.api.v1.endpoints.billing  import billing_bp
from app.api.v1.endpoints.auth     import auth_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp,     url_prefix="/api/v1/auth")
    app.register_blueprint(menu_bp,     url_prefix="/api/v1/menu")
    app.register_blueprint(orders_bp,   url_prefix="/api/v1/orders")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments")
    app.register_blueprint(billing_bp,  url_prefix="/api/v1/billing")
'''


MENU_ENDPOINTS_PY = r'''"""Menu endpoints."""
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
'''


ORDERS_ENDPOINTS_PY = r'''"""Order endpoints."""
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
'''


PAYMENTS_ENDPOINTS_PY = r'''"""Payment endpoints."""
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
'''


BILLING_ENDPOINTS_PY = r'''"""Billing / receipt / invoice endpoints."""
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
'''


AUTH_ENDPOINTS_PY = r'''"""Auth endpoints — stub for Phase 4; full JWT in Phase 8."""
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
'''


RUN_PY = r'''"""Entry point — starts the Flask server."""
from app.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''


TEST_API_PY = r'''"""
Phase 4 tests — HTTP API integration.
Run:  python -m pytest tests/test_api.py -v
"""
from decimal import Decimal
import pytest

from app.main import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Isolated Flask client with a temp data directory."""
    from app.database import session
    from app.repositories import menu_repository, order_repository, payment_repository

    store = session.JsonStore(data_dir=tmp_path)
    monkeypatch.setattr(session, "JsonStore", lambda *a, **k: store)
    for mod in (menu_repository, order_repository, payment_repository):
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type) and hasattr(obj, "__init__"):
                try:
                    orig = obj.__init__
                    def patched(self, store=store, _orig=orig):
                        _orig(self, store=store)
                    obj.__init__ = patched
                except Exception:
                    pass

    app = create_app()
    app.testing = True
    return app.test_client()


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_menu_endpoints(client):
    # create three items via direct repository
    from app.repositories.menu_repository import MenuRepository
    from app.models.menu import MenuItem
    repo = MenuRepository()
    repo.create(MenuItem(name="Biryani", price="450", category="food"))
    repo.create(MenuItem(name="Soda",    price="100", category="drink"))

    r = client.get("/api/v1/menu")
    assert r.status_code == 200
    items = r.get_json()
    assert len(items) == 2
    assert items[0]["name"] == "Biryani"

    r = client.get("/api/v1/menu?category=drink")
    assert len(r.get_json()) == 1

    item_id = items[0]["id"]
    r = client.get(f"/api/v1/menu/{item_id}")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Biryani"


def test_menu_404(client):
    r = client.get("/api/v1/menu/999")
    assert r.status_code == 404
    assert r.get_json()["type"] == "not_found"


def test_full_billing_flow(client):
    """Menu → order → 2 payments → receipt with change."""
    from app.repositories.menu_repository import MenuRepository
    from app.models.menu import MenuItem
    repo = MenuRepository()
    a = repo.create(MenuItem(name="Biryani", price="450"))
    b = repo.create(MenuItem(name="Burger",  price="350"))

    # 2. Create order: 2 biryani + 3 burgers = 1950
    r = client.post("/api/v1/orders", json={"items": [
        {"menu_item_id": a.id, "quantity": 2},
        {"menu_item_id": b.id, "quantity": 3},
    ]})
    assert r.status_code == 201, r.get_json()
    order = r.get_json()
    order_id = order["id"]
    assert order["total"] == "1950.00"

    # 3. Pay 500 → balance 1450
    r = client.post("/api/v1/payments", json={"order_id": order_id, "amount": "500"})
    assert r.status_code == 201
    body = r.get_json()
    assert body["balance"] == "1450.00"
    assert body["is_fully_paid"] is False

    # 4. Pay 1600 → change 150
    r = client.post("/api/v1/payments", json={"order_id": order_id, "amount": "1600"})
    body = r.get_json()
    assert body["balance"] == "0.00"
    assert body["change"] == "150.00"
    assert body["is_fully_paid"] is True

    # 5. Receipt
    r = client.get(f"/api/v1/billing/receipt/{order_id}")
    assert r.status_code == 200
    receipt = r.get_json()
    assert receipt["total"] == "1950.00"
    assert receipt["total_paid"] == "2100.00"
    assert receipt["change"] == "150.00"
    assert len(receipt["items"]) == 2
    assert len(receipt["payments"]) == 2


def test_payment_requires_fields(client):
    r = client.post("/api/v1/payments", json={"amount": "100"})
    assert r.status_code == 400
    r = client.post("/api/v1/payments", json={"order_id": 1})
    assert r.status_code == 400


def test_create_order_empty(client):
    r = client.post("/api/v1/orders", json={"items": []})
    assert r.status_code == 400
    assert r.get_json()["type"] == "validation"


def test_auth_register_and_login(client):
    r = client.post("/api/v1/auth/register", json={
        "username": "alice", "email": "a@x.com", "password": "s3cret"
    })
    assert r.status_code == 201, r.get_json()
    assert r.get_json()["username"] == "alice"

    r = client.post("/api/v1/auth/login", json={
        "username": "alice", "password": "s3cret"
    })
    assert r.status_code == 200
    assert r.get_json()["role"] == "waiter"

    r = client.post("/api/v1/auth/login", json={
        "username": "alice", "password": "wrong"
    })
    assert r.status_code == 401
'''


# ===========================================================================
# BUILD
# ===========================================================================
def build() -> None:
    root = Path.cwd()

    if not (root / "app").exists():
        print(f"ERROR: no 'app' folder in {root}")
        print("       Run from C:\\Users\\user\\OneDrive\\Desktop\\scaffold.sh\\backend")
        return

    print(f"\nPhase 4 setup in: {root}\n")

    print("[1/4] App factory and entry point...")
    write(root / "app" / "main.py", MAIN_PY)
    write(root / "run.py", RUN_PY)

    print("\n[2/4] API layer (__init__ files, router)...")
    write(root / "app" / "api" / "__init__.py", API_INIT_PY)
    write(root / "app" / "api" / "v1" / "__init__.py", V1_INIT_PY)
    write(root / "app" / "api" / "v1" / "endpoints" / "__init__.py", ENDPOINTS_INIT_PY)
    write(root / "app" / "api" / "v1" / "router.py", ROUTER_PY)

    print("\n[3/4] Endpoints (5 files)...")
    ep = root / "app" / "api" / "v1" / "endpoints"
    write(ep / "menu.py",     MENU_ENDPOINTS_PY)
    write(ep / "orders.py",   ORDERS_ENDPOINTS_PY)
    write(ep / "payments.py", PAYMENTS_ENDPOINTS_PY)
    write(ep / "billing.py",  BILLING_ENDPOINTS_PY)
    write(ep / "auth.py",     AUTH_ENDPOINTS_PY)

    print("\n[4/4] Tests...")
    write(root / "tests" / "test_api.py", TEST_API_PY)

    print("\nPhase 4 setup complete.")
    print("\nNext steps:")
    print("  1) pip install flask flask-cors   (if not installed)")
    print("  2) python -m pytest tests\\test_api.py -v")
    print("  3) python run.py")
    print("  4) Open: http://localhost:5000/api/v1/health\n")


if __name__ == "__main__":
    build()