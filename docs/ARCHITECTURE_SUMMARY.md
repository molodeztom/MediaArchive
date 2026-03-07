# Architecture Summary

## Quick Reference

This document provides a high-level overview of the Media Archive Manager architecture. For detailed information, refer to the specific documentation files.

## Application Overview

**Media Archive Manager** is a local desktop application for managing physical storage media inventory (M-Disks, DVDs, CDs, backup media, etc.). It replaces a Microsoft Access database with a modern Python-based solution.

**Key Characteristics:**
- Local desktop application (Windows)
- Single user
- No cloud dependency
- Easy database backup (single SQLite file)
- Minimal dependencies (uses Python standard library)

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.10+ | Modern, maintainable, excellent standard library |
| **GUI Framework** | tkinter | Built-in, no external dependencies, sufficient for requirements |
| **Database** | SQLite | Serverless, single file, easy backup, perfect for local apps |
| **Architecture** | Layered (3-tier) | Clear separation of concerns, maintainable |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      GUI Layer (tkinter)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Main Window  │  │   Dialogs    │  │   Widgets    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Services   │  │  Validation  │  │    Export    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Repositories │  │   Database   │  │    Models    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                          │
│              media_archive.db (single file)                 │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
MediaArchive/
├── src/                    # Source code
│   ├── gui/               # GUI layer (tkinter)
│   ├── business/          # Business logic layer
│   ├── data/              # Data access layer
│   ├── models/            # Data models
│   └── utils/             # Utilities
├── tests/                 # Unit and integration tests
├── data/                  # Database files
├── docs/                  # Documentation
├── requirements.txt       # Dependencies (minimal)
├── main.py               # Entry point
└── README.md             # Project readme
```

## Database Schema

### Tables

**storage_location**
- Stores physical storage locations
- Fields: id, box, place, detail, timestamps
- Example: "CD Register A" in "office cabinet", "slot 4"

**media**
- Stores media records
- Fields: id, name, content_description, remarks, creation_date, valid_until_date, media_type, company, license_code, location_id, timestamps
- Foreign key to storage_location

### Relationships

```
storage_location (1) ──────< (many) media
```

One storage location can contain many media items.

## Key Features

### Core Features
- ✅ Add, edit, delete media records
- ✅ Search by name, content, creation date
- ✅ Filter by media type
- ✅ List expired media
- ✅ List media by storage location
- ✅ Manage storage locations

### Data Management
- ✅ CSV import (for migration from Access)
- ✅ CSV export (for backup)
- ✅ Database backup (copy SQLite file)

### User Interface
- ✅ Main window with media list table
- ✅ Add/Edit dialog with validation
- ✅ Search panel with multiple criteria
- ✅ Location management dialog
- ✅ Keyboard shortcuts
- ✅ Context menus

## Design Principles

### Layered Architecture
- **GUI Layer**: Only handles user interaction and display
- **Business Logic Layer**: Handles validation, business rules, and orchestration
- **Data Access Layer**: Only handles database operations
- **No layer skipping**: Each layer only communicates with adjacent layers

### Separation of Concerns
- Each module has a single, well-defined responsibility
- Models represent data structures
- Repositories handle database operations
- Services handle business logic
- GUI components handle user interaction

### Dependency Injection
- Services receive repository dependencies via constructor
- Makes testing easier (can mock dependencies)
- Reduces coupling between components

### Type Safety
- Use Python type hints throughout
- Helps catch errors early
- Improves code documentation
- Enables better IDE support

## Data Flow Examples

### Adding a New Media Record

```
User clicks "Add" button
    ↓
GUI opens MediaFormDialog
    ↓
User fills form and clicks "Save"
    ↓
GUI calls MediaService.create_media()
    ↓
Service validates input (MediaValidator)
    ↓
Service calls MediaRepository.create()
    ↓
Repository executes SQL INSERT
    ↓
Database stores record
    ↓
Repository returns Media object
    ↓
Service returns Media object
    ↓
GUI refreshes table and shows success message
```

### Searching for Media

```
User enters search term and clicks "Search"
    ↓
GUI calls SearchService.search_by_name()
    ↓
Service calls MediaRepository.search_by_name()
    ↓
Repository executes SQL SELECT with LIKE
    ↓
Database returns matching rows
    ↓
Repository converts rows to Media objects
    ↓
Service returns List[Media]
    ↓
