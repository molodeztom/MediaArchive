"""CSV mapper for importing data from Microsoft Access database format.

This module provides mapping and conversion utilities for importing media data
from the specific Access database CSV export format used in the Media Archive.

History:
20260308  V1.0: Initial Access CSV mapper implementation
20260308  V1.1: Added location mapper for Box;Ort;Typ format with internal ID generation
20260308  V1.2: Removed media type requirement - empty types map to "Other"
20260308  V1.3: Changed to store Art as Type in content_description, media_type defaults to DVD
20260308  V1.4: Store Art value in separate type field instead of content_description
20260308  V1.5: Allow locations with empty Ort/Typ - only Box ID is required
20260308  V1.6: Rename AccessMediaTypeMapper to AccessContentTypeMapper for clarity
20260308  V1.7: Rename AccessContentTypeMapper to AccessCategoryMapper, store ID as number
"""

import logging
from datetime import date
from typing import Optional, Dict, List, Tuple
from pathlib import Path

from models.media import Media
from models.location import StorageLocation
from utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


class AccessCategoryMapper:
    """Maps Access content categories (Art field) to Media Archive content categories.
    
    Note: This maps the "Art" field from Access (Archive, Program, Backup, Game, etc.)
    to content categories stored in the Media.category field. This is different from
    media_type which represents the physical storage medium (DVD, CD, USB-Stick, etc.).
    """
    
    # Mapping from Access Art values to content categories
    # These are content categories, not storage media types
    CATEGORY_MAPPING = {
        "Archive": "Archive",      # Archive content
        "Image": "Image",          # Image/photo content
        "Lexica": "Lexica",        # Reference/lexicon content
        "Program": "Program",      # Software/program content
        "Backup": "Backup",        # Backup content
        "Game": "Game",            # Game content
    }
    
    # Valid content categories in Access
    VALID_CATEGORIES = [
        "Archive", "Image", "Lexica", "Program", "Backup", "Game", "Other"
    ]

    @staticmethod
    def map_category(access_category: str) -> Optional[str]:
        """Map Access content category (Art field) to Media Archive content category.
        
        Args:
            access_category: Content category from Access (Archive, Image, Lexica, Program, Backup, Game, Other)
        
        Returns:
            Content category or None if empty
        """
        if not access_category or not access_category.strip():
            return None
        
        access_category = access_category.strip()
        
        # Check if it's a valid Access category
        if access_category not in AccessCategoryMapper.VALID_CATEGORIES:
            logger.warning(f"Unknown Access content category: {access_category}, using as-is")
            return access_category
        
        # Map to content category
        mapped_category = AccessCategoryMapper.CATEGORY_MAPPING.get(access_category, access_category)
        logger.debug(f"Mapped Access content category '{access_category}' to '{mapped_category}'")
        
        return mapped_category


class AccessDateConverter:
    """Converts dates from Access CSV format to ISO format."""
    
    @staticmethod
    def convert_date(date_str: str) -> Optional[date]:
        """Convert date from DD.MM.YYYY format to date object.
        
        Args:
            date_str: Date string in DD.MM.YYYY format (time part is ignored)
        
        Returns:
            date object or None if date_str is empty/invalid
        
        Raises:
            ValidationError: If date format is invalid
        """
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        # Remove time part if present (DD.MM.YYYY hh:mm)
        if " " in date_str:
            date_str = date_str.split(" ")[0]
        
        try:
            # Parse DD.MM.YYYY format
            parts = date_str.split(".")
            if len(parts) != 3:
                raise ValueError(f"Invalid date format: {date_str}")
            
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            
            # Create date object
            result = date(year, month, day)
            logger.debug(f"Converted date '{date_str}' to {result.isoformat()}")
            
            return result
            
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse date '{date_str}': {e}")
            raise ValidationError(f"Invalid date format: {date_str}. Expected DD.MM.YYYY")


