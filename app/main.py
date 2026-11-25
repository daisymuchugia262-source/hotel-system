"""
App factory â€” creates the Flask application.
No business logic here â€” just wiring.
"""
from __future__ import annotations

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.api.v1.router import register_blueprints
from app.core.exceptions import (
    DomainError, NotFoundError, ValidationError,
    AuthenticationError, PaymentError, OrderNotPayableError,
)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=r"C:\Users\user\OneDrive\Desktop\scaffold.sh\frontend", static_url_path="")
    app.url_map.strict_slashes = False
    CORS(app)

    register_blueprints(app)
    _register_error_handlers(app)

    @app.get("/")
    def frontend():
        """Serve the single-page frontend when the server root is opened."""
        return send_from_directory(app.static_folder, "index.html")

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
