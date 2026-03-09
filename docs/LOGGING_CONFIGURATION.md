# Logging Configuration Guide

## Overview

The Media Archive Manager uses a centralized logging configuration system that provides both file and console logging with automatic log rotation.

## Quick Start

### Basic Usage

To configure logging in your application, import and call the `configure_logging()` function:

```python
from gui.logging_config import configure_logging
import logging

# Configure logging at application startup
configure_logging()

# Get logger for your module
logger = logging.getLogger(__name__)

# Use logger
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### With Custom Log Level

```python
from gui.logging_config import configure_logging
import logging

# Configure with DEBUG level for verbose logging
configure_logging(log_level=logging.DEBUG)

# Or use other levels
configure_logging(log_level=logging.WARNING)
configure_logging(log_level=logging.ERROR)
```

## Configuration Details

### Log Levels

The logging system supports five levels (from least to most severe):

| Level | Value | Usage |
|-------|-------|-------|
| DEBUG | 10 | Detailed information for debugging |
| INFO | 20 | General informational messages (default) |
| WARNING | 30 | Warning messages for potentially harmful situations |
| ERROR | 40 | Error messages for serious problems |
| CRITICAL | 50 | Critical messages for very serious problems |

### File Logging

**Location**: `logs/media_archive.log` (in project root)

**Features**:
- Automatic directory creation
- Rotating file handler (prevents unlimited growth)
- Maximum file size: 10 MB
- Backup files: 5 (keeps last 5 rotated logs)
- Log level: DEBUG (captures all messages)
- Format: `YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message`

**Example log entry**:
```
2026-03-09 16:55:30 - src.gui.main_window - INFO - Media added successfully
2026-03-09 16:55:31 - src.business.media_service - DEBUG - Retrieved 100 media items
2026-03-09 16:55:32 - src.gui.main_window - ERROR - Failed to add media: Validation error
```

### Console Logging

**Output**: Standard output (terminal/console)

**Features**:
- Real-time feedback during execution
- Configurable log level (default: INFO)
- Simple format: `LEVEL - message`
- Useful for development and debugging

**Example console output**:
```
INFO - Application started
INFO - Database initialized successfully
WARNING - Media already expired at creation time
ERROR - Failed to import data: File not found
```

## Usage Examples

### Example 1: Basic Application Setup

```python
# main.py
import logging
from gui.logging_config import configure_logging
from gui.main_window import MainWindow
import tkinter as tk

def main():
    # Configure logging first
    configure_logging(log_level=logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("Application starting")
    
    try:
        root = tk.Tk()
        app = MainWindow(root)
        app.run()
    except Exception as e:
        logger.critical(f"Application failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

### Example 2: Module-Specific Logging

```python
# src/business/media_service.py
import logging

logger = logging.getLogger(__name__)

class MediaService:
    def create_media(self, name, media_type):
        logger.debug(f"Creating media: {name} ({media_type})")
        
        try:
            # Create media logic
            logger.info(f"Media created: {name}")
            return media
        except Exception as e:
            logger.error(f"Failed to create media: {e}", exc_info=True)
            raise
```

### Example 3: Debug Mode

```python
# Enable DEBUG logging for troubleshooting
from gui.logging_config import configure_logging
import logging

configure_logging(log_level=logging.DEBUG)

# Now all DEBUG messages will appear in console and file
logger = logging.getLogger(__name__)
logger.debug("This debug message will be logged")
```

## Log File Management

### Automatic Rotation

The logging system automatically rotates log files when they reach 10 MB:

1. Current log: `logs/media_archive.log`
2. When 10 MB reached:
   - `media_archive.log` → `media_archive.log.1`
   - New `media_archive.log` created
3. Older backups shift: `.1` → `.2`, `.2` → `.3`, etc.
4. Oldest backup (`.5`) is deleted

### Manual Log Cleanup

To manually clean up old logs:

```bash
# Remove all log files
rm logs/media_archive.log*

# Or keep only current log
rm logs/media_archive.log.[1-5]
```

## Configuration Options

### Modify Log File Location

Edit `src/gui/logging_config.py`:

```python
# Change log directory
log_dir = Path(BASE_DIR) / "custom_logs"  # Instead of "logs"

# Or use absolute path
log_dir = Path("/var/log/media_archive")
```

### Modify Log File Size

Edit `src/gui/logging_config.py`:

```python
# Change max file size (currently 10 MB)
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=50 * 1024 * 1024,  # 50 MB instead of 10 MB
    backupCount=5
)
```

### Modify Backup Count

Edit `src/gui/logging_config.py`:

```python
# Keep more backup files
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,
    backupCount=10  # Keep 10 backups instead of 5
)
```

### Modify Log Format

Edit `src/gui/logging_config.py`:

```python
# Add more information to log format
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

## Troubleshooting

### Logs Not Appearing

1. **Check log level**: Ensure configured level is not higher than message level
   ```python
   configure_logging(log_level=logging.DEBUG)  # Lower level to see more
   ```

2. **Check log file location**: Verify `logs/` directory exists
   ```bash
   ls -la logs/
   ```

3. **Check permissions**: Ensure write permissions to logs directory
   ```bash
   chmod 755 logs/
   ```

### Log File Growing Too Large

1. **Reduce log level**: Use WARNING or ERROR instead of DEBUG
   ```python
   configure_logging(log_level=logging.WARNING)
   ```

2. **Reduce max file size**: Rotate more frequently
   ```python
   maxBytes=5 * 1024 * 1024  # 5 MB instead of 10 MB
   ```

3. **Increase backup count**: Keep more rotated files
   ```python
   backupCount=10  # Keep more backups
   ```

### Missing Log Entries

1. **Check logger name**: Use `__name__` to get correct logger
   ```python
   logger = logging.getLogger(__name__)  # Correct
   logger = logging.getLogger("custom")  # May not work as expected
   ```

2. **Check log level**: Message level must be >= configured level
   ```python
   logger.debug("...")  # Won't appear if level is INFO
   logger.info("...")   # Will appear if level is INFO or lower
   ```

## Best Practices

1. **Use module-level loggers**:
   ```python
   logger = logging.getLogger(__name__)
   ```

2. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Warning messages
   - ERROR: Error messages
   - CRITICAL: Critical errors

3. **Include context in messages**:
   ```python
   logger.info(f"Media created: {media.id} - {media.name}")
   logger.error(f"Failed to save media {media.id}: {error}")
   ```

4. **Use exc_info for exceptions**:
   ```python
   try:
       # code
   except Exception as e:
       logger.error(f"Error: {e}", exc_info=True)  # Includes stack trace
   ```

5. **Configure logging early**:
   ```python
   # In main.py, before creating other components
   configure_logging()
   ```

## Integration with Application

The logging system is integrated into the application startup:

1. **main.py**: Calls `configure_logging()` at startup
2. **All modules**: Use `logging.getLogger(__name__)` for module loggers
3. **Log file**: Automatically created in `logs/media_archive.log`
4. **Console output**: Real-time feedback during execution

## Summary

The logging configuration provides:

✓ Centralized configuration
✓ File and console logging
✓ Automatic log rotation
✓ Configurable log levels
✓ Detailed and simple formats
✓ Easy to use and customize
✓ Production-ready logging system
