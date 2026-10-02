"""SQLite implementation of the BaseProductRepository."""

import os
import sqlite3
from typing import List, Optional
from datetime import datetime, timezone
from .base import BaseProductRepository
from ..domain.models import Product
from ..domain.exceptions import DuplicateSKUError, StorageError, ProductNotFoundError

class SQLiteProductRepository(BaseProductRepository):
    """Manages persistent SQLite storage for Products."""

    def __init__(self, db_path: str = "data/inventory.db"):
        self.db_path = db_path
        self._shared_conn: Optional[sqlite3.Connection] = None
        if db_path != ":memory:":
            parent_dir = os.path.dirname(db_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        else:
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
            self._shared_conn.execute("PRAGMA foreign_keys = ON;")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create or reuse connection with row factory configured."""
        if self._shared_conn is not None:
            return self._shared_conn
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            raise StorageError(f"Database connection failed: {e}")

    def _init_db(self) -> None:
        """Initialize products table and indexes."""
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL UNIQUE COLLATE NOCASE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            min_stock_threshold INTEGER NOT NULL DEFAULT 5,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
        """
        try:
            with self._get_connection() as conn:
                conn.executescript(query)
        except sqlite3.Error as e:
            raise StorageError(f"Failed to initialize database schema: {e}")

    def _row_to_product(self, row: sqlite3.Row) -> Product:
        """Convert a sqlite3.Row to a Product domain entity."""
        return Product(
            id=row["id"],
            sku=row["sku"],
            name=row["name"],
            category=row["category"],
            price=float(row["price"]),
            quantity=int(row["quantity"]),
            min_stock_threshold=int(row["min_stock_threshold"]),
            description=row["description"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, product: Product) -> Product:
        """Insert a new product record."""
        now = datetime.now(timezone.utc).isoformat()
        product.created_at = now
        product.updated_at = now

        query = """
        INSERT INTO products (sku, name, category, price, quantity, min_stock_threshold, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (
                        product.sku,
                        product.name,
                        product.category,
                        product.price,
                        product.quantity,
                        product.min_stock_threshold,
                        product.description,
                        product.created_at,
                        product.updated_at,
                    ),
                )
                product.id = cursor.lastrowid
                return product
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) and "products.sku" in str(e):
                raise DuplicateSKUError(product.sku)
            raise StorageError(f"Database integrity violation: {e}")
        except sqlite3.Error as e:
            raise StorageError(f"Database error during creation: {e}")

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Fetch single product by internal database ID."""
        query = "SELECT * FROM products WHERE id = ?"
        try:
            with self._get_connection() as conn:
                row = conn.execute(query, (product_id,)).fetchone()
                return self._row_to_product(row) if row else None
        except sqlite3.Error as e:
            raise StorageError(f"Error fetching product ID {product_id}: {e}")

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Fetch single product by SKU."""
        query = "SELECT * FROM products WHERE sku = ? COLLATE NOCASE"
        try:
            with self._get_connection() as conn:
                row = conn.execute(query, (sku.strip(),)).fetchone()
                return self._row_to_product(row) if row else None
        except sqlite3.Error as e:
            raise StorageError(f"Error fetching product SKU '{sku}': {e}")

    def list_all(self, sort_by: str = "id", descending: bool = False) -> List[Product]:
        """List all products, sorted by specified column."""
        valid_cols = {"id", "sku", "name", "category", "price", "quantity", "created_at"}
        col = sort_by if sort_by in valid_cols else "id"
        order = "DESC" if descending else "ASC"
        query = f"SELECT * FROM products ORDER BY {col} {order}"
        try:
            with self._get_connection() as conn:
                rows = conn.execute(query).fetchall()
                return [self._row_to_product(r) for r in rows]
        except sqlite3.Error as e:
            raise StorageError(f"Error listing products: {e}")

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        low_stock_only: bool = False,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Product]:
        """Filter products by multiple search criteria."""
        clauses = []
        params = []

        if query:
            clean_q = f"%{query.strip()}%"
            clauses.append("(sku LIKE ? OR name LIKE ? OR description LIKE ?)")
            params.extend([clean_q, clean_q, clean_q])

        if category:
            clauses.append("category = ? COLLATE NOCASE")
            params.append(category.strip())

        if low_stock_only:
            clauses.append("quantity <= min_stock_threshold")

        if min_price is not None:
            clauses.append("price >= ?")
            params.append(min_price)

        if max_price is not None:
            clauses.append("price <= ?")
            params.append(max_price)

        where_str = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM products {where_str} ORDER BY name ASC"

        try:
            with self._get_connection() as conn:
                rows = conn.execute(sql, params).fetchall()
                return [self._row_to_product(r) for r in rows]
        except sqlite3.Error as e:
            raise StorageError(f"Error searching products: {e}")

    def update(self, product: Product) -> Product:
        """Update an existing product."""
        if product.id is None:
            raise ProductNotFoundError("None (Product ID is required for update)")

        now = datetime.now(timezone.utc).isoformat()
        product.updated_at = now

        query = """
        UPDATE products
        SET sku = ?, name = ?, category = ?, price = ?, quantity = ?,
            min_stock_threshold = ?, description = ?, updated_at = ?
        WHERE id = ?
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (
                        product.sku,
                        product.name,
                        product.category,
                        product.price,
                        product.quantity,
                        product.min_stock_threshold,
                        product.description,
                        product.updated_at,
                        product.id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ProductNotFoundError(str(product.id))
                return product
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) and "products.sku" in str(e):
                raise DuplicateSKUError(product.sku)
            raise StorageError(f"Integrity violation during update: {e}")
        except sqlite3.Error as e:
            raise StorageError(f"Error updating product: {e}")

    def delete(self, product_id: int) -> bool:
        """Delete product by ID."""
        query = "DELETE FROM products WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (product_id,))
                if cursor.rowcount == 0:
                    raise ProductNotFoundError(str(product_id))
                return True
        except sqlite3.Error as e:
            raise StorageError(f"Error deleting product ID {product_id}: {e}")

    def count(self) -> int:
        """Count total product records."""
        query = "SELECT COUNT(*) FROM products"
        try:
            with self._get_connection() as conn:
                return conn.execute(query).fetchone()[0]
        except sqlite3.Error as e:
            raise StorageError(f"Error counting products: {e}")

    def get_categories(self) -> List[str]:
        """Fetch distinct categories."""
        query = "SELECT DISTINCT category FROM products ORDER BY category ASC"
        try:
            with self._get_connection() as conn:
                rows = conn.execute(query).fetchall()
                return [r["category"] for r in rows]
        except sqlite3.Error as e:
            raise StorageError(f"Error fetching categories: {e}")

    def close(self) -> None:
        """Close shared connection if open."""
        if self._shared_conn is not None:
            try:
                self._shared_conn.close()
            except sqlite3.Error:
                pass
            self._shared_conn = None
