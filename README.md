# Media Archive Manager

A private desktop application for managing physical storage media inventory.

## Overview

This application replaces a simple Microsoft Access database with a modern Python-based solution for tracking physical media such as M-Disks, DVDs, CDs, backup media, software installation discs, and archive discs.

## Features

- Add, edit, and delete media records
- Search by name, content, or creation date
- List expired media
- Filter by media type
- Organize by storage location
- CSV import/export for data backup and migration

## Technology Stack

- **Language**: Python 3.10+
- **Database**: SQLite
- **GUI Framework**: tkinter (built-in)
- **Architecture**: Layered (GUI / Business Logic / Data Access)

## Project Structure

```
MediaArchive/
├── src/                    # Source code
│   ├── gui/               # GUI layer (tkinter)
│   ├── business/          # Business logic layer
│   ├── data/              # Data access layer
│   └── models/            # Data models
├── tests/                 # Unit and integration tests
├── data/                  # Database files
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── main.py               # Application entry point
```

## Documentation

See the [`docs/`](docs/) folder for detailed documentation:

- [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) - Application description and goals
- [DATA_MODEL.md](docs/DATA_MODEL.md) - Database schema and relationships
- [UI_WORKFLOW.md](docs/UI_WORKFLOW.md) - User interface design and workflows
- [DEV_RULES.md](docs/DEV_RULES.md) - Development guidelines and best practices
- [TASKS.md](docs/TASKS.md) - Implementation roadmap

## Quick Start

```bash
# Install dependencies (minimal)
pip install -r requirements.txt

# Run the application
python main.py
```

## Requirements

- Python 3.10 or higher
- Windows 10/11
- No internet connection required

## License

Private use only.
