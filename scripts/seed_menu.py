"""
Seed data/menu.json with sample menu items.
Run from backend/:  python scripts/seed_menu.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
from app.repositories.menu_repository import MenuRepository
from app.models.menu import MenuItem


SAMPLE_ITEMS = [
    ("Chicken Biryani", "food",    "450.00"),
    ("Beef Burger",     "food",    "350.00"),
    ("Pizza (Large)",   "food",    "800.00"),
    ("Fried Chicken",   "food",    "600.00"),
    ("Fish & Chips",    "food",    "550.00"),
    ("Soda (500ml)",    "drink",   "100.00"),
    ("Juice (300ml)",   "drink",   "150.00"),
    ("Ice Cream",       "dessert", "200.00"),
    ("Coffee",          "drink",   "120.00"),
    ("Water (1L)",      "drink",    "80.00"),
]


def main() -> None:
    repo = MenuRepository()
    existing = repo.list_all()
    if existing:
        print(f"menu.json already has {len(existing)} items. Skipping seed.")
        return

    for name, category, price in SAMPLE_ITEMS:
        repo.create(MenuItem(name=name, category=category, price=Decimal(price)))

    print(f"Seeded {len(SAMPLE_ITEMS)} menu items into data/menu.json")


if __name__ == "__main__":
    main()
