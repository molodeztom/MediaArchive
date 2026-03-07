# Project Structure

This document defines the complete directory structure and key files for the Media Archive Manager application.

## Directory Tree

```
MediaArchive/
├── src/                           # Source code root
│   ├── __init__.py
│   ├── gui/                       # GUI layer (tkinter)
│   │   ├── __init__.py
│   │   ├── main_window.py        # Main application window
│   │   ├── media_form.py         # Add/Edit media dialog
│   │   ├── search_panel.py       # Search interface
│   │   ├── location_dialog.py    # Storage location management
│   │   └── widgets/              # Custom widgets
│   │       ├── __init__.py
│   │       └── media_table.py    # Media list table widget
│   │
│   ├── business/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── media_service.py      # Media CRUD operations
│   │   ├── location_service.py   # Location management
│   │   ├── search_service.py     # Search and filter logic
│   │   ├── validation.py         # Input validation
│   │   └── export_service.py     # CSV import/export
│   │
│   ├── data/                      # Data access layer
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection manager
│   │   ├── media_repository.py   # Media table operations
│   │   ├── location_repository.py # Location table operations
│   │   └── schema.py             # Database schema definition
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── media.py              # Media entity
│   │   ├── location.py           # StorageLocation entity
│   │   └── enums.py              # MediaType enum
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── date_utils.py         # Date formatting and validation
│       └── config.py             # Application configuration
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_media_service.py
│   ├── test_location_service.py
│   ├── test_search_service.py
│   ├── test_repositories.py
│   └── test_validation.py
│
├── data/                          # Database and data files
│   ├── .gitkeep                  # Keep directory in git
│   └── media_archive.db          # SQLite database (gitignored)
│
├── docs/                          # Documentation
│   ├── PROJECT_OVERVIEW.md       # Application overview
│   ├── DATA_MODEL.md             # Database schema
│   ├── UI_WORKFLOW.md            # UI design and workflows
│   ├── DEV_RULES.md              # Development guidelines
│   ├── TASKS.md                  # Implementation roadmap
│   └── PROJECT_STRUCTURE.md      # This file
│
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── main.py                        # Application entry point
└── README.md                      # Project readme
```

## Key Files Description

### Root Level

- **main.py**: Application entry point that initializes the database and launches the GUI
- **requirements.txt**: Python package dependencies (minimal)
- **.gitignore**: Excludes database files, Python cache, and IDE files
- **README.md**: Project overview and quick start guide

### Source Code (src/)

#### GUI Layer (src/gui/)
- **main_window.py**: Main application window with menu bar, toolbar, and media list
- **media_form.py**: Dialog for adding/editing media records
- **search_panel.py**: Search and filter interface
- **location_dialog.py**: Dialog for managing storage locations
- **widgets/media_table.py**: Custom table widget for displaying media list

#### Business Logic Layer (src/business/)
- **media_service.py**: Business logic for media operations (CRUD, validation)
- **location_service.py**: Business logic for storage location management
- **search_service.py**: Search, filter, and query logic
- **validation.py**: Input validation rules
- **export_service.py**: CSV import/export functionality

#### Data Access Layer (src/data/)
- **database.py**: SQLite connection manager and initialization
- **media_repository.py**: Database operations for media table
- **location_repository.py**: Database operations for storage_location table
- **schema.py**: SQL schema definitions and migrations

#### Models (src/models/)
- **media.py**: Media entity class with properties
- **location.py**: StorageLocation entity class
- **enums.py**: MediaType enumeration

#### Utilities (src/utils/)
- **date_utils.py**: Date formatting and validation helpers
- **config.py**: Application configuration (database path, etc.)

### Tests (tests/)
Unit and integration tests for business logic and data access layers.

### Data (data/)
Contains the SQLite database file (excluded from version control).

### Documentation (docs/)
Comprehensive project documentation (this folder).

## File Creation Order

When implementing, create files in this order:

1. **Setup files**: requirements.txt, .gitignore
2. **Models**: enums.py, location.py, media.py
3. **Data layer**: schema.py, database.py, repositories
4. **Business layer**: services and validation
5. **GUI layer**: widgets, dialogs, main window
6. **Entry point**: main.py
7. **Tests**: test files

## Dependencies

The application uses minimal external dependencies:

- **Python 3.10+**: Core language
- **tkinter**: GUI framework (built-in)
- **sqlite3**: Database (built-in)
- **csv**: Import/export (built-in)
- **datetime**: Date handling (built-in)
- **typing**: Type hints (built-in)

No external packages required for core functionality.
