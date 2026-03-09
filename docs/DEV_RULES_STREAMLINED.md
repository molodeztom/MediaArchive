# Development Rules - Streamlined Version

## CRITICAL RULES FOR AI AGENTS

### 1. Project Philosophy
- **Goal**: Simple, reliable, maintainable local desktop application
- **NOT Goal**: Architectural sophistication or theoretical flexibility
- **Priority Order**: Correctness > Maintainability > Simplicity > Readability > Performance

### 2. Modification Limits
- Modify only files necessary for the requested change
- Do NOT rewrite large working files
- Do NOT restructure project without approval
- Prefer simplest working solution
- Preserve existing functionality

### 3. Change Size Limits (Per Step)
- Maximum 3 files modified
- Maximum 200 lines added
- Maximum 50 lines removed
- If exceeded, split into multiple steps

---

## VERSIONING RULES (MANDATORY)

### Version Format
```
V<major>.<minor>
Example: V1.5
```

### Version Increment Rules
1. **After each phase completion**: Increase minor version by 0.1
   - Phase 9A complete: V1.0 → V1.1
   - Phase 9B complete: V1.1 → V1.2
   
2. **After normal code updates**: Increase minor version by 0.1
   - V1.5 → V1.6

3. **New release**: Increase major version, reset minor to 0
   - V1.9 → V2.0

### Version Update Locations (MANDATORY)
When completing a phase, update version in:
- `src/gui/about_dialog.py` - APP_VERSION constant
- Main window title (if displayed)
- Any UI version display

### File History Format (MANDATORY)
Every modified Python file must have History section in module docstring:

```python
"""Module description.

History:
YYYYMMDD  Vx.y: description of change
"""
```

Rules:
- Append new entries at the end
- Never remove existing entries
- Use current program version
- Format: `YYYYMMDD  Vx.y: short description`

---

## CODE STYLE (MANDATORY)

### PEP 8 Specifics
- Line length: 100 characters
- Indentation: 4 spaces (no tabs)
- Encoding: UTF-8

### Naming
- Module: `lowercase_with_underscores`
- Class: `PascalCase`
- Function: `lowercase_with_underscores`
- Variable: `lowercase_with_underscores`
- Constant: `UPPERCASE_WITH_UNDERSCORES`
- Private: `_leading_underscore`

### Imports (3 groups, blank line separated)
```python
# 1. Standard library
import sqlite3
from datetime import datetime

# 2. Third-party (if any)
# import external_library

# 3. Local application
from models.media import Media
```

Use absolute imports only.

### Type Hints (MANDATORY)
All functions must have type hints:
```python
def get_media_by_id(media_id: int) -> Optional[Media]:
    """Retrieve media by ID."""
    pass
```

### Docstrings (MANDATORY)
All public functions must have Google-style docstrings:
```python
def create_media(name: str, media_type: str) -> Media:
    """Create a new media record.
    
    Args:
        name: The name of the media (required).
        media_type: Type of media (e.g., 'DVD', 'M-Disk').
    
    Returns:
        The newly created Media object.
    
    Raises:
        ValidationError: If validation fails.
    """
    pass
```

---

## ARCHITECTURE RULES (MANDATORY)

### Layer Separation
```
GUI Layer → Business Logic Layer → Data Access Layer → Database
```

Rules:
- GUI only calls Business Logic
- Business Logic only calls Data Access
- Data Access only interacts with Database
- NO layer skipping
- NO circular dependencies

### Dependency Injection
Pass dependencies through constructors:
```python
class MediaService:
    def __init__(self, media_repository: MediaRepository):
        self._repository = media_repository
```

---

## DATABASE RULES (MANDATORY)

### SQLite Implementation
- Use direct SQLite3 from standard library
- NO ORM frameworks (SQLAlchemy, Peewee, etc.)
- NO migration frameworks (Alembic, etc.)
- Use parameterized queries ALWAYS
- Store dates as ISO format (YYYY-MM-DD) in database
- Display dates as DD.MM.YYYY in UI
- Store booleans as INTEGER (0/1)

### Query Safety
```python
# CORRECT - parameterized query
cursor.execute("SELECT * FROM media WHERE name LIKE ?", (f"%{search}%",))

# WRONG - string concatenation (SQL injection risk)
cursor.execute(f"SELECT * FROM media WHERE name LIKE '%{search}%'")
```

