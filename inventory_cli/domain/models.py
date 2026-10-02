"""Domain model representing a Product entity in the inventory system."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from .exceptions import ValidationError

@dataclass
class Product:
    """Represents an inventory product item."""
    sku: str
    name: str
    category: str
    price: float
    quantity: int
    id: Optional[int] = None
    min_stock_threshold: int = 5
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        self.sku = self.sku.strip().upper() if self.sku else ""
        self.name = self.name.strip() if self.name else ""
        self.category = self.category.strip() if self.category else ""
        self.description = self.description.strip() if self.description else ""
        self.validate()

    def validate(self) -> None:
        """Validate domain model invariants."""
        if not self.sku:
            raise ValidationError("Product SKU cannot be empty.")
        if len(self.sku) < 3:
            raise ValidationError("Product SKU must be at least 3 characters long.")
        if not self.name:
            raise ValidationError("Product name cannot be empty.")
        if not self.category:
            raise ValidationError("Product category cannot be empty.")
        try:
            self.price = float(self.price)
        except (ValueError, TypeError):
            raise ValidationError("Price must be a valid number.")
        if self.price <= 0:
            raise ValidationError("Price must be strictly positive (greater than 0.00).")
        try:
            self.quantity = int(self.quantity)
        except (ValueError, TypeError):
            raise ValidationError("Quantity must be a valid integer.")
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        try:
            self.min_stock_threshold = int(self.min_stock_threshold)
        except (ValueError, TypeError):
            raise ValidationError("Minimum stock threshold must be a valid integer.")
        if self.min_stock_threshold < 0:
            raise ValidationError("Minimum stock threshold cannot be negative.")

    @property
    def is_low_stock(self) -> bool:
        """Checks if current quantity is at or below the reorder threshold."""
        return self.quantity <= self.min_stock_threshold

    @property
    def total_value(self) -> float:
        """Computes total inventory valuation for this product."""
        return round(self.price * self.quantity, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary representation."""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "min_stock_threshold": self.min_stock_threshold,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_low_stock": self.is_low_stock,
            "total_value": self.total_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """Construct Product instance from dictionary."""
        return cls(
            id=data.get("id"),
            sku=data.get("sku", ""),
            name=data.get("name", ""),
            category=data.get("category", ""),
            price=float(data.get("price", 0.0)),
            quantity=int(data.get("quantity", 0)),
            min_stock_threshold=int(data.get("min_stock_threshold", 5)),
            description=data.get("description", ""),
            created_at=data.get("created_at") or datetime.now(timezone.utc).isoformat(),
            updated_at=data.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        )