class AccessCSVMapper:
    """Maps Access CSV format to Media Archive format."""
    
    # Column indices in Access CSV
    # ID; Name; Firma; Box; Position; Code; Art; Bemerkung; Datum; Verfällt am
    COLUMN_MAPPING = {
        "id": 0,
        "name": 1,
        "company": 2,
        "box": 3,
        "place": 4,
        "license_code": 5,
        "category": 6,
        "content_description": 7,
        "creation_date": 8,
        "valid_until_date": 9,
    }

    @staticmethod
    def parse_media_row(
        row: List[str],
        locations: List[StorageLocation],
        external_id_map: Optional[Dict[int, int]] = None,
    ) -> Tuple[Optional[Media], Optional[str]]:
        """Parse a single media row from Access CSV.
        
        Args:
            row: CSV row as list of strings
            locations: List of available storage locations for lookup
            external_id_map: Optional mapping of external IDs to internal IDs
        
        Returns:
            Tuple of (Media object or None, error message or None)
        """
        try:
            # Ensure row has enough columns
            if len(row) < 10:
                return None, f"Row has insufficient columns: {len(row)} < 10"
            
            # Extract fields
            external_id_str = row[AccessCSVMapper.COLUMN_MAPPING["id"]].strip()
            name = row[AccessCSVMapper.COLUMN_MAPPING["name"]].strip()
            company = row[AccessCSVMapper.COLUMN_MAPPING["company"]].strip() or None
            box = row[AccessCSVMapper.COLUMN_MAPPING["box"]].strip()
            place = row[AccessCSVMapper.COLUMN_MAPPING["place"]].strip()
            license_code = row[AccessCSVMapper.COLUMN_MAPPING["license_code"]].strip() or None
            access_art = row[AccessCSVMapper.COLUMN_MAPPING["category"]].strip()  # "Art" field from Access
            bemerkung = row[AccessCSVMapper.COLUMN_MAPPING["content_description"]].strip() or None  # "Bemerkung" field
            creation_date_str = row[AccessCSVMapper.COLUMN_MAPPING["creation_date"]].strip()
            valid_until_str = row[AccessCSVMapper.COLUMN_MAPPING["valid_until_date"]].strip()
            
            # Validate required fields
            if not name:
                return None, "Name is required"
            
            # Store Access "ID" column as number field
            number = external_id_str if external_id_str else None
            
            # Set media_type to "Unknown" as default (not in Access CSV)
            media_type = "Unknown"
            
            # Store Access "Art" value in category field
            category_value = access_art if access_art else None
            
            # Use "Bemerkung" as content_description
            content_description = bemerkung if bemerkung else None
            
            # Convert dates
            try:
                creation_date = AccessDateConverter.convert_date(creation_date_str)
            except ValidationError as e:
                return None, f"Invalid creation date: {str(e)}"
            
            try:
                valid_until_date = AccessDateConverter.convert_date(valid_until_str)
            except ValidationError as e:
                return None, f"Invalid valid until date: {str(e)}"
            
            # Find location by box and place
            location_id = None
            if box and place:
                for loc in locations:
                    if loc.box == box and loc.place == place:
                        location_id = loc.id
                        break
                
                if location_id is None:
                    logger.warning(f"Location not found for Box='{box}', Place='{place}'")
            
            # Create media object
            media = Media(
                name=name,
                number=number,
                media_type=media_type,
                category=category_value,
                company=company,
                license_code=license_code,
                creation_date=creation_date,
                valid_until_date=valid_until_date,
                content_description=content_description,
                remarks=None,  # Not in Access CSV
                location_id=location_id,
            )
            
            logger.debug(f"Parsed media: {name} (type={media_type}, location_id={location_id})")
            
            return media, None
            
        except Exception as e:
            logger.error(f"Error parsing media row: {e}")
            return None, f"Error parsing row: {str(e)}"

    @staticmethod
    def parse_media_rows(
        rows: List[List[str]],
        locations: List[StorageLocation],
        skip_header: bool = True,
    ) -> Tuple[List[Media], List[str]]:
        """Parse multiple media rows from Access CSV.
        
        Args:
            rows: List of CSV rows
            locations: List of available storage locations
            skip_header: Whether to skip first row (header)
        
        Returns:
            Tuple of (list of Media objects, list of error messages)
        """
        media_list = []
        errors = []
        
        start_row = 1 if skip_header else 0
        
        for i, row in enumerate(rows[start_row:], start=start_row + 1):
            media, error = AccessCSVMapper.parse_media_row(row, locations)
            
            if error:
                errors.append(f"Row {i}: {error}")
            elif media:
                media_list.append(media)
        
        logger.info(f"Parsed {len(media_list)} media items with {len(errors)} errors")
        
        return media_list, errors


