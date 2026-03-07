"""Application entry point for Media Archive Manager.

This module initializes the application, sets up logging, and starts the GUI.
"""

import logging
import sys
import tkinter as tk
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import LOG_FILE, LOG_LEVEL, APP_NAME, APP_VERSION
from gui.main_window import MainWindow


def setup_logging() -> None:
    """Configure application logging.
    
    Sets up logging to both file and console with appropriate formatting.
    """
    log_level = getattr(logging, LOG_LEVEL, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(),
        ],
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"{APP_NAME} v{APP_VERSION} starting")


def main() -> None:
    """Main application entry point.
    
    Initializes logging and starts the GUI.
    """
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Application initialized successfully")
        
        # Create root window
        root = tk.Tk()
        
        # Create main window
        app = MainWindow(root)
        
        # Run application
        app.run()
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.critical(f"Application startup failed: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
