"""Unit tests for the SQLiteProductRepository."""

import unittest
from inventory_cli.domain.models import Product
from inventory_cli.domain.exceptions import DuplicateSKUError, ProductNotFoundError
from inventory_cli.repository.sqlite_repo import SQLiteProductRepository

class TestSQLiteProductRepository(unittest.TestCase):
    """Test suite for SQLite persistence layer."""

    def setUp(self):
        """Initialize an in-memory SQLite database before each test."""
        self.repo = SQLiteProductRepository(db_path=":memory:")

    def tearDown(self):
        """Close database connection."""
        if hasattr(self.repo, "close"):
            self.repo.close()

    def test_create_and_get_by_id(self):
        """Ensure product is created with auto-increment ID and retrieved accurately."""
        p = Product(
            sku="DEV-001",
            name="Developer Monitor",
            category="Hardware",
            price=399.00,
            quantity=15,
            min_stock_threshold=5,
            description="Ultra HD monitor",
        )
        saved = self.repo.create(p)
        self.assertIsNotNone(saved.id)

        fetched = self.repo.get_by_id(saved.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.sku, "DEV-001")
        self.assertEqual(fetched.name, "Developer Monitor")
        self.assertEqual(fetched.price, 399.00)
        self.assertEqual(fetched.quantity, 15)

    def test_get_by_sku_case_insensitive(self):
        """Test SKU lookup works regardless of casing."""
        p = Product(sku="KEY-100", name="Keyboard", category="Peripherals", price=50.0, quantity=10)
        self.repo.create(p)

        self.assertIsNotNone(self.repo.get_by_sku("KEY-100"))
        self.assertIsNotNone(self.repo.get_by_sku("key-100"))
        self.assertIsNone(self.repo.get_by_sku("NONEXISTENT"))

    def test_duplicate_sku_raises_error(self):
        """Ensure inserting a product with duplicate SKU raises DuplicateSKUError."""
        p1 = Product(sku="DUP-01", name="Original Item", category="Cat A", price=20.0, quantity=5)
        self.repo.create(p1)

        p2 = Product(sku="DUP-01", name="Duplicate Item", category="Cat B", price=25.0, quantity=2)
        with self.assertRaises(DuplicateSKUError):
            self.repo.create(p2)

    def test_list_all_and_sorting(self):
        """Test listing with sorting options."""
        p1 = Product(sku="AAA-1", name="Banana", category="Fruit", price=1.50, quantity=20)
        p2 = Product(sku="BBB-2", name="Apple", category="Fruit", price=2.00, quantity=5)
        self.repo.create(p1)
        self.repo.create(p2)

        items_by_name = self.repo.list_all(sort_by="name", descending=False)
        self.assertEqual(items_by_name[0].name, "Apple")
        self.assertEqual(items_by_name[1].name, "Banana")

        items_by_price_desc = self.repo.list_all(sort_by="price", descending=True)
        self.assertEqual(items_by_price_desc[0].price, 2.00)
        self.assertEqual(items_by_price_desc[1].price, 1.50)

    def test_search_filters(self):
        """Test multi-attribute search functionality."""
        self.repo.create(Product(sku="TAB-01", name="Pro Tablet", category="Electronics", price=800.0, quantity=10, min_stock_threshold=5))
        self.repo.create(Product(sku="TAB-02", name="Budget Tablet", category="Electronics", price=200.0, quantity=2, min_stock_threshold=5))
        self.repo.create(Product(sku="DESK-1", name="Office Desk", category="Furniture", price=350.0, quantity=8, min_stock_threshold=3))

        # Query substring
        q_results = self.repo.search(query="Tablet")
        self.assertEqual(len(q_results), 2)

        # Category filter
        cat_results = self.repo.search(category="Furniture")
        self.assertEqual(len(cat_results), 1)
        self.assertEqual(cat_results[0].sku, "DESK-1")

        # Low stock filter
        low_stock = self.repo.search(low_stock_only=True)
        self.assertEqual(len(low_stock), 1)
        self.assertEqual(low_stock[0].sku, "TAB-02")

        # Price range filter
        price_filtered = self.repo.search(min_price=250.0, max_price=500.0)
        self.assertEqual(len(price_filtered), 1)
        self.assertEqual(price_filtered[0].name, "Office Desk")

    def test_update_product(self):
        """Test updating an existing product."""
        p = self.repo.create(Product(sku="UPD-01", name="Old Name", category="Tools", price=30.0, quantity=10))
        p.name = "New Name"
        p.price = 35.0
        p.quantity = 12

        updated = self.repo.update(p)
        self.assertEqual(updated.name, "New Name")
        self.assertEqual(updated.price, 35.0)
        self.assertEqual(updated.quantity, 12)

        refetched = self.repo.get_by_id(p.id)
        self.assertEqual(refetched.name, "New Name")

    def test_delete_product(self):
        """Test deleting a product."""
        p = self.repo.create(Product(sku="DEL-01", name="To Delete", category="Misc", price=10.0, quantity=1))
        self.assertTrue(self.repo.delete(p.id))
        self.assertIsNone(self.repo.get_by_id(p.id))

        with self.assertRaises(ProductNotFoundError):
            self.repo.delete(9999)

    def test_count_and_categories(self):
        """Test count and distinct category listing."""
        self.assertEqual(self.repo.count(), 0)
        self.repo.create(Product(sku="CAT-1", name="Item 1", category="Books", price=10.0, quantity=2))
        self.repo.create(Product(sku="CAT-2", name="Item 2", category="Toys", price=15.0, quantity=4))
        self.repo.create(Product(sku="CAT-3", name="Item 3", category="Books", price=20.0, quantity=1))

        self.assertEqual(self.repo.count(), 3)
        categories = self.repo.get_categories()
        self.assertEqual(categories, ["Books", "Toys"])

if __name__ == "__main__":
    unittest.main()
