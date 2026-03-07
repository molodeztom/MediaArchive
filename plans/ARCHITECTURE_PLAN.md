# Media Archive Manager - Architecture Plan

## Executive Summary

This document presents the complete architecture plan for the Media Archive Manager, a local desktop application to replace a Microsoft Access database for managing physical storage media inventory.

**Status**: Architecture Complete ✅  
**Next Phase**: Implementation  
**Estimated Phases**: 9 phases  

## Project Goals

Replace a Microsoft Access database with a modern Python-based desktop application that:
- Manages physical media inventory (M-Disks, DVDs, CDs, backup media, etc.)
- Runs locally on Windows with no cloud dependency
- Uses a single SQLite database file for easy backup
- Provides a simple, intuitive GUI for non-technical users
- Supports CSV import/export for data migration and backup

## Architecture Overview

### Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.10+ | Modern, maintainable, excellent standard library |
| **GUI** | tkinter | Built-in, no dependencies, sufficient for requirements |
| **Database** | SQLite | Single file, easy backup, perfect for local apps |
| **Architecture** | 3-tier layered | Clear separation, maintainable, testable |

### Architecture Pattern

**Layered Architecture** with strict separation:

```
GUI Layer (tkinter)
    ↓
Business Logic Layer (services, validation)
    ↓
Data Access Layer (repositories)
    ↓
SQLite Database
```

**Key Principle**: Each layer only communicates with adjacent layers. No layer skipping.

## Database Design

### Schema

**Two main tables:**

1. **storage_location** - Physical storage locations
   - id, box, place, detail, timestamps
   - Example: "CD Register A" in "office cabinet", "slot 4"

2. **media** - Media records
   - id, name, content_description, remarks, creation_date, valid_until_date, media_type, company, license_code, location_id, timestamps
   - Foreign key to storage_location (ON DELETE SET NULL)

**Relationship**: One location → Many media items

**Indexes**: On name, type, location_id, dates for fast queries

### Media Types

Predefined types (stored as TEXT):
- M-Disk
- DVD
- CD
- Blu-ray
- USB Drive
- External HDD
- Backup Tape
- Other

## User Interface Design

### Main Window

```
┌─────────────────────────────────────────────────────────────┐
│ Media Archive Manager                              [_][□][X] │
├─────────────────────────────────────────────────────────────┤
│ File   Edit   View   Tools   Help                          │
├─────────────────────────────────────────────────────────────┤
│ [+] [✎] [🗑] [🔍] [📊] [⚙]                                  │
├─────────────────────────────────────────────────────────────┤
│ Search Panel (collapsible)                                  │
├─────────────────────────────────────────────────────────────┤
│                   Media List Table                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Status: 42 items | 3 expired                                │
└─────────────────────────────────────────────────────────────┘
```

### Key Dialogs

1. **Add/Edit Media Dialog** - Form with validation
2. **Manage Locations Dialog** - CRUD for storage locations
3. **Search Panel** - Multiple search criteria
4. **Import/Export Dialogs** - CSV operations
5. **Statistics Dialog** - Database statistics

### Features

- Add, edit, delete media
- Search by name, content, date
- Filter by type, location
- List expired media
- Manage storage locations
- CSV import/export
- Database backup

## Project Structure

```
MediaArchive/
├── src/
│   ├── gui/              # GUI layer
│   │   ├── main_window.py
│   │   ├── media_form.py
│   │   ├── location_dialog.py
│   │   └── widgets/
│   ├── business/         # Business logic
│   │   ├── media_service.py
│   │   ├── location_service.py
│   │   ├── search_service.py
│   │   ├── validation.py
│   │   └── export_service.py
│   ├── data/             # Data access
│   │   ├── database.py
│   │   ├── media_repository.py
│   │   ├── location_repository.py
│   │   └── schema.py
│   ├── models/           # Data models
│   │   ├── media.py
│   │   ├── location.py
│   │   └── enums.py
│   └── utils/            # Utilities
│       ├── config.py
│       ├── date_utils.py
│       └── exceptions.py
├── tests/                # Unit tests
├── data/                 # Database files
├── docs/                 # Documentation
├── main.py              # Entry point
└── README.md
```

## Implementation Roadmap

### Phase 1: Project Setup
- Create project structure
- Create configuration module
- Create data models
- Create custom exceptions

### Phase 2: Database Layer
- Create database schema
- Create database manager
- Create repositories (location, media)
- Write database tests

### Phase 3: Business Logic Layer
- Create validation module
- Create services (media, location, search, export)
- Create utility functions
- Write business logic tests

### Phase 4: Basic GUI
- Create custom widgets
- Create main window
- Create media form dialog
- Create location dialog
- Wire up basic CRUD

### Phase 5: Search and Filter
- Create search panel
- Implement search functionality
- Implement filters
- Add keyboard shortcuts

