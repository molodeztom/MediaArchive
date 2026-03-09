"""Logging configuration for Media Archive Manager.

This module provides centralized logging configuration for the application.

History:
20260309  V1.0: Initial logging configuration
"""

import logging
import logging.handlers
from pathlib import Path
from utils.config import BASE_DIR


def configure_logging(log_level: int = logging.INFO) -> None:
    """Configure logging for the application.
    
    Sets up both file and console logging with appropriate formatters.
    
    Args:
        log_level: Logging level (default: logging.INFO).
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(BASE_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
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
