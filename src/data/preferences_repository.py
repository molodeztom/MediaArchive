"""Repository for user preferences data access.

This module provides data access operations for user preferences stored in the database.

History:
20260309  V1.0: Initial preferences repository implementation
"""

import logging
from typing import Optional

from data.database import Database
from utils.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class PreferencesRepository:
    """Repository for user preferences data access."""

    def __init__(self, database: Database) -> None:
        """Initialize preferences repository.
        
        Args:
            database: Database connection manager.
        """
        self._db = database
        logger.debug("PreferencesRepository initialized")

    def set_preference(self, key: str, value: str) -> None:
        """Set a user preference value.
        
        Args:
            key: Preference key.
            value: Preference value.
        """
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            
            # Try to update first
            cursor.execute(
                "UPDATE user_preferences SET value = ? WHERE key = ?",
                (value, key)
            )
            
            # If no rows updated, insert new
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO user_preferences (key, value) VALUES (?, ?)",
                    (key, value)
                )
            
            conn.commit()
            logger.debug(f"Set preference: {key} = {value}")
        except Exception as e:
            logger.error(f"Error setting preference {key}: {e}")
            raise

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a user preference value.
        
        Args:
            key: Preference key.
            default: Default value if preference not found.
        
        Returns:
            Preference value or default.
        """
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM user_preferences WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if row:
                logger.debug(f"Retrieved preference: {key} = {row[0]}")
                return row[0]
            else:
                logger.debug(f"Preference not found: {key}, using default: {default}")
                return default
        except Exception as e:
            logger.error(f"Error getting preference {key}: {e}")
            return default

    def delete_preference(self, key: str) -> None:
        """Delete a user preference.
        
        Args:
            key: Preference key.
        """
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_preferences WHERE key = ?",
                (key,)
            )
            conn.commit()
            logger.debug(f"Deleted preference: {key}")
        except Exception as e:
            logger.error(f"Error deleting preference {key}: {e}")
            raise

    def get_all_preferences(self) -> dict:
        """Get all user preferences.
        
        Returns:
            Dictionary of all preferences.
        """
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_preferences")
            rows = cursor.fetchall()
            
            preferences = {row[0]: row[1] for row in rows}
            logger.debug(f"Retrieved {len(preferences)} preferences")
            return preferences
        except Exception as e:
            logger.error(f"Error getting all preferences: {e}")
            return {}
