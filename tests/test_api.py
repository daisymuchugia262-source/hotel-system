"""
Phase 4 tests — HTTP API integration.
Run:  python -m pytest tests/test_api.py -v
"""
from decimal import Decimal
import pytest

from app.main import create_app
from app.database.session import JsonStore
from app.repositories.menu_repository      import MenuRepository
from app.repositories.order_repository     import OrderRepository
from app.repositories.payment_repository   import PaymentRepository
from app.repositories.invoice_repository   import InvoiceRepository
from app.repositories.user_repository      import UserRepository
from app.services.menu_service             import MenuService
from app.services.order_service            import OrderService
from app.services.payment_service          import PaymentService
from app.services.billing_service          import BillingService
from app.services.auth_service             import AuthService
from app.models.menu import MenuItem


@pytest.fixture
def app(tmp_path):
    """
    Create a Flask app whose services all point to an isolated tmp_path
    store. We override the services directly via a monkeypatch on the
    endpoint modules — cleanest approach.
    """
    store = JsonStore(data_dir=tmp_path)

    menu_repo    = MenuRepository(store=store)
    order_repo   = OrderRepository(store=store)
    payment_repo = PaymentRepository(store=store)
    invoice_repo = InvoiceRepository(store=store)
    user_repo    = UserRepository(store=store)

    payment_svc = PaymentService(payment_repo=payment_repo, order_repo=order_repo)
    order_svc   = OrderService(order_repo=order_repo, menu_repo=menu_repo)
    menu_svc    = MenuService(repo=menu_repo)
    billing_svc = BillingService(order_repo=order_repo,
                                 invoice_repo=invoice_repo,
                                 payment_service=payment_svc)
    auth_svc    = AuthService(user_repo=user_repo)

    # Replace the service classes called inside the endpoint modules
    import app.api.v1.endpoints.menu     as ep_menu
    import app.api.v1.endpoints.orders   as ep_orders
    import app.api.v1.endpoints.payments as ep_payments
    import app.api.v1.endpoints.billing  as ep_billing
    import app.api.v1.endpoints.auth     as ep_auth

    ep_menu.MenuService       = lambda *a, **k: menu_svc
    ep_orders.OrderService    = lambda *a, **k: order_svc
    ep_payments.PaymentService = lambda *a, **k: payment_svc
    ep_billing.BillingService = lambda *a, **k: billing_svc
    ep_auth.AuthService       = lambda *a, **k: auth_svc

    flask_app = create_app()
    flask_app.testing = True

    # hand the repos to the tests via app.config
    flask_app.config["_menu_repo"]    = menu_repo
    flask_app.config["_order_repo"]   = order_repo
    flask_app.config["_payment_repo"] = payment_repo
    flask_app.config["_user_repo"]    = user_repo
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


# =====================================================================
def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_menu_endpoints(app, client):
    # seed directly through the repo the app is wired to
    repo = app.config["_menu_repo"]
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


def test_full_billing_flow(app, client):
    """Menu → order → 2 payments → receipt with change."""
    repo = app.config["_menu_repo"]
    a = repo.create(MenuItem(name="Biryani", price="450"))
    b = repo.create(MenuItem(name="Burger",  price="350"))

    # Create order: 2 biryani (900) + 3 burgers (1050) = 1950
    r = client.post("/api/v1/orders", json={"items": [
        {"menu_item_id": a.id, "quantity": 2},
        {"menu_item_id": b.id, "quantity": 3},
    ]})
    assert r.status_code == 201, r.get_json()
    order_id = r.get_json()["id"]
    assert r.get_json()["total"] == "1950.00"

    # Pay 500 → balance 1450
    r = client.post("/api/v1/payments", json={"order_id": order_id, "amount": "500"})
    assert r.status_code == 201
    assert r.get_json()["balance"] == "1450.00"
    assert r.get_json()["is_fully_paid"] is False

    # Pay 1600 → overpaid by 150
    r = client.post("/api/v1/payments", json={"order_id": order_id, "amount": "1600"})
    body = r.get_json()
    assert body["balance"] == "0.00"
    assert body["change"] == "150.00"
    assert body["is_fully_paid"] is True

    # Receipt
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


def test_create_order_empty(app, client):
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