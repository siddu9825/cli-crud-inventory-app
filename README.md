# InventoCLI — Enterprise Inventory & Product Management CLI

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture: Clean](https://img.shields.io/badge/Architecture-Clean%20%2F%20Layered-emerald.svg)](#architecture--design-patterns)
[![Tests: Passing](https://img.shields.io/badge/Tests-34%2F34%20Passing-brightgreen.svg)](#automated-unit-testing)

A professional, menu-driven **Command Line Interface (CLI)** application implementing complete **CRUD (Create, Read, Update, Delete)** operations with persistent SQLite storage, multi-criteria search, rigorous input validation, custom domain exception handling, and clean modular layered architecture.

Developed for **Week 1: Task 1 – Build a CLI Application with CRUD Operations**.

---

## Table of Contents

- [Overview & Objectives](#overview--objectives)
- [Key Features](#key-features)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [CLI Walkthrough & CRUD Operations](#cli-walkthrough--crud-operations)
  - [1. Add Product (Create)](#1-add-product-create)
  - [2. View All Products (Read)](#2-view-all-products-read)
  - [3. Search Products (Multi-Criteria)](#3-search-products-multi-criteria)
  - [4. View Product Details (Read Specific)](#4-view-product-details-read-specific)
  - [5. Update Product (Update)](#5-update-product-update)
  - [6. Delete Product (Delete)](#6-delete-product-delete)
  - [7. Inventory Analytics & Low-Stock Alerts](#7-inventory-analytics--low-stock-alerts)
  - [8. Data Portability (Export / Import JSON)](#8-data-portability-export--import-json)
- [Input Validation & Exception Handling](#input-validation--exception-handling)
- [Automated Unit Testing](#automated-unit-testing)
- [GitHub Submission & Release Guide](#github-submission--release-guide)
- [Learning Outcomes](#learning-outcomes)
- [License](#license)

---

## Overview & Objectives

The primary objective of this project is to construct an enterprise-grade CLI application demonstrating fundamental software engineering principles:
- **Menu-Driven Interface**: Intuitive navigation with numeric menus, clear status messages, formatted tables, and interactive prompts.
- **Complete CRUD Lifecycle**: Create new records, read formatted rosters and individual detail cards, update fields with default preservation, and safely delete records with confirmation prompts.
- **Persistent Storage**: Robust data persistence powered by **SQLite** with ACID guarantees, indexed lookups, and JSON export/import data portability.
- **Search & Filter Engine**: Comprehensive search by keywords (SKU, title, description), category filters, price range boundaries, and stock health alerts.
- **Defensive Input Validation**: Enforced at both the presentation layer (prompt loops) and domain layer (invariants).
- **Graceful Error Handling**: Custom exception hierarchy preventing crashes, handling database locking, integrity violations, and `Ctrl+C` interrupts.
- **Zero Third-Party Dependencies**: Runs directly on any modern Python 3.10+ standard library.

---

## Key Features

| Feature | Implementation Highlights |
| :--- | :--- |
| **Interactive Menu** | Numeric menu (1–9) with ANSI color indicators, borders, and confirmation prompts. |
| **Full CRUD** | Create, Read (Table + Detailed Card), Update (field-level with defaults), and Delete with safety checks. |
| **Persistence** | Embedded SQLite database (`data/inventory.db`) with automatic schema initialization and indexes. |
| **Advanced Search** | Keyword wildcard matching (`LIKE %query%`), category exact filtering, price range limits, and low-stock queries. |
| **Business Analytics** | Real-time calculation of total valuation, stock volume, average unit price, and low-stock reorder warnings. |
| **Data Portability** | Full JSON backup export and import with duplicate SKU skipping and schema validation. |
| **Input Validation** | Type enforcement (floats, integers), positive price constraints ($> 0$), non-negative quantities ($\ge 0$), SKU uniqueness. |
| **Exception Handling** | Domain-specific exceptions (`ProductNotFoundError`, `DuplicateSKUError`, `ValidationError`, `StorageError`). |
| **Clean Architecture** | Strict separation of concerns between Domain, Repository, Service, and CLI layers. |

---

## Architecture & Design Patterns

The project follows **Clean Architecture** principles and the **Repository Pattern**:

```
┌────────────────────────────────────────────────────────┐
│                   Presentation / CLI                   │
│        (menu.py, views.py, validators.py)              │
└───────────────────────────┬────────────────────────────┘
                            │ Calls
┌───────────────────────────▼────────────────────────────┐
│                      Service Layer                     │
│                 (inventory_service.py)                 │
│      - Business Rules, Metrics, Orchestration          │
└─────────────┬────────────────────────────┬─────────────┘
              │ Implements                 │ Uses
┌─────────────▼─────────────┐ ┌────────────▼─────────────┐
│      Repository Layer     │ │       Domain Layer       │
│    (base.py, sqlite_repo) │ │ (models.py, exceptions)  │
│  - SQLite persistence     │ │ - Entity Invariants      │
│  - Query Construction     │ │ - Dataclass validation   │
└───────────────────────────┘ └──────────────────────────┘
```

1. **Domain Layer (`domain/`)**: Pure domain logic and models (`Product` dataclass) with no external framework dependencies. All invariants (e.g. positive pricing, minimum SKU length) are enforced here.
2. **Repository Layer (`repository/`)**: Defines the abstract storage contract (`BaseProductRepository`) and provides the concrete `SQLiteProductRepository` with parameterized SQL queries to prevent injection.
3. **Service Layer (`service/`)**: Houses core business rules, SKU uniqueness checks, multi-parameter search logic, analytical metrics calculations, and JSON export/import routines.
4. **Presentation Layer (`cli/`)**: Handles terminal input/output, interactive retry loops, table rendering, ANSI colors, and menu routing.

---

## Directory Structure

```
cli-crud-inventory-app/
├── inventory_cli/
│   ├── __init__.py                 # Package version declaration (v1.0.0)
│   ├── main.py                     # Entry point & CLI argument parser
│   ├── domain/
│   │   ├── __init__.py             # Domain exports
│   │   ├── models.py               # Product dataclass & invariant validation
│   │   └── exceptions.py           # Custom exception hierarchy
│   ├── repository/
│   │   ├── __init__.py             # Repository exports
│   │   ├── base.py                 # Abstract BaseProductRepository interface
│   │   └── sqlite_repo.py          # SQLite repository implementation
│   ├── service/
│   │   ├── __init__.py             # Service exports
│   │   └── inventory_service.py    # InventoryService business logic
│   └── cli/
│       ├── __init__.py             # CLI exports
│       ├── menu.py                 # Main menu controller & interaction loop
│       ├── views.py                # ANSI tables, cards, & dashboards
│       └── validators.py           # Robust input prompt validators
├── tests/
│   ├── __init__.py
│   ├── test_models.py              # Domain model & invariant tests
│   ├── test_repository.py          # SQLite repository integration tests
│   ├── test_service.py             # Service layer & business rule tests
│   └── test_validators.py          # Input parser & validation tests
├── data/
│   └── .gitkeep                    # Tracks data directory for SQLite & exports
├── .gitignore                      # Python, SQLite, and IDE ignore patterns
├── LICENSE                         # MIT License
├── requirements.txt                # Zero runtime dependencies (pytest optional)
└── README.md                       # Comprehensive system documentation
```

---

## Getting Started

### Prerequisites
- **Python 3.10** or higher.
- Standard terminal (macOS Terminal, iTerm2, Linux Shell, or Windows PowerShell/WSL).
- Git.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/cli-crud-inventory-app.git
   cd cli-crud-inventory-app
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Note on dependencies:
   > [!NOTE]
   > The application utilizes **only the Python standard library** (`sqlite3`, `dataclasses`, `typing`, `json`, `argparse`). No `pip install` is required to run the application!

---

### Running the Application

Launch the interactive CLI:
```bash
python3 -m inventory_cli.main
```

#### CLI Options
```text
usage: main.py [-h] [--db DB] [--no-seed]

InventoCLI - Enterprise Command Line Inventory Management System

options:
  -h, --help  show this help message and exit
  --db DB     Path to SQLite database file (default: data/inventory.db)
  --no-seed   Do not seed sample products if database is empty
```

---

## CLI Walkthrough & CRUD Operations

### 1. Add Product (Create)
Allows adding a new product with continuous field-level validation:
```text
▶ ADD NEW PRODUCT
Product SKU (e.g. LAP-001): LAP-001
Product Name: MacBook Pro 16
Category (e.g. Electronics, Office, Apparel): Electronics
Unit Price ($): 2499.00
Initial Stock Quantity: 12
Low Stock Alert Threshold [5]: 5
Product Description (optional): M3 Max chip, 36GB RAM, 1TB SSD
✔ Product 'MacBook Pro 16' (SKU: LAP-001) created successfully with ID 1!
```

### 2. View All Products (Read)
Renders a dynamically-sized, aligned ASCII table displaying product rosters and stock health:
```text
+----+---------+--------------------------+-------------+-----------+-----+-----------+-----------+
| ID | SKU     | Name                     | Category    | Price ($) | Qty | Threshold | Status    |
+----+---------+--------------------------+-------------+-----------+-----+-----------+-----------+
|  1 | LAP-001 | MacBook Pro 16           | Electronics |  2,499.00 |  12 |         5 | IN STOCK  |
|  2 | KEY-002 | Mechanical Keyboard      | Accessories |    129.50 |   3 |         5 | LOW STOCK |
|  3 | MON-003 | 4K Ultra-wide Monitor    | Electronics |    699.99 |   8 |         4 | IN STOCK  |
|  4 | DSK-004 | Ergonomic Standing Desk  | Furniture   |    450.00 |   2 |         3 | LOW STOCK |
|  5 | MOU-005 | Wireless Precision Mouse | Accessories |     89.90 |  25 |        10 | IN STOCK  |
+----+---------+--------------------------+-------------+-----------+-----+-----------+-----------+
Total rows: 5
```

### 3. Search Products (Multi-Criteria)
Offers 4 targeted search modalities:
- **Keyword Search**: Substring matches across SKU, Name, or Description.
- **Category Filter**: Case-insensitive category grouping.
- **Low-Stock Alert Filter**: Instantly surfaces items requiring inventory restocking (`quantity <= min_stock_threshold`).
- **Price Range Filter**: Finds products bounded within minimum and maximum dollar amounts.

### 4. View Product Details (Read Specific)
Accepts either numeric Product ID or SKU code and renders a detailed card:
```text
┌──────────────────────────────────────────────────────────────┐
│               PRODUCT SPECIFICATION: LAP-001                 │
├──────────────────────────────────────────────────────────────┤
│  Database ID         : 1                                     │
│  SKU Code            : LAP-001                               │
│  Product Name        : MacBook Pro 16                        │
│  Category            : Electronics                           │
│  Unit Price          : $2,499.00                             │
│  Stock On Hand       : 12 units                              │
│  Reorder Threshold   : 5 units                               │
│  Stock Status        : IN STOCK (OPTIMAL)                    │
│  Inventory Value     : $29,988.00                            │
│  Description         : M3 Max chip, 36GB RAM, 1TB SSD        │
│  Created At (UTC)    : 2026-10-02T12:49:33.725887+00:00      │
│  Updated At (UTC)    : 2026-10-02T12:49:33.725887+00:00      │
└──────────────────────────────────────────────────────────────┘
```

### 5. Update Product (Update)
Allows selective modification of fields. Hitting `[Enter]` on any field retains the current value:
```text
Editing product: MacBook Pro 16 (SKU: LAP-001)
Hint: Press [Enter] on any field to keep its current value.

Product SKU [LAP-001]: [Enter]
Product Name [MacBook Pro 16]: MacBook Pro 16 (M3 Max)
Category [Electronics]: [Enter]
Unit Price ($) [2499.0]: 2399.00
Stock Quantity [12]: 15
Low Stock Threshold [5]: [Enter]
Description [M3 Max chip...]: [Enter]
✔ Product 'MacBook Pro 16 (M3 Max)' (SKU: LAP-001) updated successfully!
```

### 6. Delete Product (Delete)
Deletes by ID or SKU with explicit confirmation to prevent accidental loss:
```text
Enter Product ID or SKU to delete: LAP-001
▲ Target: [LAP-001] MacBook Pro 16 (Stock: 15, Value: $35,985.00)
Are you sure you want to permanently delete this product? [y/N]: y
✔ Product 'MacBook Pro 16' (SKU: LAP-001) has been deleted.
```

### 7. Inventory Analytics & Low-Stock Alerts
Computes aggregate warehouse metrics:
```text
======================================================================
                   INVENTORY ANALYTICS & METRICS                     
======================================================================
  • Total Product Lines:     5
  • Total Stock Units:       50
  • Total Inventory Value:   $39,123.92
  • Average Unit Price:      $773.68
  • Active Categories:       3 (Accessories, Electronics, Furniture)
  • Low Stock Attention:     2 item(s) need replenishment!

Items below minimum threshold:
    - [KEY-002] Mechanical Keyboard: 3 in stock (threshold: 5)
    - [DSK-004] Ergonomic Standing Desk: 2 in stock (threshold: 3)
======================================================================
```

### 8. Data Portability (Export / Import JSON)
Export entire inventory states or import backups with automated conflict resolution:
- **Export**: Generates timestamped JSON snapshots to any custom or default path (`data/inventory_export.json`).
- **Import**: Parses JSON files, auto-assigns fresh primary keys, and skips duplicate SKU collisions gracefully.

---

## Input Validation & Exception Handling

### Input Validation Matrix

| Field | Rule / Validation Constraint | Error Triggered |
| :--- | :--- | :--- |
| **SKU** | Required, trimmed, uppercase, minimum 3 chars, globally unique | `ValidationError`, `DuplicateSKUError` |
| **Name** | Required, non-empty, trimmed string | `ValidationError` |
| **Category** | Required, non-empty string | `ValidationError` |
| **Price** | Required, positive decimal number ($> 0.00$) | `ValidationError` |
| **Quantity** | Required, non-negative integer ($\ge 0$) | `ValidationError` |
| **Threshold** | Non-negative integer ($\ge 0$, default: 5) | `ValidationError` |
| **Search Range** | $\text{Min Price} \le \text{Max Price}$ | `ValidationError` |

### Custom Exception Hierarchy

```
InventoryError (Base Exception)
├── ProductNotFoundError (Lookup by ID or SKU returned empty)
├── DuplicateSKUError    (SKU uniqueness conflict in DB)
├── ValidationError      (Invariants or domain validation failure)
└── StorageError         (Database disk I/O, lock, or corrupt connection)
```

- **Keyboard Interrupt (`Ctrl+C`)**: Intercepted cleanly at the event loop, giving users the option to confirm exit or return to the menu without unhandled Python tracebacks.

---

## Automated Unit Testing

The project includes **34 comprehensive unit tests** testing all layers:
- **Domain Tests** (`tests/test_models.py`): Invariants, constraints, edge cases, properties, and dictionary serialization.
- **Repository Tests** (`tests/test_repository.py`): SQLite schema initialization, indices, CRUD operations, transactions, and search queries against in-memory SQLite.
- **Service Tests** (`tests/test_service.py`): Business logic, uniqueness checks, metric aggregations, and JSON export/import.
- **Validator Tests** (`tests/test_validators.py`): Stdin simulation testing input loops, invalid entries, bounds, and fallback defaults.

### Running the Test Suite

Run tests via Python's built-in `unittest` runner:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Output:
```text
test_low_stock_property (test_models.TestProductModel.test_low_stock_property) ... ok
test_name_and_category_validation (test_models.TestProductModel.test_name_and_category_validation) ... ok
test_price_validation (test_models.TestProductModel.test_price_validation) ... ok
test_quantity_and_threshold_validation (test_models.TestProductModel.test_quantity_and_threshold_validation) ... ok
test_serialization (test_models.TestProductModel.test_serialization) ... ok
test_sku_validation (test_models.TestProductModel.test_sku_validation) ... ok
test_valid_product_creation (test_models.TestProductModel.test_valid_product_creation) ... ok
test_count_and_categories (test_repository.TestSQLiteProductRepository.test_count_and_categories) ... ok
test_create_and_get_by_id (test_repository.TestSQLiteProductRepository.test_create_and_get_by_id) ... ok
test_delete_product (test_repository.TestSQLiteProductRepository.test_delete_product) ... ok
test_duplicate_sku_raises_error (test_repository.TestSQLiteProductRepository.test_duplicate_sku_raises_error) ... ok
test_get_by_sku_case_insensitive (test_repository.TestSQLiteProductRepository.test_get_by_sku_case_insensitive) ... ok
test_list_all_and_sorting (test_repository.TestSQLiteProductRepository.test_list_all_and_sorting) ... ok
test_search_filters (test_repository.TestSQLiteProductRepository.test_search_filters) ... ok
test_update_product (test_repository.TestSQLiteProductRepository.test_update_product) ... ok
test_add_and_get_product (test_service.TestInventoryService.test_add_and_get_product) ... ok
test_add_duplicate_sku_raises_error (test_service.TestInventoryService.test_add_duplicate_sku_raises_error) ... ok
test_delete_product (test_service.TestInventoryService.test_delete_product) ... ok
test_get_nonexistent_product_raises_error (test_service.TestInventoryService.test_get_nonexistent_product_raises_error) ... ok
test_inventory_analytics (test_service.TestInventoryService.test_inventory_analytics) ... ok
test_json_export_and_import (test_service.TestInventoryService.test_json_export_and_import) ... ok
test_search_price_range_validation (test_service.TestInventoryService.test_search_price_range_validation) ... ok
test_update_duplicate_sku_collision (test_service.TestInventoryService.test_update_duplicate_sku_collision) ... ok
test_update_product_partial_fields (test_service.TestInventoryService.test_update_product_partial_fields) ... ok
test_prompt_choice (test_validators.TestValidators.test_prompt_choice) ... ok
test_prompt_confirm_default (test_validators.TestValidators.test_prompt_confirm_default) ... ok
test_prompt_confirm_no (test_validators.TestValidators.test_prompt_confirm_no) ... ok
test_prompt_confirm_yes (test_validators.TestValidators.test_prompt_confirm_yes) ... ok
test_prompt_float_allow_blank (test_validators.TestValidators.test_prompt_float_allow_blank) ... ok
test_prompt_float_with_min (test_validators.TestValidators.test_prompt_float_with_min) ... ok
test_prompt_int_retry_on_float (test_validators.TestValidators.test_prompt_int_retry_on_float) ... ok
test_prompt_string_default (test_validators.TestValidators.test_prompt_string_default) ... ok
test_prompt_string_empty_retry (test_validators.TestValidators.test_prompt_string_empty_retry) ... ok
test_prompt_string_normal (test_validators.TestValidators.test_prompt_string_normal) ... ok

----------------------------------------------------------------------
Ran 34 tests in 0.017s

OK
```

---

## GitHub Submission & Release Guide

Follow these steps to submit your project and create the mandatory GitHub Release:

### Step 1: Push Local Code to GitHub

1. Create a new public repository on [GitHub](https://github.com/new) named `cli-crud-inventory-app`.
2. Connect your local repository and push:
   ```bash
   # Add remote
   git remote add origin https://github.com/<YOUR_USERNAME>/cli-crud-inventory-app.git

   # Rename branch to main
   git branch -M main

   # Push commits and tag
   git push -u origin main --tags
   ```

### Step 2: Create the GitHub Release (Mandatory)

#### Option A: Using the GitHub Web Interface
1. Go to your repository on GitHub: `https://github.com/<YOUR_USERNAME>/cli-crud-inventory-app`.
2. In the right-hand sidebar, click **Releases** (or navigate to `https://github.com/<YOUR_USERNAME>/cli-crud-inventory-app/releases/new`).
3. Click **Draft a new release**.
4. Choose the existing tag: **`v1.0.0`** (or create tag `v1.0.0` on `main`).
5. Set Release Title: `v1.0.0 - Production CLI CRUD Application`.
6. Add Release Notes:
   ```markdown
   ## InventoCLI v1.0.0 Release

   ### Highlights
   - Full CRUD operations with menu-driven CLI interface.
   - Persistent SQLite backend with parameterized queries and index optimization.
   - Multi-criteria search (keyword, category, price range, stock alert).
   - Robust input validation and custom domain exceptions.
   - Real-time inventory analytics and valuation reports.
   - JSON export and import capabilities.
   - 34 automated unit tests with 100% pass rate.
   ```
7. Click **Publish release**.

#### Option B: Using GitHub CLI (`gh`)
If logged in via `gh auth login`:
```bash
gh release create v1.0.0 \
  --title "v1.0.0 - Production CLI CRUD Application" \
  --notes "Complete Menu-driven CRUD CLI application with SQLite persistence, search, input validation, and unit tests."
```

### Step 3: Submission URLs
Submit both URLs as required:
- **Repository URL**: `https://github.com/<YOUR_USERNAME>/cli-crud-inventory-app`
- **GitHub Release URL**: `https://github.com/<YOUR_USERNAME>/cli-crud-inventory-app/releases/tag/v1.0.0`

---

## Learning Outcomes

By building and completing this project, the following core software engineering and development disciplines were demonstrated:

1. **CLI Development**: Interactive text user interfaces, terminal ANSI styling, and navigation event loops.
2. **CRUD Operations**: Complete data lifecycle management with transactional safety.
3. **Data Persistence**: Relational schema design, SQL index optimization, and JSON serialization.
4. **Error Handling**: Graceful exception propagation, domain boundary validation, and user interrupt handling.
5. **Git & GitHub Workflows**: Clean commit history, semantic versioning tags (`v1.0.0`), and GitHub Releases.
6. **Software Engineering Best Practices**: Layered architecture, dependency injection, and comprehensive unit testing.

---

## License

This project is licensed under the [MIT License](LICENSE).