class AccessLocationMapper:
    """Maps Access location format to Media Archive format.
    
    Supports two formats:
    1. Old format: Box; Place; Detail
    2. New format: Box; Ort; Typ (with internal ID generation)
    """
    
    # Column indices in Access locations CSV
    # Format 1 (old): Box; Place; Detail
    # Format 2 (new): Box; Ort; Typ
    COLUMN_MAPPING = {
        "box": 0,
        "place": 1,
        "detail": 2,
    }

    @staticmethod
    def parse_location_row(
        row: List[str],
        internal_id: Optional[int] = None,
    ) -> Tuple[Optional[StorageLocation], Optional[str]]:
        """Parse a single location row from Access CSV.
        
        Accepts locations with only Box ID, even if Ort/Place and Typ/Detail are empty.
        This allows importing all locations from the CSV, including those with minimal data.
        
        Args:
            row: CSV row as list of strings
            internal_id: Optional internal ID for the location (not displayed to user)
        
        Returns:
            Tuple of (StorageLocation object or None, error message or None)
        """
        try:
            # Ensure row has enough columns (only box is required)
            if len(row) < 1:
                return None, f"Row has insufficient columns: {len(row)} < 1"
            
            # Extract fields
            # Box column contains the visible box number (e.g., "1", "2", "Box 1")
            # This is the only required field - it serves as the location ID reference
            box = row[AccessLocationMapper.COLUMN_MAPPING["box"]].strip()
            # Place/Ort column contains the location (e.g., "Shelf A", "Regal 1") - optional
            place = row[AccessLocationMapper.COLUMN_MAPPING["place"]].strip() if len(row) > 1 else ""
            # Detail/Typ column contains optional details
            detail = row[AccessLocationMapper.COLUMN_MAPPING["detail"]].strip() if len(row) > 2 else None
            
            # Validate required fields
            if not box:
                return None, "Box is required"
            
            # Place is optional - set to empty string if not provided
            if not place:
                place = ""
            
            # Create location object
            # The box field remains visible to the user for physical reference
            location = StorageLocation(
                box=box,
                place=place,
                detail=detail or None,
            )
            
            # Set internal ID if provided (not displayed to user)
            if internal_id is not None:
                location.id = internal_id
            
            logger.debug(f"Parsed location: {box} / {place} (internal_id={internal_id})")
            
            return location, None
            
        except Exception as e:
            logger.error(f"Error parsing location row: {e}")
            return None, f"Error parsing row: {str(e)}"

    @staticmethod
    def parse_location_rows(
        rows: List[List[str]],
        skip_header: bool = True,
        generate_internal_ids: bool = True,
    ) -> Tuple[List[StorageLocation], List[str]]:
        """Parse multiple location rows from Access CSV.
        
        Args:
            rows: List of CSV rows
            skip_header: Whether to skip first row (header)
            generate_internal_ids: Whether to generate internal IDs for locations
        
        Returns:
            Tuple of (list of StorageLocation objects, list of error messages)
        """
        location_list = []
        errors = []
        
        start_row = 1 if skip_header else 0
        internal_id_counter = 1
        
        for i, row in enumerate(rows[start_row:], start=start_row + 1):
            internal_id = internal_id_counter if generate_internal_ids else None
            location, error = AccessLocationMapper.parse_location_row(row, internal_id=internal_id)
            
            if error:
                errors.append(f"Row {i}: {error}")
            elif location:
                location_list.append(location)
                internal_id_counter += 1
        
        logger.info(f"Parsed {len(location_list)} locations with {len(errors)} errors")
        
        return location_list, errors
