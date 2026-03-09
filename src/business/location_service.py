"""Business logic service for StorageLocation operations.

This module provides high-level operations for managing storage locations
with validation and business rule enforcement.
"""

import logging
from typing import Optional

from data.database import Database
from data.location_repository import LocationRepository
from models.location import StorageLocation
from utils.config import MAX_BOX_LENGTH, MAX_PLACE_LENGTH, MAX_DETAIL_LENGTH
from utils.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class LocationService:
    """Service for StorageLocation business operations.
    
    Provides CRUD operations with validation and business rule enforcement.
    """

    def __init__(self, database: Database) -> None:
        """Initialize service.
        
        Args:
            database: Database connection manager.
        """
        self._db = database
        self._repo = LocationRepository(database)
        logger.debug("LocationService initialized")

    def create_location(
        self,
        box: str,
        place: str,
        detail: Optional[str] = None,
    ) -> StorageLocation:
        """Create a new storage location with validation.
        
        Args:
            box: Container name (required).
            place: Physical location (optional).
            detail: Additional detail (optional).
        
        Returns:
            Created StorageLocation with id set.
        
        Raises:
            ValidationError: If validation fails.
        """
        # Validate inputs
        self._validate_location_input(box, place, detail)
        
        # Create location object
        location = StorageLocation(
            box=box,
            place=place,
            detail=detail,
        )
        
        # Save to database
        created = self._repo.create(location)
        logger.info(f"Created location: {created.id} - {created}")
        return created

    def get_location(self, location_id: int) -> StorageLocation:
        """Get storage location by ID.
        
        Args:
            location_id: Location ID.
        
        Returns:
            StorageLocation object.
        
        Raises:
            NotFoundError: If location not found.
        """
        try:
            location = self._repo.get_by_id(location_id)
            logger.debug(f"Retrieved location: {location_id}")
            return location
        except NotFoundError:
            logger.warning(f"Location not found: {location_id}")
            raise

    def get_all_locations(self) -> list[StorageLocation]:
        """Get all storage locations.
        
        Returns:
            List of StorageLocation objects.
        """
        locations = self._repo.get_all()
        logger.debug(f"Retrieved {len(locations)} locations")
        return locations

    def update_location(
        self,
        location_id: int,
        box: Optional[str] = None,
        place: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> StorageLocation:
        """Update an existing storage location.
        
        Args:
            location_id: Location ID.
            box: New box name (optional).
            place: New place (optional).
            detail: New detail (optional).
        
        Returns:
            Updated StorageLocation.
        
        Raises:
            NotFoundError: If location not found.
            ValidationError: If validation fails.
        """
        # Get existing location
        location = self._repo.get_by_id(location_id)
        
        # Update fields if provided
        if box is not None:
            location.box = box
        if place is not None:
            location.place = place
        if detail is not None:
            location.detail = detail
        
        # Validate updated location
        self._validate_location_input(location.box, location.place, location.detail)
        
        # Save changes
        updated = self._repo.update(location)
        logger.info(f"Updated location: {location_id}")
        return updated

    def delete_location(self, location_id: int) -> None:
        """Delete a storage location.
        
        Args:
            location_id: Location ID.
        
        Raises:
            NotFoundError: If location not found.
        """
        # Check if location exists
        self._repo.get_by_id(location_id)
        
        # Delete location
        self._repo.delete(location_id)
        logger.info(f"Deleted location: {location_id}")

    def search_locations(self, query: str) -> list[StorageLocation]:
        """Search locations by box or place.
        
        Args:
            query: Search query (searches both box and place).
        
        Returns:
            List of matching StorageLocation objects.
        
        Raises:
            ValidationError: If query is empty.
        """
        if not query or not query.strip():
            raise ValidationError("Search query cannot be empty")
        
        query = query.strip()
        
        # Search in both box and place
        results_box = self._repo.search_by_box(query)
        results_place = self._repo.search_by_place(query)
        
        # Combine and deduplicate results
        seen_ids = set()
        combined = []
        for loc in results_box + results_place:
            if loc.id not in seen_ids:
                combined.append(loc)
                seen_ids.add(loc.id)
        
        logger.debug(f"Search found {len(combined)} locations for: {query}")
        return combined

    def get_locations_by_box(self, box: str) -> list[StorageLocation]:
        """Get all locations in a specific box.
        
        Args:
            box: Box name.
        
        Returns:
            List of StorageLocation objects.
        
        Raises:
            ValidationError: If box name is empty.
        """
        if not box or not box.strip():
            raise ValidationError("Box name cannot be empty")
        
        results = self._repo.search_by_box(box.strip())
        logger.debug(f"Found {len(results)} locations in box: {box}")
        return results

    def get_locations_by_place(self, place: str) -> list[StorageLocation]:
        """Get all locations in a specific place.
        
        Args:
            place: Place name.
        
        Returns:
            List of StorageLocation objects.
        
        Raises:
            ValidationError: If place name is empty.
        """
        if not place or not place.strip():
            raise ValidationError("Place name cannot be empty")
        
        results = self._repo.search_by_place(place.strip())
        logger.debug(f"Found {len(results)} locations in place: {place}")
        return results

    @staticmethod
    def _validate_location_input(
        box: str,
        place: str,
        detail: Optional[str] = None,
    ) -> None:
        """Validate location input fields.
        
        Args:
            box: Box name.
            place: Place name.
            detail: Detail (optional).
        
        Raises:
            ValidationError: If validation fails.
        """
        # Validate box
        if not box or not box.strip():
            raise ValidationError("Box name is required")
        if len(box) > MAX_BOX_LENGTH:
            raise ValidationError(f"Box name exceeds {MAX_BOX_LENGTH} characters")
        
        # Validate place (optional)
        if place and len(place) > MAX_PLACE_LENGTH:
            raise ValidationError(f"Place exceeds {MAX_PLACE_LENGTH} characters")
        
        # Validate detail
        if detail and len(detail) > MAX_DETAIL_LENGTH:
            raise ValidationError(f"Detail exceeds {MAX_DETAIL_LENGTH} characters")
