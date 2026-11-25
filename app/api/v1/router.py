"""Registers all API blueprints under /api/v1."""
from __future__ import annotations

from flask import Flask

from app.api.v1.endpoints.menu      import menu_bp
from app.api.v1.endpoints.orders    import orders_bp
from app.api.v1.endpoints.payments  import payments_bp
from app.api.v1.endpoints.billing   import billing_bp
from app.api.v1.endpoints.auth      import auth_bp
from app.api.v1.endpoints.customers import customers_bp
from app.api.v1.endpoints.tables    import tables_bp
from app.api.v1.endpoints.rooms     import rooms_bp
from app.api.v1.endpoints.inventory import inventory_bp
from app.api.v1.endpoints.reports   import reports_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp,      url_prefix="/api/v1/auth")
    app.register_blueprint(menu_bp,      url_prefix="/api/v1/menu")
    app.register_blueprint(orders_bp,    url_prefix="/api/v1/orders")
    app.register_blueprint(payments_bp,  url_prefix="/api/v1/payments")
    app.register_blueprint(billing_bp,   url_prefix="/api/v1/billing")
    app.register_blueprint(customers_bp, url_prefix="/api/v1/customers")
    app.register_blueprint(tables_bp,    url_prefix="/api/v1/tables")
    app.register_blueprint(rooms_bp,     url_prefix="/api/v1/rooms")
    app.register_blueprint(inventory_bp, url_prefix="/api/v1/inventory")
    app.register_blueprint(reports_bp,   url_prefix="/api/v1/reports")
