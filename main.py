"""Application entry point for Media Archive Manager.

This module initializes the application, sets up logging, and starts the GUI.
"""

import logging
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import LOG_FILE, LOG_LEVEL, APP_NAME, APP_VERSION


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
        logger.info("Phase 1: Project Setup - Complete")
        logger.info("Next: Phase 2 - Database Layer Implementation")
        
        print(f"\n{APP_NAME} v{APP_VERSION}")
        print("=" * 50)
        print("Phase 1: Project Setup - Complete ✓")
        print("\nProject structure created:")
        print("  ✓ src/models/ - Data models (Media, StorageLocation, MediaType)")
        print("  ✓ src/utils/ - Configuration and exceptions")
        print("  ✓ tests/ - Test suite directory")
        print("  ✓ data/ - Database directory")
        print("  ✓ requirements.txt - Dependencies (minimal)")
        print("\nNext steps:")
        print("  1. Phase 2: Implement database layer")
        print("  2. Phase 3: Implement business logic")
        print("  3. Phase 4: Implement GUI")
        print("\nFor more information, see docs/TASKS.md")
        print("=" * 50 + "\n")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.critical(f"Application startup failed: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
