"""Encoding detection utility for CSV files.

This module provides encoding detection for CSV files, particularly those
exported from Microsoft Access which often use Windows-1252 (ANSI) encoding.

History:
20260308  V1.0: Initial encoding detector implementation
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class EncodingDetector:
    """Detects file encoding with fallback mechanisms."""
    
    # Encoding priority list for CSV files
    ENCODING_PRIORITY = [
        'utf-8',           # Try UTF-8 first
        'utf-8-sig',       # UTF-8 with BOM
        'windows-1252',    # Windows ANSI (common for Access exports)
        'iso-8859-1',      # Latin-1 (fallback)
        'cp1252',          # Windows Western European
        'latin-1',         # Alias for iso-8859-1
    ]
    
    @staticmethod
    def detect_encoding(file_path: str | Path) -> str:
        """Detect file encoding by trying multiple encodings.
        
        Args:
            file_path: Path to the file to detect encoding for.
        
        Returns:
            Detected encoding name.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}, defaulting to utf-8")
            return 'utf-8'
        
        # Try each encoding in priority order
        for encoding in EncodingDetector.ENCODING_PRIORITY:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # Try to read the entire file
                    f.read()
                
                logger.debug(f"Detected encoding for {file_path.name}: {encoding}")
                return encoding
                
            except (UnicodeDecodeError, LookupError) as e:
                logger.debug(f"Encoding {encoding} failed for {file_path.name}: {e}")
                continue
        
        # If all encodings fail, default to utf-8 with error handling
        logger.warning(f"Could not detect encoding for {file_path.name}, defaulting to utf-8 with error handling")
        return 'utf-8'
    
    @staticmethod
    def read_file_with_fallback(file_path: str | Path) -> tuple[str, str]:
        """Read file content with automatic encoding detection and fallback.
        
        Args:
            file_path: Path to the file to read.
        
        Returns:
            Tuple of (file_content, encoding_used).
        
        Raises:
            IOError: If file cannot be read with any encoding.
        """
        file_path = Path(file_path)
        
        # Try each encoding in priority order
        for encoding in EncodingDetector.ENCODING_PRIORITY:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                logger.info(f"Successfully read {file_path.name} with encoding: {encoding}")
                return content, encoding
                
            except (UnicodeDecodeError, LookupError) as e:
                logger.debug(f"Failed to read {file_path.name} with {encoding}: {e}")
                continue
        
        # Last resort: read with utf-8 and replace errors
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            logger.warning(f"Read {file_path.name} with utf-8 and error replacement")
            return content, 'utf-8-replace'
            
        except Exception as e:
            logger.error(f"Failed to read {file_path.name} with any encoding: {e}")
            raise IOError(f"Cannot read file {file_path.name}: {e}") from e