GUI displays results in table
```

## Security Considerations

### SQL Injection Prevention
- **Always use parameterized queries**
- Never concatenate user input into SQL strings
- Repository layer enforces this pattern

### Input Validation
- All user input validated in business logic layer
- Validation rules defined in validation module
- GUI provides immediate feedback on invalid input

### Data Protection
- Database file stored locally (no network exposure)
- No authentication needed (single user, local app)
- License codes stored as plain text (acceptable for local use)

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns (name, type, location_id, dates)
- Parameterized queries for query plan caching
- Transactions for batch operations
- VACUUM periodically to reclaim space

### GUI Responsiveness
- Load data asynchronously for large datasets (future enhancement)
- Debounce search input to avoid excessive queries
- Use virtual scrolling for large tables (future enhancement)
- Cache frequently accessed data

## Error Handling Strategy

### Exception Hierarchy
```
MediaArchiveError (base)
├── ValidationError (invalid input)
├── DatabaseError (database operations)
└── NotFoundError (resource not found)
```

### Error Handling by Layer
- **GUI Layer**: Display user-friendly error messages
- **Business Logic Layer**: Validate input, raise ValidationError
- **Data Access Layer**: Handle database errors, raise DatabaseError
- **All Layers**: Log errors for debugging

## Testing Strategy

### Unit Tests
- Test business logic in isolation
- Mock repository dependencies
- Test validation rules
- Test error handling

### Integration Tests
- Test complete workflows
- Use in-memory database
- Test database operations
- Test CSV import/export

### User Acceptance Testing
- Test with real users
- Test with real data
- Verify all requirements met
- Gather usability feedback

## Deployment

### Requirements
- Python 3.10 or higher
- Windows 10/11
- No external dependencies (uses standard library)

### Installation
1. Install Python 3.10+
2. Clone/download project
3. Run `python main.py`

### Database Initialization
- Database created automatically on first run
- Schema applied automatically
- No manual setup required

### Backup Strategy
- **Simple**: Copy `data/media_archive.db` file
- **Scheduled**: Use Windows Task Scheduler to copy file
- **Export**: Export to CSV for portability

## Future Enhancements

### Potential Features
1. **Reporting**: Generate PDF/HTML reports
2. **Print Support**: Print media labels
3. **Backup Automation**: Scheduled automatic backups
4. **Advanced Search**: Full-text search with FTS5
5. **Media Images**: Store photos of media
6. **Barcode Support**: Scan barcodes for quick lookup
7. **Statistics Dashboard**: Visual charts and graphs
8. **Tags**: Additional categorization
9. **History**: Track changes to records
10. **Multi-language**: Internationalization support

### Potential Technical Improvements
1. **Async Operations**: Use asyncio for database operations
2. **Virtual Scrolling**: Handle very large datasets
3. **Caching**: Cache frequently accessed data
4. **Packaging**: Create standalone executable with PyInstaller
5. **Auto-updates**: Check for application updates
6. **Database Migrations**: Version database schema

## Documentation Index

| Document | Purpose |
|----------|---------|
| [README.md](../README.md) | Project overview and quick start |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Detailed application description and goals |
| [DATA_MODEL.md](DATA_MODEL.md) | Database schema, tables, and queries |
| [UI_WORKFLOW.md](UI_WORKFLOW.md) | User interface design and workflows |
| [DEV_RULES.md](DEV_RULES.md) | Coding standards and best practices |
| [TASKS.md](TASKS.md) | Implementation roadmap and task breakdown |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | File organization and structure |
| [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md) | This document |

## Getting Started with Implementation

### Recommended Approach

1. **Read Documentation**: Review all documentation files
2. **Set Up Environment**: Install Python 3.10+, set up IDE
3. **Follow Task Order**: Start with Phase 1 in TASKS.md
4. **Test Incrementally**: Write tests as you implement
5. **Follow Dev Rules**: Adhere to coding standards in DEV_RULES.md

### First Steps

1. Create project structure (directories and `__init__.py` files)
2. Create configuration module
3. Create data models
4. Create database schema
5. Create database manager
6. Create repositories
7. Write tests for data layer

### Development Workflow

```
1. Read task in TASKS.md
2. Write test (if applicable)
3. Implement feature
4. Run tests
5. Commit changes
6. Move to next task
```

## Key Design Decisions

### Why tkinter?
- Built-in with Python (no dependencies)
- Sufficient for requirements
- Cross-platform (though targeting Windows)
- Simple to learn and use
- Good documentation

### Why SQLite?
- Serverless (no installation)
- Single file (easy backup)
- Excellent for local applications
- Full SQL support
- Reliable and well-tested

### Why Layered Architecture?
- Clear separation of concerns
- Easy to test (can mock layers)
- Easy to maintain (changes isolated)
- Easy to understand (clear structure)
- Scalable (can add features without breaking existing code)

### Why Minimal Dependencies?
- Easier installation
- Fewer security vulnerabilities
- Faster startup
- Smaller distribution size
- Less maintenance burden

## Success Criteria

The architecture is successful if:

1. ✅ All requirements can be implemented
2. ✅ Code is maintainable and testable
3. ✅ Performance is acceptable
4. ✅ User interface is intuitive
5. ✅ Database is reliable and easy to backup
6. ✅ Application runs on Windows without issues
7. ✅ Future enhancements can be added easily

## Conclusion

This architecture provides a solid foundation for the Media Archive Manager application. It balances simplicity with maintainability, uses proven technologies, and follows best practices. The layered architecture ensures the application can grow and evolve while remaining maintainable.

The next step is to begin implementation following the roadmap in [TASKS.md](TASKS.md).
