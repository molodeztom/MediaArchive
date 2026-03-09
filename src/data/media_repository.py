"""Repository for Media data access.

This module provides CRUD operations for media items.
"""

import logging
from datetime import date, datetime
from typing import Optional

from data.database import Database
from models.media import Media
from utils.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class MediaRepository:
    """Repository for Media data access.
    
    Provides CRUD operations for media items.
    """

    def __init__(self, database: Database) -> None:
        """Initialize repository.
        
        Args:
            database: Database connection manager.
        """
        self._db = database
        logger.debug("MediaRepository initialized")

    def create(self, media: Media) -> Media:
        """Create a new media item.
        
        Args:
            media: Media object to create.
        
        Returns:
            Media with id set.
        
        Raises:
            DatabaseError: If creation fails.
        """
        try:
            cursor = self._db.execute(
                """
                INSERT INTO media (
                    name, number, content_description, remarks, creation_date,
                    valid_until_date, media_type, category, company, license_code,
                    location_id, box, position
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media.name,
                    media.number,
                    media.content_description,
                    media.remarks,
                    media.creation_date,
                    media.valid_until_date,
                    media.media_type,
                    media.category,
                    media.company,
                    media.license_code,
                    media.location_id,
                    media.box,
                    media.position,
                ),
            )
            self._db.commit()
            
            media.id = cursor.lastrowid
            media.created_at = datetime.now().isoformat()
            media.updated_at = datetime.now().isoformat()
            
            logger.info(f"Created media: {media.id}")
            return media
        except DatabaseError as e:
            logger.error(f"Failed to create media: {e}")
            raise

    def get_by_id(self, media_id: int) -> Media:
        """Get media by ID.
        
        Args:
            media_id: Media ID.
        
        Returns:
            Media object.
        
        Raises:
            NotFoundError: If media not found.
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM media WHERE id = ?",
                (media_id,),
            )
            row = cursor.fetchone()
            
            if not row:
                raise NotFoundError(f"Media {media_id} not found")
            
            return self._row_to_media(row)
        except DatabaseError as e:
            logger.error(f"Failed to get media: {e}")
            raise

    def get_all(self) -> list[Media]:
        """Get all media items.
        
        Returns:
            List of Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM media ORDER BY name"
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to get all media: {e}")
            raise

    def update(self, media: Media) -> Media:
        """Update an existing media item.
        
        Args:
            media: Media object with id set.
        
        Returns:
            Updated Media.
        
        Raises:
            NotFoundError: If media not found.
            DatabaseError: If update fails.
        """
        if media.id is None:
            raise ValueError("Cannot update media without id")
        
        try:
            cursor = self._db.execute(
                """
                UPDATE media
                SET name = ?, number = ?, content_description = ?, remarks = ?,
                    creation_date = ?, valid_until_date = ?, media_type = ?,
                    category = ?, company = ?, license_code = ?, location_id = ?,
                    box = ?, position = ?
                WHERE id = ?
                """,
                (
                    media.name,
                    media.number,
                    media.content_description,
                    media.remarks,
                    media.creation_date,
                    media.valid_until_date,
                    media.media_type,
                    media.category,
                    media.company,
                    media.license_code,
                    media.location_id,
                    media.box,
                    media.position,
                    media.id,
                ),
            )
            self._db.commit()
            
            if cursor.rowcount == 0:
                raise NotFoundError(f"Media {media.id} not found")
            
            media.updated_at = datetime.now().isoformat()
            logger.info(f"Updated media: {media.id}")
            return media
        except DatabaseError as e:
            logger.error(f"Failed to update media: {e}")
            raise

    def delete(self, media_id: int) -> None:
        """Delete a media item.
        
        Args:
            media_id: Media ID.
        
        Raises:
            NotFoundError: If media not found.
            DatabaseError: If delete fails.
        """
        try:
            cursor = self._db.execute(
                "DELETE FROM media WHERE id = ?",
                (media_id,),
            )
            self._db.commit()
            
            if cursor.rowcount == 0:
                raise NotFoundError(f"Media {media_id} not found")
            
            logger.info(f"Deleted media: {media_id}")
        except DatabaseError as e:
            logger.error(f"Failed to delete media: {e}")
            raise

    def search_by_name(self, name: str) -> list[Media]:
        """Search media by name.
        
        Args:
            name: Name to search for (case-insensitive).
        
        Returns:
            List of matching Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM media WHERE name LIKE ? ORDER BY name",
                (f"%{name}%",),
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search media by name: {e}")
            raise

    def search_by_content(self, content: str) -> list[Media]:
        """Search media by content description.
        
        Args:
            content: Content to search for (case-insensitive).
        
        Returns:
            List of matching Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                """
                SELECT * FROM media
                WHERE content_description LIKE ? OR remarks LIKE ?
                ORDER BY name
                """,
                (f"%{content}%", f"%{content}%"),
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search media by content: {e}")
            raise

    def search_by_type(self, media_type: str) -> list[Media]:
        """Search media by type.
        
        Args:
            media_type: Media type to search for.
        
        Returns:
            List of matching Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM media WHERE media_type = ? ORDER BY name",
                (media_type,),
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search media by type: {e}")
            raise

    def search_by_location(self, location_id: int) -> list[Media]:
        """Search media by storage location.
        
        Args:
            location_id: Storage location ID.
        
        Returns:
            List of matching Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                "SELECT * FROM media WHERE location_id = ? ORDER BY name",
                (location_id,),
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search media by location: {e}")
            raise

    def search_by_creation_date(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Media]:
        """Search media by creation date range.
        
        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
        
        Returns:
            List of matching Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                """
                SELECT * FROM media
                WHERE creation_date BETWEEN ? AND ?
                ORDER BY creation_date DESC
                """,
                (start_date, end_date),
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to search media by creation date: {e}")
            raise

    def get_expired_media(self) -> list[Media]:
        """Get all expired media.
        
        Returns:
            List of expired Media objects.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                """
                SELECT * FROM media
                WHERE valid_until_date IS NOT NULL
                AND valid_until_date < DATE('now')
                ORDER BY valid_until_date DESC
                """
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to get expired media: {e}")
            raise

    def get_expiring_soon(self, days: int = 30) -> list[Media]:
        """Get media expiring within specified days.
        
        Args:
            days: Number of days to look ahead (default 30).
        
        Returns:
            List of Media objects expiring soon.
        
        Raises:
            DatabaseError: If query fails.
        """
        try:
            cursor = self._db.execute(
                f"""
                SELECT * FROM media
                WHERE valid_until_date IS NOT NULL
                AND valid_until_date BETWEEN DATE('now') AND DATE('now', '+{days} days')
                ORDER BY valid_until_date ASC
                """
            )
            rows = cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except DatabaseError as e:
            logger.error(f"Failed to get expiring media: {e}")
            raise

    @staticmethod
    def _row_to_media(row: dict) -> Media:
        """Convert database row to Media object.
        
        Args:
            row: Database row as dict.
        
        Returns:
            Media object.
        """
        # Handle both dict and sqlite3.Row objects
        # sqlite3.Row doesn't support .get(), so use try/except for optional fields
        try:
            box = row["box"]
        except (KeyError, IndexError):
            box = None
        try:
            position = row["position"]
        except (KeyError, IndexError):
            position = None
        
        return Media(
            id=row["id"],
            name=row["name"],
            number=row["number"],
            media_type=row["media_type"],
            category=row["category"],
            content_description=row["content_description"],
            remarks=row["remarks"],
            creation_date=date.fromisoformat(row["creation_date"]) if row["creation_date"] else None,
            valid_until_date=date.fromisoformat(row["valid_until_date"]) if row["valid_until_date"] else None,
            company=row["company"],
            license_code=row["license_code"],
            location_id=row["location_id"],
            box=box,
            position=position,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
