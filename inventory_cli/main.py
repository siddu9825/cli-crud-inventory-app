"""Application entry point for InventoCLI."""

import argparse
import os
import sys
from inventory_cli.repository.sqlite_repo import SQLiteProductRepository
from inventory_cli.service.inventory_service import InventoryService
from inventory_cli.cli.menu import InventoryCLI
from inventory_cli.domain.models import Product

def seed_sample_data(service: InventoryService) -> None:
    """Pre-populate sample records if the database is newly initialized."""
    samples = [
        Product(
            sku="LAP-001",
            name="MacBook Pro 16",
            category="Electronics",
            price=2499.00,
            quantity=12,
            min_stock_threshold=5,
            description="M3 Max chip, 36GB unified memory, 1TB SSD storage",
        ),
        Product(
            sku="KEY-002",
            name="Mechanical Keyboard",
            category="Accessories",
            price=129.50,
            quantity=3,
            min_stock_threshold=5,
            description="Hot-swappable RGB wireless mechanical keyboard (Low Stock)",
        ),
        Product(
            sku="MON-003",
            name="4K Ultra-wide Monitor",
            category="Electronics",
            price=699.99,
            quantity=8,
            min_stock_threshold=4,
            description="34-inch curved USB-C hub display with HDR400",
        ),
        Product(
            sku="DSK-004",
            name="Ergonomic Standing Desk",
            category="Furniture",
            price=450.00,
            quantity=2,
            min_stock_threshold=3,
            description="Dual-motor motorized standing desk with solid oak top (Low Stock)",
        ),
        Product(
            sku="MOU-005",
            name="Wireless Precision Mouse",
            category="Accessories",
            price=89.90,
            quantity=25,
            min_stock_threshold=10,
            description="Ergonomic laser mouse with magnetic scroll wheel",
        ),
    ]

    for item in samples:
        try:
            service.repository.create(item)
        except Exception:
            pass

def main():
    """Parse CLI arguments and run interactive application."""
    parser = argparse.ArgumentParser(
        description="InventoCLI - Enterprise Command Line Inventory Management System"
    )
    parser.add_argument(
        "--db",
        default="data/inventory.db",
        help="Path to SQLite database file (default: data/inventory.db)",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Do not seed sample products if database is empty",
    )

    args = parser.parse_args()

    repo = SQLiteProductRepository(db_path=args.db)
    service = InventoryService(repository=repo)

    if not args.no_seed and repo.count() == 0:
        seed_sample_data(service)

    cli = InventoryCLI(service=service)
    cli.run()

if __name__ == "__main__":
    main()