### Phase 6: Import/Export
- Create import dialog
- Create export dialog
- Implement CSV import/export
- Add database backup

### Phase 7: Additional Features
- Create statistics dialog
- Create about dialog
- Add application icon
- Polish UI
- Add logging

### Phase 8: Testing
- Integration testing
- User acceptance testing
- Bug fixes
- Documentation updates
- Code cleanup

### Phase 9: Deployment
- Create entry point
- Create startup scripts
- Create installation guide
- Create migration guide
- Optional: Package as executable

## Development Guidelines

### Code Style
- Follow PEP 8 (100 char line length)
- Use type hints throughout
- Use Google-style docstrings
- Use meaningful variable names

### Architecture Rules
- Maintain layer separation
- Use dependency injection
- Validate in business layer
- Use parameterized queries (always)
- Handle errors gracefully

### Testing Strategy
- Write unit tests for business logic
- Use in-memory database for tests
- Mock dependencies
- Test edge cases and errors

### Error Handling
- Custom exception hierarchy
- User-friendly error messages in GUI
- Log all errors
- Clean up resources

## Key Design Decisions

### Why tkinter?
✅ Built-in (no dependencies)  
✅ Sufficient for requirements  
✅ Simple to learn  
✅ Good documentation  

### Why SQLite?
✅ Single file (easy backup)  
✅ No server needed  
✅ Full SQL support  
✅ Reliable and fast  

### Why Layered Architecture?
✅ Clear separation of concerns  
✅ Easy to test  
✅ Easy to maintain  
✅ Scalable  

### Why Minimal Dependencies?
✅ Easier installation  
✅ Fewer security issues  
✅ Faster startup  
✅ Less maintenance  

## Success Criteria

The architecture is successful if:

1. ✅ All requirements can be implemented
2. ✅ Code is maintainable and testable
3. ✅ Performance is acceptable
4. ✅ UI is intuitive for non-technical users
5. ✅ Database is reliable and easy to backup
6. ✅ Runs on Windows without issues
7. ✅ Future enhancements can be added easily

## Documentation

Complete documentation available in [`/docs`](../docs/):

| Document | Purpose |
|----------|---------|
| **PROJECT_OVERVIEW.md** | Detailed application description and goals |
| **DATA_MODEL.md** | Database schema, tables, queries, ER diagram |
| **UI_WORKFLOW.md** | User interface design and workflows |
| **DEV_RULES.md** | Coding standards and best practices |
| **TASKS.md** | Detailed implementation roadmap |
| **PROJECT_STRUCTURE.md** | File organization and structure |
| **ARCHITECTURE_SUMMARY.md** | High-level architecture overview |

## Next Steps

### To Begin Implementation:

1. **Review Documentation**: Read all docs in `/docs` folder
2. **Set Up Environment**: Install Python 3.10+, set up IDE
3. **Switch to Code Mode**: Use Code mode to create files
4. **Start with Phase 1**: Follow TASKS.md sequentially
5. **Test Incrementally**: Write and run tests as you build

### Recommended First Tasks:

1. Create project directories and `__init__.py` files
2. Create `src/utils/config.py` with configuration
3. Create `src/models/enums.py` with MediaType enum
4. Create `src/models/location.py` with StorageLocation class
5. Create `src/models/media.py` with Media class

## Questions for Review

Before starting implementation, please confirm:

1. ✅ **GUI Framework**: tkinter is acceptable (minimal dependencies)
2. ✅ **CSV Import/Export**: Feature is included
3. ✅ **Database Design**: Two-table schema meets requirements
4. ✅ **Architecture**: Layered approach is appropriate
5. ✅ **Project Structure**: File organization is clear

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Database corruption | Use transactions, regular backups |
| Data loss during import | Validation, preview, error reporting |
| Performance issues | Indexes, query optimization |
| UI responsiveness | Async operations (future) |
| Windows compatibility | Test on multiple Windows versions |

## Future Enhancements

Potential features for future versions:
- PDF/HTML reporting
- Print media labels
- Automated backups
- Full-text search (FTS5)
- Media images/photos
- Barcode scanning
- Statistics dashboard
- Tags for categorization
- Change history tracking
- Multi-language support

## Conclusion

The architecture is complete and ready for implementation. The design balances:
- **Simplicity** - Easy to understand and maintain
- **Functionality** - Meets all requirements
- **Maintainability** - Clean separation, testable
- **Performance** - Optimized database, efficient queries
- **Usability** - Intuitive UI for non-technical users

**Status**: ✅ Architecture approved and ready for implementation

**Next Action**: Switch to Code mode and begin Phase 1 implementation following TASKS.md

---

*Architecture designed: 2026-03-07*  
*Documentation location: `/docs`*  
*Implementation guide: `/docs/TASKS.md`*
