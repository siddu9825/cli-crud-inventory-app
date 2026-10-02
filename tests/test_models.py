"""Unit tests for the Product domain entity."""

import unittest
from inventory_cli.domain.models import Product
from inventory_cli.domain.exceptions import ValidationError

class TestProductModel(unittest.TestCase):
    """Test suite for Product domain model invariants and business logic."""

    def test_valid_product_creation(self):
        """Ensure a valid product instantiates correctly with trimmed, uppercase SKU."""
        p = Product(
            sku="  lap-001  ",
            name="  Gaming Laptop  ",
            category="  Computers  ",
            price=1299.99,
            quantity=10,
            min_stock_threshold=5,
            description="High performance gaming laptop",
        )
        self.assertEqual(p.sku, "LAP-001")
        self.assertEqual(p.name, "Gaming Laptop")
        self.assertEqual(p.category, "Computers")
        self.assertEqual(p.price, 1299.99)
        self.assertEqual(p.quantity, 10)
        self.assertEqual(p.min_stock_threshold, 5)
        self.assertFalse(p.is_low_stock)
        self.assertEqual(p.total_value, 12999.90)

    def test_sku_validation(self):
        """Verify SKU invariants."""
        # Empty SKU
        with self.assertRaises(ValidationError) as ctx:
            Product(sku="", name="Item", category="Misc", price=10.0, quantity=5)
        self.assertIn("cannot be empty", str(ctx.exception))

        # Too short SKU
        with self.assertRaises(ValidationError) as ctx:
            Product(sku="AB", name="Item", category="Misc", price=10.0, quantity=5)
        self.assertIn("at least 3 characters", str(ctx.exception))

    def test_name_and_category_validation(self):
        """Verify name and category cannot be empty."""
        with self.assertRaises(ValidationError) as ctx:
            Product(sku="ABC-1", name="", category="Misc", price=10.0, quantity=5)
        self.assertIn("name cannot be empty", str(ctx.exception))

        with self.assertRaises(ValidationError) as ctx:
            Product(sku="ABC-1", name="Item", category="", price=10.0, quantity=5)
        self.assertIn("category cannot be empty", str(ctx.exception))

    def test_price_validation(self):
        """Verify price must be strictly positive."""
        with self.assertRaises(ValidationError) as ctx:
            Product(sku="ABC-1", name="Item", category="Misc", price=0.0, quantity=5)
        self.assertIn("must be strictly positive", str(ctx.exception))

        with self.assertRaises(ValidationError) as ctx:
            Product(sku="ABC-1", name="Item", category="Misc", price=-5.0, quantity=5)
        self.assertIn("must be strictly positive", str(ctx.exception))

    def test_quantity_and_threshold_validation(self):
        """Verify quantity and threshold cannot be negative."""
        with self.assertRaises(ValidationError) as ctx:
            Product(sku="ABC-1", name="Item", category="Misc", price=10.0, quantity=-1)
        self.assertIn("Quantity cannot be negative", str(ctx.exception))

        with self.assertRaises(ValidationError) as ctx:
            Product(sku="ABC-1", name="Item", category="Misc", price=10.0, quantity=5, min_stock_threshold=-2)
        self.assertIn("threshold cannot be negative", str(ctx.exception))

    def test_low_stock_property(self):
        """Test low stock evaluation."""
        p1 = Product(sku="ABC-1", name="Item", category="Misc", price=10.0, quantity=5, min_stock_threshold=5)
        self.assertTrue(p1.is_low_stock)

        p2 = Product(sku="ABC-2", name="Item", category="Misc", price=10.0, quantity=3, min_stock_threshold=5)
        self.assertTrue(p2.is_low_stock)

        p3 = Product(sku="ABC-3", name="Item", category="Misc", price=10.0, quantity=6, min_stock_threshold=5)
        self.assertFalse(p3.is_low_stock)

    def test_serialization(self):
        """Test to_dict and from_dict roundtrip."""
        original = Product(
            sku="SER-999",
            name="Serial Unit",
            category="Test",
            price=45.50,
            quantity=8,
            min_stock_threshold=3,
            description="Testing serialization",
        )
        d = original.to_dict()
        self.assertEqual(d["sku"], "SER-999")
        self.assertEqual(d["price"], 45.50)
        self.assertEqual(d["total_value"], 364.0)

        restored = Product.from_dict(d)
        self.assertEqual(restored.sku, original.sku)
        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.price, original.price)
        self.assertEqual(restored.quantity, original.quantity)

if __name__ == "__main__":
    unittest.main()
