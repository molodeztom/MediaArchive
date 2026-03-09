"""Business logic service for Media operations.

This module provides high-level operations for managing media items
with validation and business rule enforcement.

History:
20260309  V1.0: Added assign_locations_by_box_place method for location assignment
20260309  V1.1: Added place parameter to create_media and update_media methods
20260309  V1.2: Fixed log message in assign_locations_by_box_place - use real_location_id
20260309  V1.3: Fixed location assignment to avoid duplicate assignments
20260309  V1.4: Fixed location assignment to correctly resolve box references
20260309  V1.5: Added position parameter to update_media method
20260309  V1.6: Added get_unique_categories method for category dropdown
20260309  V1.7: Added get_next_number method for auto-numbering
20260309  V1.8: Added soft delete support (delete_media_soft, restore_media, delete_media_permanent)
20260309  V1.9: Updated get_media_statistics to exclude deleted items and add deleted count
20260309  V1.10: Added include_deleted parameter to search_media_by_name
20260309  V1.11: Phase 9A complete - auto-numbering and date format support
20260309  V1.12: Phase 9D - Added batch_update_media method for multi-select operations
20260309  V1.13: Phase 9E - Added auto-set creation date support
20260309  V1.14: Phase 9F - Added max_items limit (3000) for performance optimization
"""

import logging
from datetime import date, timedelta
from typing import Optional, List

