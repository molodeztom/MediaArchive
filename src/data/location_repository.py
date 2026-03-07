"""Repository for StorageLocation data access.

This module provides CRUD operations for storage locations.
"""

import logging
from datetime import datetime
from typing import Optional

from data.database import Database
from models.location import StorageLocation
from utils.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class LocationRepository:
    """Repository for StorageLocation data access.
    
    Provides CRUD operations for storage locations.
    """

    def __init__(self, database: Database) -> None:
        """Initialize repository.
        
        Args:
            database: Database connection manager.
        """
        self._db = database
        logger.debug("LocationRepository initialized")

    def create(self, location: StorageLocation) -> StorageLocation:
        """Create a new storage location.
        
        Args:
            location: StorageLocation object to create.
        
        Returns:
            StorageLocation with id set.
        
        Raises:
            DatabaseError: If creation fails.
        """
        try:
            cursor = self._db.execute(
                """
                INSERT INTO storage_location (box, place, detail)
                VALUES (?, ?, ?)
                """,
                (location.box, location.place, location.detail),
            )
            self._db.commit()
            
            location.id = cursor.lastrowid
            location.created_at = datetime.now()
            location.updated_at = datetime.now()
            
            logger.info(f"Created storage location: {location.id}")
            return location
        except DatabaseError as e:
            logger.error(f"Failed to create storage location: {e}")
            raise

    def get_by_id(self, location_id: int) -> StorageLocation:
        """Get storage location by ID.
        
        Args:
            location_id: Location ID.
        
        Returns:
            StorageLocation object.
        
        Raises:
            NotFoundError: If location not found.
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM storage_location WHERE id = ?",
                (location_id,),
            )
            row = cursor.fetchone()
            
            if not row:
                raise NotFoundError(f"Storage location {location_id} not found")
            
            return self._row_to_location(row)
        except DatabaseError as e:
            logger.error(f"Failed to get storage location: {e}")
            raise

    def get_all(self) -> list[StorageLocation]:
        """Get all storage locations.
        
        Returns:
            List of StorageLocation objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM storage_location ORDER BY box, place"
            )
            rows = cursor.fetchall()
            return [self._row_to_location(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to get all storage locations: {e}")
            raise

    def update(self, location: StorageLocation) -> StorageLocation:
        """Update an existing storage location.
        
        Args:
            location: StorageLocation object with id set.
        
        Returns:
            Updated StorageLocation.
        
        Raises:
            NotFoundError: If location not found.
            DatabaseError: If update fails.
        """
        if location.id is None:
            raise ValueError("Cannot update location without id")
        
        try:
            cursor = self._db.execute(
                """
                UPDATE storage_location
                SET box = ?, place = ?, detail = ?
                WHERE id = ?
                """,
                (location.box, location.place, location.detail, location.id),
            )
            self._db.commit()
            
            if cursor.rowcount == 0:
                raise NotFoundError(f"Storage location {location.id} not found")
            
            location.updated_at = datetime.now()
            logger.info(f"Updated storage location: {location.id}")
            return location
        except DatabaseError as e:
            logger.error(f"Failed to update storage location: {e}")
            raise

    def delete(self, location_id: int) -> None:
        """Delete a storage location.
        
        Args:
            location_id: Location ID.
        
        Raises:
            NotFoundError: If location not found.
            DatabaseError: If delete fails.
        """
        try:
            cursor = self._db.execute(
                "DELETE FROM storage_location WHERE id = ?",
                (location_id,),
            )
            self._db.commit()
            
            if cursor.rowcount == 0:
                raise NotFoundError(f"Storage location {location_id} not found")
            
            logger.info(f"Deleted storage location: {location_id}")
        except DatabaseError as e:
            logger.error(f"Failed to delete storage location: {e}")
            raise

    def search_by_box(self, box: str) -> list[StorageLocation]:
        """Search storage locations by box name.
        
        Args:
            box: Box name to search for (case-insensitive).
        
        Returns:
            List of matching StorageLocation objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM storage_location WHERE box LIKE ? ORDER BY place",
                (f"%{box}%",),
            )
            rows = cursor.fetchall()
            return [self._row_to_location(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search storage locations: {e}")
            raise

    def search_by_place(self, place: str) -> list[StorageLocation]:
        """Search storage locations by place.
        
        Args:
            place: Place to search for (case-insensitive).
        
        Returns:
            List of matching StorageLocation objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM storage_location WHERE place LIKE ? ORDER BY box",
                (f"%{place}%",),
            )
            rows = cursor.fetchall()
            return [self._row_to_location(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search storage locations: {e}")
            raise

    @staticmethod
    def _row_to_location(row: dict) -> StorageLocation:
        """Convert database row to StorageLocation object.
        
        Args:
            row: Database row as dict.
        
        Returns:
            StorageLocation object.
        """
        return StorageLocation(
            id=row["id"],
            box=row["box"],
            place=row["place"],
            detail=row["detail"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
