"""Application configuration for Media Archive Manager.

This module defines all configuration constants used throughout the application.
Centralized configuration makes it easy to adjust settings without modifying code.
"""

from pathlib import Path

# ============================================================================
# Application Paths
# ============================================================================

# Base directory is the project root (parent of src/)
# For PyInstaller: use the directory where the executable is located
import sys
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as Python script
    BASE_DIR = Path(__file__).parent.parent.parent

# Data directory for database files
DATA_DIR = BASE_DIR / "data"

# Database file path
DB_PATH = DATA_DIR / "media_archive.db"

# Log file path
LOG_FILE = BASE_DIR / "media_archive.log"

# ============================================================================
# Database Settings
# ============================================================================

# Database connection timeout (seconds)
DB_TIMEOUT = 5.0

# Allow database access from multiple threads (False for single-threaded)
DB_CHECK_SAME_THREAD = False

# ============================================================================
# Validation Limits
# ============================================================================

# Media name maximum length
MAX_NAME_LENGTH = 200

# Content description maximum length
MAX_DESCRIPTION_LENGTH = 2000

# Remarks maximum length
MAX_REMARKS_LENGTH = 2000

# Storage location box name maximum length
MAX_BOX_LENGTH = 100

# Storage location place maximum length
MAX_PLACE_LENGTH = 100

# Storage location detail maximum length
MAX_DETAIL_LENGTH = 200

# Company name maximum length
MAX_COMPANY_LENGTH = 100

# License code maximum length
MAX_LICENSE_CODE_LENGTH = 200

# Maximum number of items to load/display (Phase 9F performance optimization)
MAX_ITEMS = 3000

# ============================================================================
# UI Settings
# ============================================================================

# Main window default width (pixels)
WINDOW_WIDTH = 1024

# Main window default height (pixels)
WINDOW_HEIGHT = 768

# Table row height (pixels)
TABLE_ROW_HEIGHT = 25

# ============================================================================
# Logging Settings
# ============================================================================

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# Application Metadata
# ============================================================================

# Application name
APP_NAME = "Media Archive Manager"

# Application version
APP_VERSION = "2.0.0"

# Application description
APP_DESCRIPTION = "Local desktop application for managing physical media inventory"

# ============================================================================
# Feature Flags
# ============================================================================

# Enable debug mode (more verbose logging)
DEBUG = False

# Enable experimental features
EXPERIMENTAL_FEATURES = False
