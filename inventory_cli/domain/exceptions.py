"""Domain exceptions for the Inventory Management System."""

class InventoryError(Exception):
    """Base exception for all inventory domain errors."""
    pass

class ProductNotFoundError(InventoryError):
    """Raised when a product with the specified identifier or SKU does not exist."""
    def __init__(self, identifier: str):
        super().__init__(f"Product with identifier '{identifier}' was not found.")
        self.identifier = identifier

class DuplicateSKUError(InventoryError):
    """Raised when attempting to add or update a product with an existing SKU."""
    def __init__(self, sku: str):
        super().__init__(f"A product with SKU '{sku}' already exists.")
        self.sku = sku

class ValidationError(InventoryError):
    """Raised when domain entity invariants or input validations fail."""
    def __init__(self, message: str):
        super().__init__(message)

class StorageError(InventoryError):
    """Raised when a persistence or database operation fails."""
    pass
