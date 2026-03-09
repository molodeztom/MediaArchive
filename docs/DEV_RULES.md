# Development Rules and Guidelines

## Overview

This document defines coding standards, best practices, and development guidelines for the Media Archive Manager project. Following these rules ensures code quality, maintainability, and consistency.
### Mandatory Rule for AI Agents

Any AI coding agent working in this project must read and follow this file before making code changes.

The agent must prioritize:
- minimal changes
- preserving working code
- simple solutions
- incremental implementation
- low dependency count
- stable project structure

The goal is not maximum architectural sophistication, but a small, reliable, maintainable local desktop application.

## Python Version

- **Minimum**: Python 3.10
- **Recommended**: Python 3.11 or 3.12
- **Reason**: Modern type hints, pattern matching, better performance

## Code Style

### PEP 8 Compliance

Follow [PEP 8](https://pep8.org/) style guide with these specifics:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Line endings**: LF (Unix style)

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Module | lowercase_with_underscores | `media_service.py` |
| Class | PascalCase | `MediaService` |
| Function | lowercase_with_underscores | `get_media_by_id()` |
| Variable | lowercase_with_underscores | `media_list` |
| Constant | UPPERCASE_WITH_UNDERSCORES | `MAX_NAME_LENGTH` |
| Private | _leading_underscore | `_validate_input()` |

### Import Organization

Order imports in three groups, separated by blank lines:

```python
# 1. Standard library imports
import sqlite3
from datetime import datetime
from typing import Optional, List

# 2. Third-party imports (if any)
# import external_library

# 3. Local application imports
from models.media import Media
from data.database import Database
```

Use absolute imports, not relative imports.

## Type Hints

### Required Type Hints

Use type hints for all function signatures:

```python
def get_media_by_id(media_id: int) -> Optional[Media]:
    """Retrieve media by ID."""
    pass

def search_media(query: str, search_in: str = "name") -> List[Media]:
    """Search media by query."""
    pass
```

### Type Hint Guidelines

- Use `Optional[T]` for nullable values
- Use `List[T]`, `Dict[K, V]` for collections
- Use `None` as return type for procedures
- Use `-> bool` for validation functions
- Use type aliases for complex types:

```python
from typing import TypeAlias

MediaDict: TypeAlias = dict[str, str | int | None]
```

## Documentation

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def create_media(name: str, media_type: str, location_id: Optional[int] = None) -> Media:
    """Create a new media record.
    
    Args:
        name: The name of the media (required).
        media_type: Type of media (e.g., 'DVD', 'M-Disk').
        location_id: Optional storage location ID.
    
    Returns:
        The newly created Media object.
    
    Raises:
        ValueError: If name is empty or media_type is invalid.
        DatabaseError: If database operation fails.
    
    Example:
        >>> media = create_media("Windows 11", "DVD", location_id=1)
        >>> print(media.name)
        Windows 11
    """
    pass
```

### Comments

- Use comments sparingly - code should be self-documenting
- Explain **why**, not **what**
- Use `# TODO:` for future improvements
- Use `# FIXME:` for known issues
- Use `# NOTE:` for important clarifications

```python
# Good comment - explains why
# Use SET NULL to preserve media records when location is deleted
FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL

# Bad comment - states the obvious
# Increment counter by 1
counter += 1
```

## Architecture Layers
## AI Agent Behaviour and Safety Rules

### General AI Rules

AI agents must follow these rules for every task:

1. Modify only the files necessary for the requested change.
2. Do not rewrite large working files unless explicitly required.
3. Do not restructure the project without explicit approval.
4. Do not rename or move files unless necessary.
5. Do not introduce new frameworks, layers, or abstractions unless explicitly requested.
6. Do not implement unrelated improvements while working on a specific task.
7. Preserve existing working functionality.
8. Prefer the simplest working solution.

## Project Scope Constraints

This application is intentionally limited in scope.

### Project Type

This is a:

- local desktop application
- single-user tool
- SQLite-based application
- low-maintenance private archive manager

### Explicit Non-Goals

The following are out of scope unless explicitly requested later:

- multi-user support
- web application
- browser-based UI
- Docker-first deployment
- cloud database backend
- user authentication system
- role/permission system
- remote API access
- mobile app support
- complex plugin systems

### Design Priority

Priority order:

1. correctness
2. maintainability
3. simplicity
4. readability
5. performance
6. extensibility

Do not trade simplicity for theoretical flexibility too early.

### Incremental Development

AI agents must implement changes in small, controlled phases.

Do not build the entire application in one step.

Preferred order:
1. project structure
2. database schema
3. minimal application startup
4. basic CRUD
5. search and filtering
6. additional views
7. export and backup helpers
8. optional future enhancements

### Large Change Protocol

Before significant changes, the AI agent should:

1. briefly explain what will be changed
2. list affected files
3. avoid unnecessary side effects
4. keep the change scope narrow

## GUI Simplicity Rules

- Prefer a clear and functional layout over visually complex design
- Use German labels in the GUI where appropriate for end-user usability
- Keep dialogs focused on one task
- Avoid hidden logic in UI callbacks
- Keep UI code separate from business and database logic
- Do not introduce complex reactive UI patterns

### Forbidden AI Behaviours

The AI agent must avoid:

- introducing web frameworks for this desktop project
- adding REST APIs or server components
- adding ORMs such as SQLAlchemy unless explicitly approved
- introducing cloud-only architecture
- splitting the project into overly complex package structures
- replacing simple direct SQL with unnecessary abstraction
- rewriting working modules for stylistic reasons only

## Forbidden Overengineering Patterns

The following patterns are explicitly forbidden unless the user requests them:

### Architecture Overengineering

❌ **Do NOT introduce:**
- Abstract factory patterns for simple object creation
- Strategy patterns for single-implementation logic
- Observer patterns for simple callbacks
- Command patterns for direct function calls
- Repository patterns with multiple abstraction layers
- Service locator patterns
- Dependency injection containers (simple constructor injection is fine)

✅ **Do use:**
- Direct instantiation where appropriate
- Simple inheritance when needed
- Constructor-based dependency injection
- Clear, straightforward function calls

### Database Overengineering

❌ **Do NOT introduce:**
- ORM frameworks (SQLAlchemy, Peewee, etc.)
- Database migration frameworks (Alembic, etc.)
- Query builders that hide SQL
- Multiple database abstraction layers
- Connection pooling for single-user desktop app
- Database versioning systems (for initial version)

✅ **Do use:**
- Direct SQLite3 module from standard library
- Parameterized SQL queries
- Simple schema.sql file
- Context managers for connections
- Transactions for multi-step operations

### GUI Overengineering

❌ **Do NOT introduce:**
- MVC/MVP/MVVM frameworks
- Reactive UI frameworks
- State management libraries
- Custom event bus systems
- Complex widget hierarchies
- UI component libraries beyond tkinter

✅ **Do use:**
- Simple tkinter widgets
- Direct event binding
- Clear callback functions
- Straightforward dialog classes
- Standard tkinter layout managers

### Code Organization Overengineering

❌ **Do NOT introduce:**
- Microservices architecture
- Plugin systems
- Dynamic module loading
- Complex package hierarchies (>3 levels deep)
- Separate packages for each class
- Abstract base classes without clear need

✅ **Do use:**
- Simple 3-layer architecture (GUI/Business/Data)
- Clear module organization
- Related classes in same file when appropriate
- Straightforward imports

## SQLite-Specific Implementation Rules

### Connection Management

**Rule**: Use a single connection per operation, managed by context manager.

```python
# Good - simple context manager
class Database:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection = None
    
    def connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

# Bad - complex connection pooling
# Do NOT implement connection pools for single-user desktop app
```

### Query Execution

**Rule**: Always use parameterized queries. Never concatenate user input.

```python
# Good - parameterized query
cursor.execute("SELECT * FROM media WHERE name LIKE ?", (f"%{search}%",))

# Bad - string concatenation (SQL injection risk)
cursor.execute(f"SELECT * FROM media WHERE name LIKE '%{search}%'")
```

### Transaction Handling

**Rule**: Use explicit transactions for multi-step operations.

```python
# Good - explicit transaction
try:
    conn.execute("BEGIN")
    conn.execute("INSERT INTO media (...) VALUES (?)", (data,))
    conn.execute("UPDATE storage_location SET count = count + 1 WHERE id = ?", (loc_id,))
    conn.commit()
except sqlite3.Error:
    conn.rollback()
    raise

# Bad - autocommit for multi-step operations
# (can lead to partial updates)
```

### Schema Management

**Rule**: Keep schema simple. Use a single schema.sql file.

```python
# Good - simple schema initialization
def init_schema(conn: sqlite3.Connection) -> None:
    """Initialize database schema from SQL file."""
    with open('src/data/schema.sql', 'r') as f:
        conn.executescript(f.read())

# Bad - complex migration framework
# Do NOT use Alembic or similar for initial version
```

### Data Types

**Rule**: Use SQLite's type affinity correctly.

| Python Type | SQLite Type | Notes |
|-------------|-------------|-------|
| int | INTEGER | Use for IDs, counts |
| str | TEXT | Use for strings |
| float | REAL | Use for decimals |
| bytes | BLOB | Avoid if possible |
| datetime | TEXT | Store as ISO 8601 string |
| date | TEXT | Store as ISO 8601 string (YYYY-MM-DD) |
| bool | INTEGER | Store as 0/1 |

```python
# Good - proper type handling
creation_date = row['creation_date']  # TEXT from database
if creation_date:
    date_obj = datetime.fromisoformat(creation_date)

# Bad - storing dates as integers (Unix timestamps)
# Harder to query and read
```

### Indexes

**Rule**: Add indexes only on columns used in WHERE, JOIN, or ORDER BY clauses.

```sql
-- Good - indexes on query columns
CREATE INDEX idx_media_name ON media(name);
CREATE INDEX idx_media_type ON media(media_type);
CREATE INDEX idx_media_location ON media(location_id);

-- Bad - indexes on every column
-- Slows down INSERT/UPDATE unnecessarily
```

### Foreign Keys

**Rule**: Enable foreign key constraints and use ON DELETE appropriately.

```python
# Good - enable foreign keys
conn.execute("PRAGMA foreign_keys = ON")

# Schema with proper foreign key
CREATE TABLE media (
    ...
    location_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL
);
```

### Full-Text Search

**Rule**: Do NOT implement FTS5 in initial version. Use simple LIKE queries.

```python
# Good - simple LIKE query for initial version
cursor.execute("SELECT * FROM media WHERE name LIKE ? OR content_description LIKE ?",
               (f"%{query}%", f"%{query}%"))

# Bad - premature FTS5 implementation
# Add only if simple search proves insufficient
```

### Database File Location

**Rule**: Store database in `data/` directory, never in system directories.

```python
# Good - local data directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "media_archive.db"

# Bad - system directories
# Do NOT use AppData, ProgramData, etc. in initial version
```

### Backup Strategy

**Rule**: Keep backup simple - just copy the .db file.

```python
# Good - simple file copy
import shutil
from datetime import datetime

def backup_database(db_path: Path, backup_dir: Path) -> Path:
    """Create a backup of the database file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"media_archive_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return backup_path

# Bad - complex backup systems with compression, encryption, etc.
# Keep it simple for initial version
```

### Performance Optimization

**Rule**: Optimize only when needed. Start simple.

```python
# Good - simple query first
cursor.execute("SELECT * FROM media WHERE name LIKE ?", (f"%{query}%",))

# If slow, then add index:
# CREATE INDEX idx_media_name ON media(name);

# Bad - premature optimization
# Do NOT add caching, query optimization, etc. before measuring
```

### Error Handling

**Rule**: Catch sqlite3.Error, not generic Exception.

```python
# Good - specific exception
try:
    cursor.execute("INSERT INTO media (...) VALUES (?)", (data,))
except sqlite3.IntegrityError as e:
    raise ValidationError(f"Duplicate entry: {e}")
except sqlite3.Error as e:
    raise DatabaseError(f"Database error: {e}")

# Bad - catching generic Exception
# Hides programming errors
```

### Layer Separation

Maintain strict separation between layers:

```
GUI Layer → Business Logic Layer → Data Access Layer → Database
```

**Rules:**
- GUI layer only calls business logic layer
- Business logic layer only calls data access layer
- Data access layer only interacts with database
- No layer skipping (GUI cannot call data access directly)
- No circular dependencies

### Dependency Injection

Pass dependencies through constructors:

```python
class MediaService:
    """Business logic for media operations."""
    
    def __init__(self, media_repository: MediaRepository):
        """Initialize service with repository dependency.
        
        Args:
            media_repository: Repository for media data access.
        """
        self._repository = media_repository
    
    def get_all_media(self) -> List[Media]:
        """Get all media records."""
        return self._repository.find_all()
```

## Error Handling

### Exception Hierarchy

Define custom exceptions:

```python
class MediaArchiveError(Exception):
    """Base exception for Media Archive application."""
    pass

class ValidationError(MediaArchiveError):
    """Raised when input validation fails."""
    pass

class DatabaseError(MediaArchiveError):
    """Raised when database operation fails."""
    pass

class NotFoundError(MediaArchiveError):
    """Raised when requested resource is not found."""
    pass
```

### Error Handling Guidelines

1. **Catch specific exceptions**, not generic `Exception`
2. **Log errors** before re-raising or handling
3. **Provide user-friendly messages** in GUI layer
4. **Clean up resources** using context managers
5. **Don't silently swallow exceptions**

```python
# Good error handling
def get_media_by_id(media_id: int) -> Media:
    """Get media by ID."""
    try:
        media = self._repository.find_by_id(media_id)
        if media is None:
            raise NotFoundError(f"Media with ID {media_id} not found")
        return media
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving media {media_id}: {e}")
        raise DatabaseError(f"Failed to retrieve media: {e}") from e
```

### GUI Error Display

Show user-friendly error messages:

```python
try:
    media_service.create_media(name, media_type)
    messagebox.showinfo("Success", "Media created successfully")
except ValidationError as e:
    messagebox.showerror("Validation Error", str(e))
except DatabaseError as e:
    messagebox.showerror("Database Error", "Failed to save media. Please try again.")
    logger.error(f"Database error: {e}")
```

## Data Validation

### Validation Rules

Validate all user input in the business logic layer:

```python
class MediaValidator:
    """Validates media data."""
    
    MAX_NAME_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 2000
    VALID_MEDIA_TYPES = ["M-Disk", "DVD", "CD", "Blu-ray", "USB Drive", 
                         "External HDD", "Backup Tape", "Other"]
    
    @staticmethod
    def validate_name(name: str) -> None:
        """Validate media name.
        
        Args:
            name: The name to validate.
        
        Raises:
            ValidationError: If name is invalid.
        """
        if not name or not name.strip():
            raise ValidationError("Name is required")
        if len(name) > MediaValidator.MAX_NAME_LENGTH:
            raise ValidationError(f"Name must be {MediaValidator.MAX_NAME_LENGTH} characters or less")
    
    @staticmethod
    def validate_media_type(media_type: str) -> None:
        """Validate media type.
        
        Args:
            media_type: The media type to validate.
        
        Raises:
            ValidationError: If media type is invalid.
        """
        if media_type not in MediaValidator.VALID_MEDIA_TYPES:
            raise ValidationError(f"Invalid media type: {media_type}")
```

### Input Sanitization

- **Trim whitespace** from all text inputs
- **Validate dates** before storing
- **Escape SQL** using parameterized queries (always)
- **Validate foreign keys** before saving

## Database Access

### Use Parameterized Queries

**Always** use parameterized queries to prevent SQL injection:

```python
# Good - parameterized query
def find_by_name(self, name: str) -> List[Media]:
    """Find media by name."""
    cursor = self._db.execute(
        "SELECT * FROM media WHERE name LIKE ?",
        (f"%{name}%",)
    )
    return [self._row_to_media(row) for row in cursor.fetchall()]

# Bad - string concatenation (NEVER DO THIS)
def find_by_name(self, name: str) -> List[Media]:
    cursor = self._db.execute(f"SELECT * FROM media WHERE name LIKE '%{name}%'")
    return [self._row_to_media(row) for row in cursor.fetchall()]
```

### Connection Management

Use context managers for database connections:

```python
class Database:
    """Database connection manager."""
    
    def __init__(self, db_path: str):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self.close()
```

### Transaction Management

Use transactions for multi-step operations:

```python
def import_media_batch(self, media_list: List[Media]) -> None:
    """Import multiple media records in a transaction.
    
    Args:
        media_list: List of media to import.
    
    Raises:
        DatabaseError: If import fails.
    """
    try:
        with self._db.connect() as conn:
            for media in media_list:
                self._repository.create(media)
            # Commit happens automatically on successful exit
    except sqlite3.Error as e:
        # Rollback happens automatically on exception
        raise DatabaseError(f"Failed to import media: {e}") from e
```

## Testing

### Test Structure

Organize tests to mirror source structure:

```
tests/
├── test_media_service.py
├── test_location_service.py
├── test_search_service.py
├── test_media_repository.py
└── test_validation.py
```

### Test Naming

Use descriptive test names:

```python
def test_create_media_with_valid_data_succeeds():
    """Test that creating media with valid data succeeds."""
    pass

def test_create_media_with_empty_name_raises_validation_error():
    """Test that creating media with empty name raises ValidationError."""
    pass

def test_search_media_by_name_returns_matching_results():
    """Test that searching by name returns matching media."""
    pass
```

### Test Guidelines

- **One assertion per test** (when possible)
- **Use fixtures** for common setup
- **Test edge cases** (empty strings, None, max length)
- **Test error conditions** (invalid input, database errors)
- **Use in-memory database** for data layer tests
- **Mock dependencies** for unit tests

```python
import unittest
from unittest.mock import Mock, MagicMock

class TestMediaService(unittest.TestCase):
    """Tests for MediaService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.service = MediaService(self.mock_repository)
    
    def test_get_all_media_returns_repository_results(self):
        """Test that get_all_media returns results from repository."""
        # Arrange
        expected_media = [Media(id=1, name="Test", media_type="DVD")]
        self.mock_repository.find_all.return_value = expected_media
        
        # Act
        result = self.service.get_all_media()
        
        # Assert
        self.assertEqual(result, expected_media)
        self.mock_repository.find_all.assert_called_once()
```

## Logging

### Logging Configuration

Use Python's built-in logging module:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('media_archive.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Logging Guidelines

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (recoverable issues)
- **ERROR**: Error messages (operation failed)
- **CRITICAL**: Critical errors (application may crash)

```python
logger.debug(f"Searching for media with query: {query}")
logger.info(f"Created new media: {media.name}")
logger.warning(f"Media {media_id} not found")
logger.error(f"Database error: {e}")
logger.critical(f"Failed to initialize database: {e}")
```

## Performance Guidelines

### Database Optimization

- **Use indexes** on frequently queried columns
- **Limit result sets** when appropriate
- **Use EXPLAIN QUERY PLAN** to optimize slow queries
- **Batch operations** when inserting multiple records
- **Run VACUUM** periodically to reclaim space

### GUI Performance

- **Load data asynchronously** for large datasets
- **Use virtual scrolling** for large tables
- **Debounce search input** (wait for user to stop typing)
- **Cache frequently accessed data**
- **Update UI incrementally** during long operations

## Security Guidelines

### Data Protection

- **No hardcoded credentials** (not applicable for local SQLite)
- **Validate all input** before processing
- **Use parameterized queries** (prevent SQL injection)
- **Sanitize file paths** for import/export
- **Handle sensitive data** (license codes) carefully

### File System Access

- **Validate file paths** before reading/writing
- **Check file permissions** before operations
- **Handle file not found** gracefully
- **Limit file size** for imports
- **Use safe file names** (no special characters)

## Git Workflow

### Commit Messages

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(media): add CSV import functionality

Implement CSV import for media records with validation
and error reporting.

Closes #12
```

```
fix(search): correct date range filter logic

Fixed issue where date range filter was not including
the end date in results.
```

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Feature branches (e.g., `feature/csv-import`)
- **bugfix/**: Bug fix branches (e.g., `bugfix/search-error`)

## Code Review Checklist

Before submitting code for review:

- [ ] Code follows PEP 8 style guide
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Input validation is implemented
- [ ] Error handling is appropriate
- [ ] Tests are written and passing
- [ ] No hardcoded values (use constants)
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Logging is appropriate
- [ ] Performance is acceptable
- [ ] Security considerations addressed

## Dependencies Management

### requirements.txt

Keep dependencies minimal. For this project:

```txt
# No external dependencies required for core functionality
# All features use Python standard library

# Development dependencies (optional)
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
mypy>=1.0.0
```

### Dependency Guidelines

- **Prefer standard library** over external packages
- **Pin versions** for reproducibility
- **Document why** each dependency is needed
- **Review licenses** before adding dependencies
- **Keep dependencies updated** for security

- Do not add dependencies for problems solvable with the Python standard library
- Any new dependency must be justified before use
- Avoid heavy GUI or database frameworks for this project
- Keep startup and installation simple

## File Organization

### Module Structure

Each module should have a clear purpose:

```python
"""Module for media business logic.

This module contains the MediaService class which handles
all business logic related to media operations including
CRUD operations, validation, and search.
"""

# Imports
import logging
from typing import List, Optional

from models.media import Media
from data.media_repository import MediaRepository
from business.validation import MediaValidator

# Module-level constants
logger = logging.getLogger(__name__)

# Classes
class MediaService:
    """Service for media business logic."""
    pass

# Module-level functions (if any)
def helper_function() -> None:
    """Helper function description."""
    pass
```

### File Size

- **Keep files focused** (single responsibility)
- **Split large files** (>500 lines) into smaller modules
- **Group related functionality** in packages

## Configuration Management

### Configuration File

Use a configuration module:

```python
"""Application configuration."""

import os
from pathlib import Path

# Application paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "media_archive.db"

# Database settings
DB_TIMEOUT = 5.0  # seconds
DB_CHECK_SAME_THREAD = False

# Validation limits
MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_REMARKS_LENGTH = 2000

# UI settings
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TABLE_ROW_HEIGHT = 25

# Logging
LOG_FILE = BASE_DIR / "media_archive.log"
LOG_LEVEL = "INFO"
```

## Documentation Maintenance

### Keep Documentation Updated

When making changes:

1. Update relevant docstrings
2. Update README if user-facing changes
3. Update architecture docs if design changes
4. Update TASKS.md to track progress
5. Add comments for complex logic

### Documentation Review

Review documentation quarterly:

- Remove outdated information
- Add missing documentation
- Improve clarity
- Update examples

## References
## Change Control for AI-Assisted Development

When implementing a feature, the AI agent should prefer this workflow:

1. read `PROJECT_OVERVIEW.md`
2. read `DATA_MODEL.md`
3. read `UI_WORKFLOW.md`
4. read this `DEV_RULES.md`
5. implement only the requested phase or feature

For every implementation step:
- keep changes small
- keep architecture stable
- avoid speculative future engineering
- favor completion of current scope over adding optional infrastructure

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Application overview
- [DATA_MODEL.md](DATA_MODEL.md) - Database schema
- [UI_WORKFLOW.md](UI_WORKFLOW.md) - User interface design
- [TASKS.md](TASKS.md) - Implementation roadmap
---

# AI Assisted Development Rules

This section defines additional rules specifically for AI-assisted development.

Any AI coding agent must read and follow these rules before generating or modifying code.

The goal of this project is a **simple, reliable, maintainable local desktop application**, not architectural complexity.

---

## AI Agent Behaviour


Prefer **simple and stable implementations** over theoretically flexible designs.

---

## Incremental Development

Development must happen in **small phases**.

Never implement the entire application in one step.

Typical implementation order:

1. project structure
2. configuration
3. database schema
4. repositories
5. business logic
6. GUI
7. search and filters
8. import/export
9. additional features
10. testing and refinement

Each phase should produce **working, testable code**.

---

## Project Scope Constraints

This project is intentionally limited in scope.

### Project Type

This application is:

- a **local desktop application**
- **single-user**
- based on **SQLite**
- designed for **low maintenance**

### Out of Scope

The following features must NOT be introduced unless explicitly requested:

- web server
- REST API
- cloud-only architecture
- user authentication systems
- role-based permissions
- microservice architecture
- Docker-first deployment
- mobile applications

The project must remain **simple and locally executable**.

---

## Dependency Policy

Dependencies must be kept minimal.

Prefer the **Python standard library** whenever possible.

Do not introduce heavy frameworks such as:

- Django
- FastAPI
- SQLAlchemy
- complex ORM frameworks

Any new dependency must include a short explanation of:

- why it is necessary
- why the standard library cannot solve the problem

---

## SQLite Specific Rules

Database implementation must follow these rules:

- Use **direct SQL queries** instead of ORM frameworks.
- Always use **parameterized queries**.
- Use **INTEGER PRIMARY KEY** for primary keys.
- Enforce **foreign key constraints**.
- Store dates in **ISO format (`YYYY-MM-DD`)** where possible.
- Allow nullable fields when real-world data may be incomplete.
- Keep schema simple and easy to migrate.

---

## GUI Simplicity Rules

The graphical user interface must remain simple.

Rules:

- Prefer **clear and functional layouts**.
- Avoid overly complex UI frameworks.
- Keep dialogs focused on a single task.
- Keep UI code separate from business logic and database access.
- Use clear labels and readable layouts.

The GUI should prioritize **usability over visual complexity**.

---

## AI Test Quality Rules

AI-generated tests must verify **correct behavior**, not just successful execution.

### Test Philosophy

Avoid trivial tests such as:


- "Does the function run without errors?"
- "Does the GUI display something?"

Instead, focus on verifying:

- Correct data transformations
- Proper error handling
- Business logic correctness
- Database integrity
- User interaction flows

Each test should verify **one specific behavior**.

---

## Code Quality Rules

Code must follow these quality standards:

- Use **type hints** for all functions and methods
- Keep functions **short and focused** (max 20 lines)
- Write **docstrings** for all public functions
- Use **meaningful variable names**
- Avoid deep nesting (max 3 levels)
- Keep imports organized and minimal
- Write **unit tests** for all business logic
- Follow **PEP 8** style guidelines

The codebase should be **maintainable and understandable** to new developers.   
---

# File History and Versioning Rules

Every Python source file in this project must contain a **History section in the module docstring**.

This history documents important changes made to the file.

Example:

```python
"""Main application window for Media Archive Manager.

This module provides the main GUI window with menu bar, toolbar, and main content area.

History:
20260307  V1.0: Initial main window implementation
20260307  V1.1: Added location management and search/filter functionality
20260307  V1.2: Integrated SearchPanel and enhanced filter menu
20260307  V1.3: Added import/export and backup functionality
20260308  V1.4: Implement two-phase import for locations and media
20260309  V1.5: Added location assignment after import and manual assignment tool
"""
```

---

## History Entry Format

Each entry must follow this format:

```
YYYYMMDD  Vx.y: description of change
```

Example:

```
20260310  V1.6: Added validation for media type
```

Rules:

- History must appear in the **module docstring**
- The section must start with `History:`
- New entries must be **appended at the bottom**
- Date format must be `YYYYMMDD`
- Description must be short and clear

---

# Program Versioning

The application uses the version format:

```
V<major>.<minor>
```

Example:

```
V1.5
```

---

## Normal Update

For normal code updates:

Increase the **minor version by 0.1**

Example:

```
V1.5 → V1.6
```

---

## New Release

When a **new release** is declared:

- Increase the **major version by 1**
- Reset the minor version to **0**

Example:

```
V1.9 → V2.0
```

---

# Version Synchronization

Whenever code is modified:

1. Locate the `History:` section of the modified file
2. Add a new entry
3. Use the **current program version**
4. Provide a short description of the change

Example:

```
20260310  V1.6: Added CSV export functionality
```

---

# AI Agent Requirements

When modifying any Python file, the AI agent must:

1. Locate the `History:` section in the module docstring
2. Add a new entry with:
   - current date
   - incremented version
   - short description
3. Ensure the version matches the current program version
4. Append the entry at the **end of the history list**

The AI agent must **never remove existing history entries**.

---

# Change Size Limit Rule

To maintain stability and readability of the codebase, AI agents must limit the size of modifications in a single step.

## Change Size Policy

AI agents must follow these limits unless explicitly instructed otherwise.

### Maximum Change Scope

In a single modification step the AI agent must not:

- modify more than **3 files**
- add more than **200 lines of code**
- remove more than **50 lines of code**
- restructure directories
- rename multiple files

If a requested change exceeds these limits, the AI agent must split the work into **multiple incremental steps**.

---

## Large Change Protocol

If the requested feature requires larger changes, the AI agent must:

1. Explain the planned change
2. List the files that will be affected
3. Implement the change in **small phases**

Example workflow:

Step 1  
Create new module.

Step 2  
Integrate module into service layer.

Step 3  
Add GUI integration.

Step 4  
Add tests.

---

## File Rewrite Protection

The AI agent must **not rewrite entire files** unless:

- explicitly requested
- refactoring is unavoidable
- the user confirms the rewrite

Instead the agent must:

- modify specific functions
- extend existing code
- keep existing logic intact

---

## Safe Modification Principle

The goal is to **preserve working code**.

Preferred actions:

✔ add small functions  
✔ modify existing functions  
✔ extend modules  
✔ add tests  

Avoid:

✘ large rewrites  
✘ architectural changes  
✘ speculative refactoring  

---

## Emergency Rule

If the AI agent detects that the change would require large modifications, it must stop and ask for confirmation before continuing.