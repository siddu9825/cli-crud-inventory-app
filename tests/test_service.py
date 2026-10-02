"""Unit tests for the InventoryService business logic."""

import unittest
import tempfile
import os
from inventory_cli.service.inventory_service import InventoryService
from inventory_cli.repository.sqlite_repo import SQLiteProductRepository
from inventory_cli.domain.exceptions import (
    DuplicateSKUError,
    ProductNotFoundError,
    ValidationError,
)

class TestInventoryService(unittest.TestCase):
    """Test suite for business rules and application service layer."""

    def setUp(self):
        """Set up in-memory repo and service."""
        self.repo = SQLiteProductRepository(db_path=":memory:")
        self.service = InventoryService(repository=self.repo)

    def tearDown(self):
        """Clean up resources."""
        if hasattr(self.repo, "close"):
            self.repo.close()

    def test_add_and_get_product(self):
        """Test adding a product through the service layer."""
        p = self.service.add_product(
            sku="SVC-001",
            name="Service Product",
            category="Services",
            price=99.99,
            quantity=10,
            min_stock_threshold=3,
            description="Testing service add",
        )
        self.assertIsNotNone(p.id)
        self.assertEqual(p.sku, "SVC-001")

        fetched = self.service.get_product(p.id)
        self.assertEqual(fetched.name, "Service Product")

        fetched_sku = self.service.get_product_by_sku("svc-001")
        self.assertEqual(fetched_sku.id, p.id)

    def test_add_duplicate_sku_raises_error(self):
        """Ensure service blocks adding duplicate SKUs."""
        self.service.add_product(sku="DUP-SVC", name="First", category="Cat", price=10.0, quantity=5)
        with self.assertRaises(DuplicateSKUError):
            self.service.add_product(sku="dup-svc", name="Second", category="Cat", price=12.0, quantity=2)

    def test_get_nonexistent_product_raises_error(self):
        """Ensure fetching non-existent ID or SKU raises ProductNotFoundError."""
        with self.assertRaises(ProductNotFoundError):
            self.service.get_product(404)

        with self.assertRaises(ProductNotFoundError):
            self.service.get_product_by_sku("GHOST-SKU")

    def test_search_price_range_validation(self):
        """Ensure search validates that min_price <= max_price."""
        with self.assertRaises(ValidationError):
            self.service.search_products(min_price=100.0, max_price=50.0)

    def test_update_product_partial_fields(self):
        """Test updating select fields without wiping others."""
        p = self.service.add_product(sku="UPD-1", name="Original", category="Cat", price=10.0, quantity=5)
        updated = self.service.update_product(p.id, price=15.50, quantity=20)

        self.assertEqual(updated.name, "Original")
        self.assertEqual(updated.price, 15.50)
        self.assertEqual(updated.quantity, 20)

    def test_update_duplicate_sku_collision(self):
        """Ensure updating SKU to one that is already in use by another item fails."""
        p1 = self.service.add_product(sku="SKU-A", name="A", category="Cat", price=10.0, quantity=5)
        p2 = self.service.add_product(sku="SKU-B", name="B", category="Cat", price=10.0, quantity=5)

        with self.assertRaises(DuplicateSKUError):
            self.service.update_product(p2.id, sku="SKU-A")

    def test_delete_product(self):
        """Test deleting through service."""
        p = self.service.add_product(sku="DEL-SVC", name="Delete Me", category="Cat", price=5.0, quantity=1)
        self.assertTrue(self.service.delete_product(p.id))

        with self.assertRaises(ProductNotFoundError):
            self.service.get_product(p.id)

    def test_inventory_analytics(self):
        """Test inventory metrics computation."""
        self.service.add_product(sku="SKU-A1", name="Item 1", category="Elec", price=100.0, quantity=2, min_stock_threshold=5) # low stock
        self.service.add_product(sku="SKU-A2", name="Item 2", category="Elec", price=50.0, quantity=10, min_stock_threshold=5)
        self.service.add_product(sku="SKU-A3", name="Item 3", category="Books", price=20.0, quantity=5, min_stock_threshold=2)

        stats = self.service.get_analytics()
        self.assertEqual(stats["total_products"], 3)
        self.assertEqual(stats["total_units"], 17)
        self.assertEqual(stats["total_valuation"], 200.0 + 500.0 + 100.0)
        self.assertEqual(stats["low_stock_count"], 1)
        self.assertEqual(stats["low_stock_items"][0].sku, "SKU-A1")
        self.assertEqual(stats["category_count"], 2)

    def test_json_export_and_import(self):
        """Test JSON backup and import workflow."""
        self.service.add_product(sku="EXP-1", name="Export Item 1", category="Exp", price=10.0, quantity=5)
        self.service.add_product(sku="EXP-2", name="Export Item 2", category="Exp", price=20.0, quantity=8)

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "backup.json")
            exported_count = self.service.export_to_json(file_path)
            self.assertEqual(exported_count, 2)
            self.assertTrue(os.path.exists(file_path))

            # Test import into a fresh database
            new_repo = SQLiteProductRepository(db_path=":memory:")
            new_service = InventoryService(repository=new_repo)

            result = new_service.import_from_json(file_path)
            self.assertEqual(result["created"], 2)
            self.assertEqual(result["skipped"], 0)
            self.assertEqual(new_repo.count(), 2)

            # Importing again should skip duplicates
            reimport = new_service.import_from_json(file_path)
            self.assertEqual(reimport["created"], 0)
            self.assertEqual(reimport["skipped"], 2)

if __name__ == "__main__":
    unittest.main()
