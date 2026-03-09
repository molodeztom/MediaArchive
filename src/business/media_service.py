"""Business logic service for Media operations.

This module provides high-level operations for managing media items
with validation and business rule enforcement.
"""

import logging
from datetime import date, timedelta
from typing import Optional

from data.database import Database
from data.media_repository import MediaRepository
from models.enums import MediaType
from models.media import Media
from utils.config import (
    MAX_NAME_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_REMARKS_LENGTH,
    MAX_COMPANY_LENGTH,
    MAX_LICENSE_CODE_LENGTH,
)
from utils.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class MediaService:
    """Service for Media business operations.
    
    Provides CRUD operations with validation and business rule enforcement.
    """

    def __init__(self, database: Database) -> None:
        """Initialize service.
        
        Args:
            database: Database connection manager.
        """
        self._db = database
        self._repo = MediaRepository(database)
        logger.debug("MediaService initialized")

    def create_media(
        self,
        name: str,
        media_type: str,
        number: Optional[str] = None,
        category: Optional[str] = None,
        content_description: Optional[str] = None,
        remarks: Optional[str] = None,
        creation_date: Optional[date] = None,
        valid_until_date: Optional[date] = None,
        company: Optional[str] = None,
        license_code: Optional[str] = None,
        location_id: Optional[int] = None,
    ) -> Media:
        """Create a new media item with validation.
        
        Args:
            name: Media name (required).
            media_type: Type of media (optional, defaults to "Unknown").
            number: Physical media number/identifier (optional).
            category: Content category (Archive, Program, Backup, etc.).
            content_description: Description of contents.
            remarks: Additional notes.
            creation_date: When media was created.
            valid_until_date: Expiration date.
            company: Company/publisher name.
            license_code: License key or activation code.
            location_id: Storage location ID.
        
        Returns:
            Created Media with id set.
        
        Raises:
            ValidationError: If validation fails.
        """
        # Validate inputs
        self._validate_media_input(
            name,
            media_type,
            content_description,
            remarks,
            creation_date,
            valid_until_date,
            company,
            license_code,
        )
        
        # Create media object
        media = Media(
            name=name,
            number=number,
            media_type=media_type,
            category=category,
            content_description=content_description,
            remarks=remarks,
            creation_date=creation_date,
            valid_until_date=valid_until_date,
            company=company,
            license_code=license_code,
            location_id=location_id,
        )
        
        # Save to database
        created = self._repo.create(media)
        logger.info(f"Created media: {created.id} - {created}")
        return created

    def get_media(self, media_id: int) -> Media:
        """Get media by ID.
        
        Args:
            media_id: Media ID.
        
        Returns:
            Media object.
        
        Raises:
            NotFoundError: If media not found.
        """
        try:
            media = self._repo.get_by_id(media_id)
            logger.debug(f"Retrieved media: {media_id}")
            return media
        except NotFoundError:
            logger.warning(f"Media not found: {media_id}")
            raise

    def get_all_media(self) -> list[Media]:
        """Get all media items.
        
        Returns:
            List of Media objects.
        """
        media_list = self._repo.get_all()
        logger.debug(f"Retrieved {len(media_list)} media items")
        return media_list

    def update_media(
        self,
        media_id: int,
        name: Optional[str] = None,
        number: Optional[str] = None,
        media_type: Optional[str] = None,
        category: Optional[str] = None,
        content_description: Optional[str] = None,
        remarks: Optional[str] = None,
        creation_date: Optional[date] = None,
        valid_until_date: Optional[date] = None,
        company: Optional[str] = None,
        license_code: Optional[str] = None,
        location_id: Optional[int] = None,
    ) -> Media:
        """Update an existing media item.
        
        Args:
            media_id: Media ID.
            name: New name (optional).
            number: New physical media number (optional).
            media_type: New type (optional).
            category: New content category (optional).
            content_description: New description (optional).
            remarks: New remarks (optional).
            creation_date: New creation date (optional).
            valid_until_date: New expiration date (optional).
            company: New company (optional).
            license_code: New license code (optional).
            location_id: New location ID (optional).
        
        Returns:
            Updated Media.
        
        Raises:
            NotFoundError: If media not found.
            ValidationError: If validation fails.
        """
        # Get existing media
        media = self._repo.get_by_id(media_id)
        
        # Update fields if provided
        if name is not None:
            media.name = name
        if number is not None:
            media.number = number
        if media_type is not None:
            media.media_type = media_type
        if category is not None:
            media.category = category
        if content_description is not None:
            media.content_description = content_description
        if remarks is not None:
            media.remarks = remarks
        if creation_date is not None:
            media.creation_date = creation_date
        if valid_until_date is not None:
            media.valid_until_date = valid_until_date
        if company is not None:
            media.company = company
        if license_code is not None:
            media.license_code = license_code
        if location_id is not None:
            media.location_id = location_id
        
        # Validate updated media
        self._validate_media_input(
            media.name,
            media.media_type,
            media.content_description,
            media.remarks,
            media.creation_date,
            media.valid_until_date,
            media.company,
            media.license_code,
        )
        
        # Save changes
        updated = self._repo.update(media)
        logger.info(f"Updated media: {media_id}")
        return updated

    def delete_media(self, media_id: int) -> None:
        """Delete a media item.
        
        Args:
            media_id: Media ID.
        
        Raises:
            NotFoundError: If media not found.
        """
        # Check if media exists
        self._repo.get_by_id(media_id)
        
        # Delete media
        self._repo.delete(media_id)
        logger.info(f"Deleted media: {media_id}")

    def search_media_by_name(self, name: str) -> list[Media]:
        """Search media by name.
        
        Args:
            name: Name to search for.
        
        Returns:
            List of matching Media objects.
        
        Raises:
            ValidationError: If search query is empty.
        """
        if not name or not name.strip():
            raise ValidationError("Search query cannot be empty")
        
        results = self._repo.search_by_name(name.strip())
        logger.debug(f"Search found {len(results)} media for name: {name}")
        return results

    def search_media_by_content(self, content: str) -> list[Media]:
        """Search media by content description.
        
        Args:
            content: Content to search for.
        
        Returns:
            List of matching Media objects.
        
        Raises:
            ValidationError: If search query is empty.
        """
        if not content or not content.strip():
            raise ValidationError("Search query cannot be empty")
        
        results = self._repo.search_by_content(content.strip())
        logger.debug(f"Search found {len(results)} media for content: {content}")
        return results

    def get_media_by_type(self, media_type: str) -> list[Media]:
        """Get all media of a specific type.
        
        Args:
            media_type: Media type.
        
        Returns:
            List of Media objects.
        
        Raises:
            ValidationError: If media type is invalid.
        """
        if not MediaType.is_valid(media_type):
            raise ValidationError(f"Invalid media type: {media_type}")
        
        results = self._repo.search_by_type(media_type)
        logger.debug(f"Found {len(results)} media of type: {media_type}")
        return results

    def get_media_by_location(self, location_id: int) -> list[Media]:
        """Get all media in a specific location.
        
        Args:
            location_id: Storage location ID.
        
        Returns:
            List of Media objects.
        """
        results = self._repo.search_by_location(location_id)
        logger.debug(f"Found {len(results)} media in location: {location_id}")
        return results

    def get_media_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Media]:
        """Get media created within a date range.
        
        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
        
        Returns:
            List of Media objects.
        
        Raises:
            ValidationError: If date range is invalid.
        """
        if start_date > end_date:
            raise ValidationError("Start date must be before end date")
        
        results = self._repo.search_by_creation_date(start_date, end_date)
        logger.debug(f"Found {len(results)} media between {start_date} and {end_date}")
        return results

    def get_expired_media(self) -> list[Media]:
        """Get all expired media.
        
        Returns:
            List of expired Media objects.
        """
        results = self._repo.get_expired_media()
        logger.debug(f"Found {len(results)} expired media")
        return results

    def get_expiring_soon(self, days: int = 30) -> list[Media]:
        """Get media expiring within specified days.
        
        Args:
            days: Number of days to look ahead (default 30).
        
        Returns:
            List of Media objects expiring soon.
        
        Raises:
            ValidationError: If days is invalid.
        """
        if days <= 0:
            raise ValidationError("Days must be greater than 0")
        
        results = self._repo.get_expiring_soon(days)
        logger.debug(f"Found {len(results)} media expiring in {days} days")
        return results

    def get_media_statistics(self) -> dict:
        """Get statistics about media collection.
        
        Returns:
            Dictionary with statistics.
        """
        all_media = self._repo.get_all()
        expired = self._repo.get_expired_media()
        expiring_soon = self._repo.get_expiring_soon(30)
        
        # Count by type
        by_type = {}
        for media in all_media:
            by_type[media.media_type] = by_type.get(media.media_type, 0) + 1
        
        stats = {
            "total_media": len(all_media),
            "expired_media": len(expired),
            "expiring_soon": len(expiring_soon),
            "media_by_type": by_type,
            "media_with_location": sum(1 for m in all_media if m.has_location()),
            "media_without_location": sum(1 for m in all_media if not m.has_location()),
        }
        
        logger.debug(f"Media statistics: {stats}")
        return stats

    @staticmethod
    def _validate_media_input(
        name: str,
        media_type: str,
        content_description: Optional[str] = None,
        remarks: Optional[str] = None,
        creation_date: Optional[date] = None,
        valid_until_date: Optional[date] = None,
        company: Optional[str] = None,
        license_code: Optional[str] = None,
    ) -> None:
        """Validate media input fields.
        
        Args:
            name: Media name.
            media_type: Media type.
            content_description: Content description.
            remarks: Remarks.
            creation_date: Creation date.
            valid_until_date: Expiration date.
            company: Company name.
            license_code: License code.
        
        Raises:
            ValidationError: If validation fails.
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Media name is required")
        if len(name) > MAX_NAME_LENGTH:
            raise ValidationError(f"Name exceeds {MAX_NAME_LENGTH} characters")
        
        # Validate media type (optional, defaults to "Unknown")
        if media_type:
            media_type = media_type.strip()
            if not MediaType.is_valid(media_type):
                raise ValidationError(f"Invalid media type: {media_type}")
        else:
            media_type = "Unknown"
        
        # Validate content description
        if content_description and len(content_description) > MAX_DESCRIPTION_LENGTH:
            raise ValidationError(f"Description exceeds {MAX_DESCRIPTION_LENGTH} characters")
        
        # Validate remarks
        if remarks and len(remarks) > MAX_REMARKS_LENGTH:
            raise ValidationError(f"Remarks exceed {MAX_REMARKS_LENGTH} characters")
        
        # Validate company
        if company and len(company) > MAX_COMPANY_LENGTH:
            raise ValidationError(f"Company name exceeds {MAX_COMPANY_LENGTH} characters")
        
        # Validate license code
        if license_code and len(license_code) > MAX_LICENSE_CODE_LENGTH:
            raise ValidationError(f"License code exceeds {MAX_LICENSE_CODE_LENGTH} characters")
        
        # Validate dates
        if creation_date and valid_until_date:
            if creation_date > valid_until_date:
                raise ValidationError("Creation date must be before expiration date")
        
        if valid_until_date and valid_until_date < date.today():
            logger.warning("Media already expired at creation time")
