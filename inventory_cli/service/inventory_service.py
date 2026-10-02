"""Business logic service for managing product inventory."""

import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from ..domain.models import Product
from ..domain.exceptions import (
    ProductNotFoundError,
    DuplicateSKUError,
    ValidationError,
    StorageError,
)
from ..repository.base import BaseProductRepository

class InventoryService:
    """Orchestrates inventory operations, validations, and analytics."""

    def __init__(self, repository: BaseProductRepository):
        self.repository = repository

    def add_product(
        self,
        sku: str,
        name: str,
        category: str,
        price: float,
        quantity: int,
        min_stock_threshold: int = 5,
        description: str = "",
    ) -> Product:
        """Create and persist a new product after validating uniqueness and constraints."""
        clean_sku = sku.strip().upper()
        existing = self.repository.get_by_sku(clean_sku)
        if existing:
            raise DuplicateSKUError(clean_sku)

        product = Product(
            sku=clean_sku,
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            min_stock_threshold=min_stock_threshold,
            description=description,
        )
        return self.repository.create(product)

    def get_product(self, product_id: int) -> Product:
        """Retrieve a product by its numeric ID."""
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(str(product_id))
        return product

    def get_product_by_sku(self, sku: str) -> Product:
        """Retrieve a product by its SKU."""
        clean_sku = sku.strip().upper()
        product = self.repository.get_by_sku(clean_sku)
        if not product:
            raise ProductNotFoundError(clean_sku)
        return product

    def list_products(self, sort_by: str = "id", descending: bool = False) -> List[Product]:
        """List all inventory products."""
        return self.repository.list_all(sort_by=sort_by, descending=descending)

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        low_stock_only: bool = False,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Product]:
        """Search products with multi-criteria filters."""
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValidationError("Minimum price cannot exceed maximum price.")

        return self.repository.search(
            query=query,
            category=category,
            low_stock_only=low_stock_only,
            min_price=min_price,
            max_price=max_price,
        )

    def update_product(
        self,
        product_id: int,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        price: Optional[float] = None,
        quantity: Optional[int] = None,
        min_stock_threshold: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Product:
        """Selectively update product fields and validate state."""
        product = self.get_product(product_id)

        if sku is not None:
            clean_sku = sku.strip().upper()
            if clean_sku != product.sku:
                existing = self.repository.get_by_sku(clean_sku)
                if existing and existing.id != product.id:
                    raise DuplicateSKUError(clean_sku)
                product.sku = clean_sku

        if name is not None:
            product.name = name.strip()
        if category is not None:
            product.category = category.strip()
        if price is not None:
            product.price = price
        if quantity is not None:
            product.quantity = quantity
        if min_stock_threshold is not None:
            product.min_stock_threshold = min_stock_threshold
        if description is not None:
            product.description = description.strip()

        product.validate()
        return self.repository.update(product)

    def delete_product(self, product_id: int) -> bool:
        """Remove a product from inventory."""
        # Ensure it exists before attempting delete
        self.get_product(product_id)
        return self.repository.delete(product_id)

    def get_analytics(self) -> Dict[str, Any]:
        """Compute summary metrics and low-stock warnings."""
        products = self.repository.list_all()
        total_products = len(products)
        total_units = sum(p.quantity for p in products)
        total_valuation = round(sum(p.total_value for p in products), 2)
        low_stock = [p for p in products if p.is_low_stock]
        categories = self.repository.get_categories()

        avg_price = (
            round(sum(p.price for p in products) / total_products, 2)
            if total_products > 0
            else 0.0
        )

        return {
            "total_products": total_products,
            "total_units": total_units,
            "total_valuation": total_valuation,
            "low_stock_count": len(low_stock),
            "low_stock_items": low_stock,
            "category_count": len(categories),
            "categories": categories,
            "average_price": avg_price,
        }

    def export_to_json(self, export_path: str) -> int:
        """Export all current products to a structured JSON file."""
        products = self.repository.list_all(sort_by="id")
        export_data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "record_count": len(products),
            "products": [p.to_dict() for p in products],
        }

        try:
            parent_dir = os.path.dirname(export_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
            return len(products)
        except OSError as e:
            raise StorageError(f"Failed to export inventory to '{export_path}': {e}")

    def import_from_json(self, import_path: str) -> Dict[str, int]:
        """Import products from JSON file with validation."""
        if not os.path.exists(import_path):
            raise StorageError(f"Import file '{import_path}' does not exist.")

        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValidationError(f"Invalid JSON file format: {e}")

        items = data.get("products") if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValidationError("JSON payload must contain a list of products.")

        created_count = 0
        skipped_count = 0

        for item in items:
            try:
                sku = str(item.get("sku", "")).strip().upper()
                if not sku or self.repository.get_by_sku(sku):
                    skipped_count += 1
                    continue
                product = Product.from_dict(item)
                product.id = None  # let DB assign fresh ID
                self.repository.create(product)
                created_count += 1
            except Exception:
                skipped_count += 1

        return {"created": created_count, "skipped": skipped_count}