from data.database import Database
from data.media_repository import MediaRepository
from models.enums import MediaType
from models.media import Media
from models.location import StorageLocation
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
        position: Optional[str] = None,
        auto_set_creation_date: bool = True,
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
            license_code: Optional license key or activation code.
            location_id: Storage location ID.
            position: Position within storage location.
            auto_set_creation_date: If True and creation_date is None, set to today.
        
        Returns:
            Created Media with id set.
        
        Raises:
            ValidationError: If validation fails.
        """
        # Auto-set creation date to today if not provided
        if auto_set_creation_date and creation_date is None:
            creation_date = date.today()
            logger.debug(f"Auto-set creation date to today: {creation_date}")
        
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
            position=position,
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

    def get_all_media(self, include_deleted: bool = False) -> list[Media]:
        """Get all media items.
        
        Args:
            include_deleted: If True, include soft-deleted items. Default False.
        
        Returns:
            List of Media objects.
        """
        media_list = self._repo.get_all(include_deleted=include_deleted)
        logger.debug(f"Retrieved {len(media_list)} media items (include_deleted={include_deleted})")
        return media_list
    
    def get_deleted_media(self) -> list[Media]:
        """Get all soft-deleted media items.
        
        Returns:
            List of deleted Media objects.
        """
        media_list = self._repo.get_deleted_media()
        logger.debug(f"Retrieved {len(media_list)} deleted media items")
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
        position: Optional[str] = None,
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
            position: New position within location (optional).
        
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
        if position is not None:
            media.position = position
        
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
        """Delete a media item (soft delete - marks as deleted).
        
        Args:
            media_id: Media ID.
        
        Raises:
            NotFoundError: If media not found.
        """
        # Check if media exists
        self._repo.get_by_id(media_id)
        
        # Soft delete media
        self._repo.delete(media_id)
        logger.info(f"Soft deleted media: {media_id}")
    
    def delete_media_soft(self, media_id: int) -> None:
        """Soft delete a media item (mark as deleted).
        
        Args:
            media_id: Media ID.
        
        Raises:
            NotFoundError: If media not found.
        """
        self.delete_media(media_id)
    
    def restore_media(self, media_id: int) -> None:
        """Restore a soft-deleted media item.
        
        Args:
            media_id: Media ID.
        
        Raises:
            NotFoundError: If media not found.
        """
        # Check if media exists
        self._repo.get_by_id(media_id)
        
        # Restore media
        self._repo.restore(media_id)
        logger.info(f"Restored media: {media_id}")
    
    def delete_media_permanent(self, media_id: int) -> None:
        """Permanently delete a media item from database.
        
        Args:
            media_id: Media ID.
        
        Raises:
            NotFoundError: If media not found.
        """
        # Check if media exists
        self._repo.get_by_id(media_id)
        
        # Permanently delete media
        self._repo.permanent_delete(media_id)
        logger.info(f"Permanently deleted media: {media_id}")

    def search_media_by_name(self, name: str, include_deleted: bool = False) -> list[Media]:
        """Search media by name.
        
        Args:
            name: Name to search for.
            include_deleted: If True, include soft-deleted items. Default False.
        
        Returns:
            List of matching Media objects.
        
        Raises:
            ValidationError: If search query is empty.
        """
        if not name or not name.strip():
            raise ValidationError("Search query cannot be empty")
        
        results = self._repo.search_by_name(name.strip(), include_deleted=include_deleted)
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
            Dictionary with statistics (excludes deleted items by default).
        """
        # Get active media (not deleted)
        all_media = self._repo.get_all(include_deleted=False)
        
        # Get deleted media separately
        deleted_media = self._repo.get_deleted_media()
        
        expired = self._repo.get_expired_media(include_deleted=False)
        expiring_soon = self._repo.get_expiring_soon(30, include_deleted=False)
        
        # Count by type (active only)
        by_type = {}
        for media in all_media:
            by_type[media.media_type] = by_type.get(media.media_type, 0) + 1
        
        stats = {
            "total_media": len(all_media),
            "deleted_media": len(deleted_media),
            "expired_media": len(expired),
            "expiring_soon": len(expiring_soon),
            "media_by_type": by_type,
            "media_with_location": sum(1 for m in all_media if m.has_location()),
            "media_without_location": sum(1 for m in all_media if not m.has_location()),
        }
        
        logger.debug(f"Media statistics: {stats}")
        return stats

    def get_unique_categories(self) -> list[str]:
        """Get list of unique categories from all media.
        
        Returns:
            Sorted list of unique category values.
        """
        categories = self._repo.get_unique_categories()
        logger.debug(f"Retrieved {len(categories)} unique categories")
        return categories

    def get_next_number(self) -> str:
        """Get the next available media number for auto-numbering.
        
        Queries the database for the highest numeric number and returns
        the next sequential number. Handles edge cases like empty database
        and non-numeric numbers.
        
        Returns:
            Next available number as string (e.g., "1", "2", "100").
            Returns "1" if database is empty or no numeric numbers exist.
        """
        try:
            all_media = self._repo.get_all()
            
            if not all_media:
                logger.debug("Database is empty, returning next number: 1")
                return "1"
            
            # Extract numeric numbers from all media
            numeric_numbers = []
            for media in all_media:
                if media.number:
                    try:
                        num = int(media.number)
                        numeric_numbers.append(num)
                    except ValueError:
                        # Skip non-numeric numbers
                        logger.debug(f"Skipping non-numeric number: {media.number}")
                        continue
            
            if not numeric_numbers:
                logger.debug("No numeric numbers found, returning next number: 1")
                return "1"
            
            # Get the highest number and increment
            max_number = max(numeric_numbers)
            next_number = max_number + 1
            logger.debug(f"Next available number: {next_number}")
            return str(next_number)
            
        except Exception as e:
            logger.error(f"Error getting next number: {e}")
            # Return "1" as fallback
            return "1"
    
    def batch_update_media(self, media_ids: List[int], updates: dict) -> int:
        """Update multiple media items with the same values.
        
        Args:
            media_ids: List of media IDs to update.
            updates: Dictionary with fields to update (media_type, category, valid_until_date).
        
        Returns:
            Number of media items updated.
        
        Raises:
            ValidationError: If validation fails.
        """
        if not media_ids:
            raise ValidationError("No media items selected")
        
        if not updates:
            raise ValidationError("No fields to update")
        
        updated_count = 0
        for media_id in media_ids:
            try:
                # Get existing media
                media = self._repo.get_by_id(media_id)
                
                # Update fields from updates dict
                if "media_type" in updates:
                    media.media_type = updates["media_type"]
                if "category" in updates:
                    media.category = updates["category"]
                if "valid_until_date" in updates:
                    media.valid_until_date = updates["valid_until_date"]
                
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
                self._repo.update(media)
                updated_count += 1
                logger.debug(f"Batch updated media {media_id}: {updates}")
            except Exception as e:
                logger.warning(f"Failed to batch update media {media_id}: {e}")
                continue
        
        logger.info(f"Batch updated {updated_count} media items")
        return updated_count
    
    def batch_delete_media(self, media_ids: List[int]) -> int:
        """Soft delete multiple media items.
        
        Args:
            media_ids: List of media IDs to delete.
        
        Returns:
            Number of media items deleted.
        """
        if not media_ids:
            raise ValidationError("No media items selected")
        
        deleted_count = 0
        for media_id in media_ids:
            try:
                # Check if media exists
                self._repo.get_by_id(media_id)
                
                # Soft delete media
                self._repo.delete(media_id)
                deleted_count += 1
                logger.debug(f"Batch deleted media {media_id}")
            except Exception as e:
                logger.warning(f"Failed to batch delete media {media_id}: {e}")
                continue
        
        logger.info(f"Batch deleted {deleted_count} media items")
        return deleted_count
    
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
    
    def assign_locations_by_box_place(self, locations: List[StorageLocation]) -> dict:
        """Assign locations to media by resolving box number references to location IDs.
        
        During media import, the box number from CSV is stored as location_id.
        This method finds the correct location by matching box numbers and updates
        the media to point to the correct location ID.
        
        Strategy: For each media, if there exists a location where location.box equals
        the media.location_id value, then update media to point to that location's ID.
        
        Args:
            locations: List of available storage locations
        
        Returns:
            Dictionary with assignment statistics:
            - total_media: Total media items checked
            - assigned: Number of media assigned/updated
            - already_assigned: Number that were already correct
            - not_found: Number where matching location wasn't found
            - updated_media: List of updated media IDs
        """
        stats = {
            "total_media": 0,
            "assigned": 0,
            "already_assigned": 0,
            "not_found": 0,
            "updated_media": []
        }
        
        try:
            # Get all media
            all_media = self.get_all_media()
            stats["total_media"] = len(all_media)
            
            # Create mapping: box_number -> location.id
            box_to_location_id = {}
            for loc in locations:
                try:
                    box_num = int(loc.box) if isinstance(loc.box, str) else loc.box
                    box_to_location_id[box_num] = loc.id
                    logger.debug(f"Location mapping: box {box_num} -> location_id {loc.id}")
                except (ValueError, TypeError):
                    logger.warning(f"Location box '{loc.box}' is not a valid integer")
            
            logger.debug(f"Created location map with {len(box_to_location_id)} entries")
            
            # Process each media item
            for media in all_media:
                if media.location_id is None:
                    stats["not_found"] += 1
                    continue
                
                # Check if there's a location with box number == media.location_id
                # If yes, update media to point to that location's ID
                if media.location_id in box_to_location_id:
                    correct_location_id = box_to_location_id[media.location_id]
                    
                    # Only update if it's different
                    if media.location_id != correct_location_id:
                        old_location_id = media.location_id
                        media.location_id = correct_location_id
                        self._repo.update(media)
                        stats["assigned"] += 1
                        stats["updated_media"].append(media.id)
                        logger.info(f"Assigned media {media.id}: box {old_location_id} -> location_id {correct_location_id}")
                    else:
                        # Already pointing to correct location
                        stats["already_assigned"] += 1
                        logger.debug(f"Media {media.id} already correctly assigned to location_id {media.location_id}")
                else:
                    # No location found with this box number
                    stats["not_found"] += 1
                    logger.debug(f"Media {media.id} has location_id {media.location_id} but no location with that box number")
            
            logger.info(f"Location assignment complete: {stats['assigned']} assigned, {stats['not_found']} not found")
            return stats
            
        except Exception as e:
            logger.error(f"Error during location assignment: {e}")
            raise
