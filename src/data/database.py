"""Database connection manager for Media Archive Manager.

This module provides a simple database connection manager that handles
SQLite connection lifecycle and schema initialization.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

from data.schema import get_schema_sql
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class Database:
    """Manages SQLite database connection and initialization.
    
    Provides context manager support for safe connection handling.
    """

    def __init__(self, db_path: str | Path) -> None:
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        logger.debug(f"Database manager initialized for {self._db_path}")

    def connect(self) -> sqlite3.Connection:
        """Get or create database connection.
        
        Returns:
            SQLite connection object.
        
        Raises:
            DatabaseError: If connection fails.
        """
        try:
            if self._connection is None:
                # Ensure parent directory exists
                self._db_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create connection
                self._connection = sqlite3.connect(
                    str(self._db_path),
                    timeout=5.0,
                    check_same_thread=False,
                )
                
                # Enable foreign keys
                self._connection.execute("PRAGMA foreign_keys = ON")
                
                # Use Row factory for dict-like access
                self._connection.row_factory = sqlite3.Row
                
                logger.info(f"Connected to database: {self._db_path}")
            
            return self._connection
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Database connection failed: {e}") from e

    def close(self) -> None:
        """Close database connection.
        
        Safely closes the connection if it exists.
        """
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
                logger.debug("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")

    def init_schema(self) -> None:
        """Initialize database schema.
        
        Creates all tables, indexes, and triggers if they don't exist.
        
        Raises:
            DatabaseError: If schema initialization fails.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Execute all schema SQL statements
            for sql in get_schema_sql():
                cursor.execute(sql)
            
            conn.commit()
            logger.info("Database schema initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise DatabaseError(f"Schema initialization failed: {e}") from e

    def execute(
        self,
        sql: str,
        params: tuple = (),
    ) -> sqlite3.Cursor:
        """Execute SQL query.
        
        Args:
            sql: SQL query string.
            params: Query parameters (for parameterized queries).
        
        Returns:
            Cursor object with query results.
        
        Raises:
            DatabaseError: If query execution fails.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query failed: {e}") from e

    def commit(self) -> None:
        """Commit current transaction.
        
        Raises:
            DatabaseError: If commit fails.
        """
        try:
            if self._connection:
                self._connection.commit()
                logger.debug("Transaction committed")
        except sqlite3.Error as e:
            logger.error(f"Commit failed: {e}")
            raise DatabaseError(f"Commit failed: {e}") from e

    def rollback(self) -> None:
        """Rollback current transaction.
        
        Raises:
            DatabaseError: If rollback fails.
        """
        try:
            if self._connection:
                self._connection.rollback()
                logger.debug("Transaction rolled back")
        except sqlite3.Error as e:
            logger.error(f"Rollback failed: {e}")
            raise DatabaseError(f"Rollback failed: {e}") from e

    def __enter__(self) -> "Database":
        """Context manager entry.
        
        Returns:
            Self for use in with statement.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit.
        
        Commits on success, rolls back on exception, then closes connection.
        
        Args:
            exc_type: Exception type if exception occurred.
            exc_val: Exception value if exception occurred.
            exc_tb: Exception traceback if exception occurred.
        """
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()
