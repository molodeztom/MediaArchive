"""Logging configuration for Media Archive Manager.

This module provides centralized logging configuration for the application.

History:
20260309  V1.0: Initial logging configuration
20260309  V1.1: Phase 9E - Added dynamic logging control
20260309  V1.2: Made logging preferences persistent via database
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from utils.config import BASE_DIR

# Global logging state
_logging_enabled = True
_log_level = logging.INFO
_preferences_repo = None


def set_preferences_repo(repo) -> None:
    """Set the preferences repository for persistent storage.
    
    Args:
        repo: PreferencesRepository instance.
    """
    global _preferences_repo
    _preferences_repo = repo


def configure_logging(log_level: int = logging.INFO, enabled: bool = True, preferences_repo=None) -> None:
    """Configure logging for the application.
    
    Sets up both file and console logging with appropriate formatters.
    
    Args:
        log_level: Logging level (default: logging.INFO).
        enabled: Whether logging should be enabled (default: True).
        preferences_repo: Optional PreferencesRepository for persistent storage.
    """
    global _logging_enabled, _log_level, _preferences_repo
    _logging_enabled = enabled
    _log_level = log_level
    if preferences_repo:
        _preferences_repo = preferences_repo
    
    # Create logs directory if it doesn't exist
    log_dir = Path(BASE_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    if not enabled:
        # Disable logging by setting to CRITICAL
        logger.setLevel(logging.CRITICAL)
        logger.info("Logging disabled")
        return
    
    logger.setLevel(log_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (rotating)
    log_file = log_dir / "media_archive.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    logger.info("Logging configured successfully")
    logger.info(f"Log file: {log_file}")


def set_logging_enabled(enabled: bool) -> None:
    """Enable or disable logging dynamically.
    
    Args:
        enabled: Whether logging should be enabled.
    """
    global _logging_enabled
    _logging_enabled = enabled
    
    # Save to database if preferences repo is available
    if _preferences_repo:
        try:
            _preferences_repo.set_logging_enabled(enabled)
        except Exception as e:
            logging.error(f"Failed to save logging enabled preference: {e}")
    
    logger = logging.getLogger()
    if enabled:
        logger.setLevel(_log_level)
    else:
        logger.setLevel(logging.CRITICAL)


def set_logging_level(level: int) -> None:
    """Set logging level dynamically.
    
    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.).
    """
    global _log_level
    _log_level = level
    
    # Convert logging level to string for storage
    level_map = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL"
    }
    level_str = level_map.get(level, "INFO")
    
    # Save to database if preferences repo is available
    if _preferences_repo:
        try:
            _preferences_repo.set_logging_level(level_str)
        except Exception as e:
            logging.error(f"Failed to save logging level preference: {e}")
    
    logger = logging.getLogger()
    if _logging_enabled:
        logger.setLevel(level)
        
        # Update console handler level
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.setLevel(level)


def is_logging_enabled() -> bool:
    """Check if logging is currently enabled.
    
    Returns:
        True if logging is enabled, False otherwise.
    """
    return _logging_enabled
