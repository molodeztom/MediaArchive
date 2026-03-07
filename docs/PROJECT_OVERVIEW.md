# Project Overview

## Application Name
**Media Archive Manager**

## Purpose

A private desktop application for managing an inventory of physical storage media. This tool replaces a simple Microsoft Access database with a modern, maintainable Python-based solution.

## Problem Statement

Users who maintain collections of physical media (M-Disks, DVDs, CDs, backup media, software installation discs, archive discs) need a simple way to:

- Track what media they own
- Record what content is stored on each medium
- Find specific media quickly
- Identify expired or outdated media
- Organize media by physical storage location
- Maintain license keys and important metadata

The existing Microsoft Access solution is outdated and difficult to maintain. A modern Python application provides better portability, easier backup, and simpler maintenance.

## Goals

### Primary Goals

1. **Replace Access Database**: Provide all functionality of the existing Access database
2. **Easy to Use**: Simple, intuitive interface for non-technical users
3. **Local and Private**: No cloud dependency, all data stored locally
4. **Easy Backup**: Single SQLite file that can be easily copied
5. **Windows Compatible**: Runs reliably on Windows 10/11

### Secondary Goals

1. **Data Migration**: Support importing data from CSV (exported from Access)
2. **Data Export**: Allow exporting to CSV for backup or analysis
3. **Maintainable**: Clean architecture for future enhancements
4. **Minimal Dependencies**: Use built-in Python libraries where possible

## Target Users

- **Primary User**: Single user managing personal media collection
- **Technical Level**: Non-technical to moderately technical
- **Use Case**: Home/office media inventory management
- **Frequency**: Occasional use (adding new media, searching for specific items)

## Scope

### In Scope

#### Core Features
- Add new media records
- Edit existing media records
- Delete media records
- Search by name
- Search by content description
- Search by creation date
- List expired media (based on "valid until" date)
- List media by storage location
- Filter by media type
- Manage storage locations (add, edit, delete)

#### Data Management
- CSV import (for migration from Access)
- CSV export (for backup)
- Database backup (copy SQLite file)

#### User Interface
- Main window with media list
- Add/Edit dialog
- Search panel
- Storage location management
- Menu bar with common actions
- Toolbar for quick access

### Out of Scope

- Multi-user support
- Cloud synchronization
- Mobile application
- Web interface
- Barcode scanning
- Image/photo storage
- File content indexing
- Network sharing
- User authentication
- Audit logging
- Advanced reporting
- Print functionality (initial version)

## Technical Overview

### Architecture

**Layered Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         GUI Layer (tkinter)         │
│  main_window, dialogs, widgets      │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Business Logic Layer           │
│  services, validation, export       │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│       Data Access Layer             │
│  repositories, database manager     │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│         SQLite Database             │
│      media_archive.db               │
└─────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.10+ | Modern, maintainable, cross-platform |
| GUI Framework | tkinter | Built-in, no dependencies, sufficient for requirements |
| Database | SQLite | Serverless, single file, easy backup |
| Data Format | CSV | Universal format for import/export |

### Key Design Principles

1. **Separation of Concerns**: GUI, business logic, and data access are separate
2. **Single Responsibility**: Each module has one clear purpose
3. **Dependency Injection**: Services receive dependencies (repositories)
4. **Data Validation**: All input validated in business layer
5. **Error Handling**: Graceful error handling with user-friendly messages
6. **Type Safety**: Use Python type hints throughout

## Success Criteria

The project is successful when:

1. ✅ All media from Access database can be imported
2. ✅ Users can add, edit, delete, and search media
3. ✅ Storage locations can be managed
4. ✅ Expired media can be identified
5. ✅ Data can be exported to CSV
6. ✅ Application runs on Windows without installation issues
7. ✅ Database can be backed up by copying a single file
8. ✅ Interface is intuitive for non-technical users

## Constraints

### Technical Constraints
- Must run on Windows 10/11
- Must work offline (no internet required)
- Must use only built-in Python libraries (or minimal dependencies)
- Database must be a single file
- Must support Python 3.10+

### Business Constraints
- Single user only (no concurrent access)
- Desktop application only (no web/mobile)
- Private use (no licensing concerns)

### User Constraints
- Must be simple enough for non-technical users
- Must not require database administration knowledge
- Must provide clear error messages

## Future Enhancements

Potential features for future versions:

1. **Reporting**: Generate reports (media by type, location, etc.)
2. **Print Support**: Print media labels or inventory lists
3. **Backup Automation**: Scheduled automatic backups
4. **Advanced Search**: Full-text search, complex queries
5. **Media Images**: Store photos of media or covers
6. **Barcode Support**: Scan barcodes for quick lookup
7. **Statistics**: Dashboard with collection statistics
8. **Tags**: Additional categorization with tags
9. **Notes**: Rich text notes with formatting
10. **History**: Track changes to media records

## Project Timeline

This is an architecture and planning phase. Implementation will follow in phases:

1. **Phase 1**: Database and data layer
2. **Phase 2**: Business logic and validation
3. **Phase 3**: Basic GUI (add, edit, delete, list)
4. **Phase 4**: Search and filter functionality
5. **Phase 5**: CSV import/export
6. **Phase 6**: Testing and refinement

## References

- [DATA_MODEL.md](DATA_MODEL.md) - Database schema and relationships
- [UI_WORKFLOW.md](UI_WORKFLOW.md) - User interface design
- [DEV_RULES.md](DEV_RULES.md) - Development guidelines
- [TASKS.md](TASKS.md) - Implementation roadmap
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File organization
