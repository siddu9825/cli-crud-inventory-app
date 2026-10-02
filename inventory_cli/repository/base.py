"""Abstract base repository defining persistent storage interface for Products."""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.models import Product

class BaseProductRepository(ABC):
    """Abstract interface for product persistence."""

    @abstractmethod
    def create(self, product: Product) -> Product:
        """Persist a new product. Returns product with assigned ID."""
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Fetch a product by primary numeric ID."""
        pass

    @abstractmethod
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Fetch a product by unique SKU code."""
        pass

    @abstractmethod
    def list_all(self, sort_by: str = "id", descending: bool = False) -> List[Product]:
        """Retrieve all products in storage."""
        pass

    @abstractmethod
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        low_stock_only: bool = False,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Product]:
        """Search products using multiple matching criteria."""
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        """Update an existing product record."""
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Delete product by primary ID. Returns True if deleted."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total number of products."""
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """Return list of distinct categories currently in use."""
        pass