### Foreign Keys
```python
# Enable foreign keys
conn.execute("PRAGMA foreign_keys = ON")

# Use ON DELETE appropriately
FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL
```

---

## FORBIDDEN PATTERNS

### DO NOT Introduce (unless explicitly requested):
- ORM frameworks
- Web frameworks
- REST APIs
- Abstract factory patterns
- Strategy patterns for single implementation
- Observer patterns for simple callbacks
- MVC/MVP/MVVM frameworks
- State management libraries
- Plugin systems
- Microservices architecture
- Connection pooling
- Complex migration frameworks

### DO Use:
- Direct instantiation
- Simple inheritance
- Constructor injection
- Direct event binding
- Simple tkinter widgets
- Parameterized SQL queries
- Context managers

---

## ERROR HANDLING

### Custom Exceptions
```python
class MediaArchiveError(Exception):
    """Base exception."""
    pass

class ValidationError(MediaArchiveError):
    """Input validation failed."""
    pass

class DatabaseError(MediaArchiveError):
    """Database operation failed."""
    pass

class NotFoundError(MediaArchiveError):
    """Resource not found."""
    pass
```

### Error Handling Rules
1. Catch specific exceptions, not generic `Exception`
2. Log errors before re-raising
3. Provide user-friendly messages in GUI
4. Use context managers for cleanup
5. Don't silently swallow exceptions

---

## TESTING RULES

### Test Quality
- Verify correct behavior, not just successful execution
- One assertion per test (when possible)
- Test edge cases (empty strings, None, max length)
- Test error conditions
- Use in-memory database for data layer tests
- Mock dependencies for unit tests

### Test Naming
```python
def test_create_media_with_valid_data_succeeds():
    """Test that creating media with valid data succeeds."""
    pass

def test_create_media_with_empty_name_raises_validation_error():
    """Test that creating media with empty name raises ValidationError."""
    pass
```

---

## DEPENDENCY POLICY

### Rules
- Prefer Python standard library
- Keep dependencies minimal
- Any new dependency must be justified
- Document why standard library cannot solve the problem

### Forbidden Dependencies
- Django
- FastAPI
- SQLAlchemy
- Complex ORM frameworks
- Heavy GUI frameworks beyond tkinter

---

## LOGGING

### Logging Levels
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Recoverable issues
- ERROR: Operation failed
- CRITICAL: Application may crash

### Usage
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Searching for media with query: {query}")
logger.info(f"Created new media: {media.name}")
logger.warning(f"Media {media_id} not found")
logger.error(f"Database error: {e}")
```

---

## PROJECT SCOPE

### This IS:
- Local desktop application
- Single-user tool
- SQLite-based
- Low-maintenance

### This is NOT (unless explicitly requested):
- Web application
- Multi-user system
- Cloud-based
- Mobile app
- REST API
- Authentication system
- Docker-first deployment

---

## INCREMENTAL DEVELOPMENT

### Implementation Order
1. Project structure
2. Database schema
3. Minimal application startup
4. Basic CRUD
5. Search and filtering
6. Additional views
7. Export and backup
8. Optional enhancements

### Each Phase Must:
- Produce working, testable code
- Be small and focused
- Not break existing functionality

---

## QUICK REFERENCE CHECKLIST

Before submitting code:
- [ ] Follows PEP 8 (100 char line length)
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] History section updated in modified files
- [ ] Version incremented if phase complete
- [ ] Input validation implemented
- [ ] Error handling appropriate
- [ ] Tests written and passing
- [ ] No hardcoded values
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Logging appropriate
- [ ] Parameterized SQL queries used
- [ ] Layer separation maintained

---

## SUMMARY FOR AI AGENTS

**When modifying code:**
1. Read this file first
2. Make minimal necessary changes
3. Update file History section
4. Increment version if phase complete
5. Update About dialog version
6. Keep changes under limits (3 files, 200 lines)
7. Preserve working functionality
8. Use simplest solution
9. Follow layer separation
10. Use parameterized queries
11. Add type hints and docstrings
12. Write tests

**Remember**: Simple, reliable, maintainable > Sophisticated, complex, flexible
