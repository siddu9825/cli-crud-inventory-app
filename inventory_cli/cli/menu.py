"""Interactive menu controller and navigation dispatcher for the CLI application."""

import sys
from typing import Optional
from ..service.inventory_service import InventoryService
from ..domain.exceptions import (
    InventoryError,
    ProductNotFoundError,
    DuplicateSKUError,
    ValidationError,
    StorageError,
)
from .validators import (
    prompt_string,
    prompt_float,
    prompt_int,
    prompt_confirm,
    prompt_choice,
    print_error,
    print_success,
    print_warning,
    BOLD,
    CYAN,
    YELLOW,
    RESET,
)
from .views import (
    render_banner,
    render_products_table,
    render_product_detail,
    render_analytics_dashboard,
)

class InventoryCLI:
    """Manages CLI menus and user interactions."""

    def __init__(self, service: InventoryService):
        self.service = service

    def display_main_menu(self) -> None:
        """Render the primary navigation menu."""
        print(f"\n{BOLD}{CYAN}------------------- MAIN MENU -------------------{RESET}")
        print(f"  {BOLD}[1]{RESET} Add New Product        {BOLD}[6]{RESET} Delete Product")
        print(f"  {BOLD}[2]{RESET} View All Products      {BOLD}[7]{RESET} Inventory Analytics")
        print(f"  {BOLD}[3]{RESET} Search Products        {BOLD}[8]{RESET} Export / Import Data")
        print(f"  {BOLD}[4]{RESET} View Product Details   {BOLD}[9]{RESET} Exit Application")
        print(f"  {BOLD}[5]{RESET} Update Product")
        print(f"{BOLD}{CYAN}-------------------------------------------------{RESET}")

    def run(self) -> None:
        """Main interaction loop."""
        render_banner()
        while True:
            try:
                self.display_main_menu()
                choice = input(f"{CYAN}Enter selection (1-9): {RESET}").strip()
                if choice == "1":
                    self.handle_add_product()
                elif choice == "2":
                    self.handle_view_all()
                elif choice == "3":
                    self.handle_search()
                elif choice == "4":
                    self.handle_view_detail()
                elif choice == "5":
                    self.handle_update_product()
                elif choice == "6":
                    self.handle_delete_product()
                elif choice == "7":
                    self.handle_analytics()
                elif choice == "8":
                    self.handle_export_import()
                elif choice == "9":
                    if prompt_confirm("Are you sure you want to exit?", default=True):
                        print(f"\n{CYAN}Thank you for using InventoCLI. Goodbye!{RESET}\n")
                        sys.exit(0)
                else:
                    print_error("Invalid selection. Please choose an option between 1 and 9.")
            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}Operation interrupted by user.{RESET}")
                if prompt_confirm("Exit application?", default=False):
                    print(f"\n{CYAN}Goodbye!{RESET}\n")
                    sys.exit(0)
            except Exception as e:
                print_error(f"Unexpected system error: {e}")

    # --------------------------------------------------------------------------
    # Handlers
    # --------------------------------------------------------------------------

    def handle_add_product(self) -> None:
        """Workflow: Add a new product."""
        print(f"\n{BOLD}▶ ADD NEW PRODUCT{RESET}")
        try:
            sku = prompt_string("Product SKU (e.g. LAP-001)", min_len=3, to_upper=True)
            name = prompt_string("Product Name", min_len=1)
            category = prompt_string("Category (e.g. Electronics, Office, Apparel)", min_len=1)
            price = prompt_float("Unit Price ($)", min_val=0.01)
            quantity = prompt_int("Initial Stock Quantity", min_val=0)
            min_stock = prompt_int("Low Stock Alert Threshold", min_val=0, default=5)
            description = prompt_string("Product Description (optional)", min_len=0, allow_blank=True)

            product = self.service.add_product(
                sku=sku,
                name=name,
                category=category,
                price=price,
                quantity=quantity,
                min_stock_threshold=min_stock if min_stock is not None else 5,
                description=description or "",
            )
            print_success(f"Product '{product.name}' (SKU: {product.sku}) created successfully with ID {product.id}!")
            render_product_detail(product)
        except (DuplicateSKUError, ValidationError, StorageError) as e:
            print_error(str(e))

    def handle_view_all(self) -> None:
        """Workflow: List all products."""
        print(f"\n{BOLD}▶ VIEW ALL PRODUCTS{RESET}")
        try:
            products = self.service.list_products(sort_by="id")
            render_products_table(products, title="Complete Inventory Roster")
        except StorageError as e:
            print_error(str(e))

    def handle_search(self) -> None:
        """Workflow: Search products across multiple criteria."""
        print(f"\n{BOLD}▶ SEARCH PRODUCTS{RESET}")
        print("  [1] Search by Keyword (SKU, Name, Description)")
        print("  [2] Filter by Category")
        print("  [3] Show Low-Stock Items Only")
        print("  [4] Filter by Price Range")
        print("  [5] Return to Main Menu")

        sub_choice = input(f"{CYAN}Select search mode (1-5): {RESET}").strip()

        try:
            if sub_choice == "1":
                query = prompt_string("Enter search keyword", min_len=1)
                results = self.service.search_products(query=query)
                render_products_table(results, title=f"Search Results for '{query}'")
            elif sub_choice == "2":
                category = prompt_string("Enter category name", min_len=1)
                results = self.service.search_products(category=category)
                render_products_table(results, title=f"Products in Category '{category}'")
            elif sub_choice == "3":
                results = self.service.search_products(low_stock_only=True)
                render_products_table(results, title="Critical Low-Stock Items")
            elif sub_choice == "4":
                min_p = prompt_float("Minimum Price ($) (press Enter to skip)", min_val=0.0, allow_blank=True)
                max_p = prompt_float("Maximum Price ($) (press Enter to skip)", min_val=0.0, allow_blank=True)
                results = self.service.search_products(min_price=min_p, max_price=max_p)
                render_products_table(results, title=f"Products in Price Range [${min_p or 0:.2f} - ${max_p or '∞'}]")
            elif sub_choice == "5":
                return
            else:
                print_error("Invalid option.")
        except (ValidationError, StorageError) as e:
            print_error(str(e))

    def _resolve_product_target(self, action_name: str) -> Optional[int]:
        """Helper to prompt for ID or SKU and resolve product ID."""
        identifier = prompt_string(f"Enter Product ID or SKU to {action_name}", min_len=1)
        if identifier.isdigit():
            try:
                prod = self.service.get_product(int(identifier))
                return prod.id
            except ProductNotFoundError:
                pass

        try:
            prod = self.service.get_product_by_sku(identifier)
            return prod.id
        except ProductNotFoundError:
            print_error(f"No product found matching '{identifier}'.")
            return None

    def handle_view_detail(self) -> None:
        """Workflow: View single product specification."""
        print(f"\n{BOLD}▶ VIEW PRODUCT DETAILS{RESET}")
        try:
            prod_id = self._resolve_product_target("view")
            if prod_id is not None:
                product = self.service.get_product(prod_id)
                render_product_detail(product)
        except (ProductNotFoundError, StorageError) as e:
            print_error(str(e))

    def handle_update_product(self) -> None:
        """Workflow: Update product fields."""
        print(f"\n{BOLD}▶ UPDATE PRODUCT{RESET}")
        try:
            prod_id = self._resolve_product_target("update")
            if prod_id is None:
                return

            current = self.service.get_product(prod_id)
            print(f"\nEditing product: {BOLD}{current.name}{RESET} (SKU: {current.sku})")
            print(f"{YELLOW}Hint: Press [Enter] on any field to keep its current value.{RESET}\n")

            new_sku = prompt_string("Product SKU", min_len=3, default=current.sku, to_upper=True)
            new_name = prompt_string("Product Name", min_len=1, default=current.name)
            new_category = prompt_string("Category", min_len=1, default=current.category)
            new_price = prompt_float("Unit Price ($)", min_val=0.01, default=current.price)
            new_qty = prompt_int("Stock Quantity", min_val=0, default=current.quantity)
            new_threshold = prompt_int("Low Stock Threshold", min_val=0, default=current.min_stock_threshold)
            new_desc = prompt_string("Description", min_len=0, default=current.description, allow_blank=True)

            updated = self.service.update_product(
                product_id=prod_id,
                sku=new_sku,
                name=new_name,
                category=new_category,
                price=new_price,
                quantity=new_qty,
                min_stock_threshold=new_threshold,
                description=new_desc,
            )
            print_success(f"Product '{updated.name}' (SKU: {updated.sku}) updated successfully!")
            render_product_detail(updated)
        except (ProductNotFoundError, DuplicateSKUError, ValidationError, StorageError) as e:
            print_error(str(e))

    def handle_delete_product(self) -> None:
        """Workflow: Delete a product with confirmation."""
        print(f"\n{BOLD}▶ DELETE PRODUCT{RESET}")
        try:
            prod_id = self._resolve_product_target("delete")
            if prod_id is None:
                return

            product = self.service.get_product(prod_id)
            print_warning(f"Target: [{product.sku}] {product.name} (Stock: {product.quantity}, Value: ${product.total_value:,.2f})")
            
            if prompt_confirm("Are you sure you want to permanently delete this product?", default=False):
                self.service.delete_product(prod_id)
                print_success(f"Product '{product.name}' (SKU: {product.sku}) has been deleted.")
            else:
                print(f"{CYAN}Deletion cancelled.{RESET}")
        except (ProductNotFoundError, StorageError) as e:
            print_error(str(e))

    def handle_analytics(self) -> None:
        """Workflow: Display inventory analytics."""
        try:
            metrics = self.service.get_analytics()
            render_analytics_dashboard(metrics)
        except StorageError as e:
            print_error(str(e))

    def handle_export_import(self) -> None:
        """Workflow: JSON Export & Import operations."""
        print(f"\n{BOLD}▶ DATA PORTABILITY (EXPORT / IMPORT){RESET}")
        print("  [1] Export Current Inventory to JSON")
        print("  [2] Import Inventory from JSON")
        print("  [3] Return to Main Menu")

        choice = input(f"{CYAN}Select option (1-3): {RESET}").strip()
        try:
            if choice == "1":
                default_path = "data/inventory_export.json"
                file_path = prompt_string("Export JSON file path", default=default_path)
                count = self.service.export_to_json(file_path)
                print_success(f"Successfully exported {count} product(s) to '{file_path}'!")
            elif choice == "2":
                file_path = prompt_string("Import JSON file path", min_len=1)
                result = self.service.import_from_json(file_path)
                print_success(f"Import completed! Added: {result['created']} record(s), Skipped/Duplicates: {result['skipped']}.")
            elif choice == "3":
                return
            else:
                print_error("Invalid selection.")
        except (ValidationError, StorageError) as e:
            print_error(str(e))
