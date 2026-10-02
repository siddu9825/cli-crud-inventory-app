"""CLI presentation views, table formatters, and dashboard display."""

from typing import List, Dict, Any, Optional
from ..domain.models import Product

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

def render_banner() -> None:
    """Print welcoming CLI banner."""
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}          INVENTOCLI - ENTERPRISE INVENTORY MANAGEMENT SYSTEM         {RESET}")
    print(f"{DIM}              Modular CRUD CLI Application • SQLite Persistence       {RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")

def render_products_table(products: List[Product], title: Optional[str] = None) -> None:
    """Render a formatted, aligned ASCII table of products."""
    if title:
        print(f"\n{BOLD}{BLUE}▶ {title} ({len(products)} record{'s' if len(products) != 1 else ''}){RESET}")

    if not products:
        print(f"{YELLOW}No records found.{RESET}\n")
        return

    headers = ["ID", "SKU", "Name", "Category", "Price ($)", "Qty", "Threshold", "Status"]

    rows = []
    for p in products:
        status_str = f"{RED}LOW STOCK{RESET}" if p.is_low_stock else f"{GREEN}IN STOCK{RESET}"
        rows.append([
            str(p.id) if p.id else "-",
            p.sku,
            p.name[:25] + ("..." if len(p.name) > 25 else ""),
            p.category[:15] + ("..." if len(p.category) > 15 else ""),
            f"{p.price:,.2f}",
            str(p.quantity),
            str(p.min_stock_threshold),
            status_str,
        ])

    # Visible length helper (ignoring ANSI escape codes for width calculation)
    def visible_len(s: str) -> int:
        clean = s.replace(RED, "").replace(GREEN, "").replace(RESET, "").replace(BOLD, "")
        return len(clean)

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], visible_len(val))

    # Construct border lines
    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    print(separator)
    print(f"{BOLD}{header_line}{RESET}")
    print(separator)

    for row in rows:
        formatted_cols = []
        for i, val in enumerate(row):
            padding = col_widths[i] - visible_len(val)
            # Right align numeric columns (ID, Price, Qty, Threshold)
            if i in (0, 4, 5, 6):
                formatted_cols.append(" " * padding + val)
            else:
                formatted_cols.append(val + " " * padding)
        print("| " + " | ".join(formatted_cols) + " |")

    print(separator)
    print(f"{DIM}Total rows: {len(products)}{RESET}\n")

def render_product_detail(p: Product) -> None:
    """Render full detailed product card."""
    status_str = f"{RED}{BOLD}LOW STOCK ALERT{RESET}" if p.is_low_stock else f"{GREEN}IN STOCK (OPTIMAL){RESET}"
    box_width = 64

    print(f"\n{BOLD}{CYAN}┌" + "─" * (box_width - 2) + "┐" + f"{RESET}")
    title = f" PRODUCT SPECIFICATION: {p.sku} "
    print(f"{BOLD}{CYAN}│{RESET}{BOLD}{title.center(box_width - 2)}{RESET}{BOLD}{CYAN}│{RESET}")
    print(f"{BOLD}{CYAN}├" + "─" * (box_width - 2) + "┤" + f"{RESET}")

    def render_row(label: str, val: str) -> None:
        content = f"  {BOLD}{label.ljust(20)}:{RESET} {val}"
        # compute visible length
        clean = content.replace(BOLD, "").replace(RESET, "").replace(RED, "").replace(GREEN, "").replace(YELLOW, "")
        pad = box_width - 2 - len(clean)
        print(f"{BOLD}{CYAN}│{RESET}{content}{' ' * max(0, pad)}{BOLD}{CYAN}│{RESET}")

    render_row("Database ID", str(p.id))
    render_row("SKU Code", p.sku)
    render_row("Product Name", p.name)
    render_row("Category", p.category)
    render_row("Unit Price", f"${p.price:,.2f}")
    render_row("Stock On Hand", f"{p.quantity} units")
    render_row("Reorder Threshold", f"{p.min_stock_threshold} units")
    render_row("Stock Status", status_str)
    render_row("Inventory Value", f"${p.total_value:,.2f}")
    render_row("Description", p.description if p.description else f"{DIM}(None provided){RESET}")
    render_row("Created At (UTC)", p.created_at)
    render_row("Updated At (UTC)", p.updated_at)

    print(f"{BOLD}{CYAN}└" + "─" * (box_width - 2) + "┘" + f"{RESET}\n")

def render_analytics_dashboard(metrics: Dict[str, Any]) -> None:
    """Render inventory analytics and metrics overview."""
    print(f"\n{BOLD}{MAGENTA}======================================================================{RESET}")
    print(f"{BOLD}{MAGENTA}                   INVENTORY ANALYTICS & METRICS                     {RESET}")
    print(f"{BOLD}{MAGENTA}======================================================================{RESET}")

    print(f"  • {BOLD}Total Product Lines:{RESET}     {metrics['total_products']:,}")
    print(f"  • {BOLD}Total Stock Units:{RESET}       {metrics['total_units']:,}")
    print(f"  • {BOLD}Total Inventory Value:{RESET}   {GREEN}${metrics['total_valuation']:,.2f}{RESET}")
    print(f"  • {BOLD}Average Unit Price:{RESET}      ${metrics['average_price']:,.2f}")
    print(f"  • {BOLD}Active Categories:{RESET}       {metrics['category_count']} ({', '.join(metrics['categories']) if metrics['categories'] else 'None'})")

    low_stock_count = metrics['low_stock_count']
    if low_stock_count > 0:
        print(f"  • {BOLD}Low Stock Attention:{RESET}     {RED}{BOLD}{low_stock_count} item(s) need replenishment!{RESET}")
        print(f"\n{YELLOW}{BOLD}Items below minimum threshold:{RESET}")
        for item in metrics["low_stock_items"]:
            print(f"    - [{item.sku}] {item.name}: {RED}{item.quantity} in stock{RESET} (threshold: {item.min_stock_threshold})")
    else:
        print(f"  • {BOLD}Stock Health:{RESET}            {GREEN}All products are above minimum threshold.{RESET}")

    print(f"{BOLD}{MAGENTA}======================================================================{RESET}\n")
