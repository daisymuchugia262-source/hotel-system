# Hotel Billing System — Backend

Flask REST API with clean architecture:

    app/
      core/         → enums, exceptions, config
      models/       → pure domain entities (dataclasses)
      schemas/      → (unused in phase 1–4; reserved for Phase 8+)
      database/     → JsonStore (persistence)
      repositories/ → data access (10 repos)
      services/     → business logic (5 services)
      api/v1/       → HTTP endpoints

## Setup

    python -m pip install flask flask-cors pytest
    python scripts/seed_menu.py
    python run.py

Server starts on http://localhost:5000.

## Run tests

    python -m pytest tests\ -v

## API

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health | Service status |
| GET | /api/v1/menu | List menu |
| POST | /api/v1/orders | Create order |
| POST | /api/v1/payments | Add payment |
| GET | /api/v1/billing/receipt/<id> | Get receipt |
| POST | /api/v1/auth/register | Register user |
| POST | /api/v1/auth/login | Login |
