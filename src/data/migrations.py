"""Database migration utilities for Media Archive Manager.

This module provides utilities for applying schema migrations to the database.
Migrations are applied automatically on application startup.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Handles database schema migrations."""
    
    @staticmethod
    def migrate_schema(conn) -> None:
        """Apply all pending schema migrations.
        
        Args:
            conn: SQLite database connection.
        """
        cursor = conn.cursor()
        
        # Migration 1: Add number column to media table
        DatabaseMigration._add_number_column(cursor, conn)
        
        # Migration 2: Rename type column to category
        DatabaseMigration._rename_type_to_category(cursor, conn)
    
    @staticmethod
    def _add_number_column(cursor, conn) -> None:
        """Add number column to media table if it doesn't exist.
        
        Args:
            cursor: Database cursor.
            conn: Database connection.
        """
        try:
            # Check if media table exists first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media'")
            if not cursor.fetchone():
                # Table doesn't exist yet, skip migration
                logger.debug("Media table doesn't exist yet, skipping number column migration")
                return
            
            # Check if number column exists
            cursor.execute("PRAGMA table_info(media)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "number" not in columns:
                logger.info("Migrating schema: Adding number column to media table")
                cursor.execute("ALTER TABLE media ADD COLUMN number TEXT")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_number ON media(number)")
                conn.commit()
                logger.info("Successfully added number column to media table")
        except Exception as e:
            logger.error(f"Error adding number column: {e}")
            raise
    
    @staticmethod
    def _rename_type_to_category(cursor, conn) -> None:
        """Rename type column to category if needed.
        
        Args:
            cursor: Database cursor.
            conn: Database connection.
        """
        try:
            # Check if media table exists first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media'")
            if not cursor.fetchone():
                # Table doesn't exist yet, skip migration
                logger.debug("Media table doesn't exist yet, skipping type to category migration")
                return
            
            # Check if type column exists and category doesn't
            cursor.execute("PRAGMA table_info(media)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "type" in columns and "category" not in columns:
                logger.info("Migrating schema: Renaming type column to category")
                
                # SQLite doesn't support RENAME COLUMN directly in older versions
                # We need to create a new table and copy data
                cursor.execute("""
                    CREATE TABLE media_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        number TEXT,
                        content_description TEXT,
                        remarks TEXT,
                        creation_date DATE,
                        valid_until_date DATE,
                        media_type TEXT,
                        category TEXT,
                        company TEXT,
                        license_code TEXT,
                        location_id INTEGER,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL
                    )
                """)
                
                # Copy data from old table to new table
                cursor.execute("""
                    INSERT INTO media_new (
                        id, name, number, content_description, remarks,
                        creation_date, valid_until_date, media_type, category,
                        company, license_code, location_id, created_at, updated_at
                    )
                    SELECT
                        id, name, NULL, content_description, remarks,
                        creation_date, valid_until_date, media_type, type,
                        company, license_code, location_id, created_at, updated_at
                    FROM media
                """)
                
                # Drop old table and rename new table
                cursor.execute("DROP TABLE media")
                cursor.execute("ALTER TABLE media_new RENAME TO media")
                
                # Recreate indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_name ON media(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_number ON media(number)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_category ON media(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_location ON media(location_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_valid_until ON media(valid_until_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_creation_date ON media(creation_date)")
                
                # Recreate triggers
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_media_timestamp
                    AFTER UPDATE ON media
                    FOR EACH ROW
                    BEGIN
                        UPDATE media SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                    END
                """)
                
                conn.commit()
                logger.info("Successfully renamed type column to category")
            elif "category" in columns and "type" in columns:
                # Both columns exist, drop the old type column
                logger.info("Migrating schema: Dropping old type column")
                cursor.execute("""
                    CREATE TABLE media_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        number TEXT,
                        content_description TEXT,
                        remarks TEXT,
                        creation_date DATE,
                        valid_until_date DATE,
                        media_type TEXT,
                        category TEXT,
                        company TEXT,
                        license_code TEXT,
                        location_id INTEGER,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO media_new (
                        id, name, number, content_description, remarks,
                        creation_date, valid_until_date, media_type, category,
                        company, license_code, location_id, created_at, updated_at
                    )
                    SELECT
                        id, name, number, content_description, remarks,
                        creation_date, valid_until_date, media_type, category,
                        company, license_code, location_id, created_at, updated_at
                    FROM media
                """)
                
                cursor.execute("DROP TABLE media")
                cursor.execute("ALTER TABLE media_new RENAME TO media")
                
                # Recreate indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_name ON media(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_number ON media(number)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_category ON media(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_location ON media(location_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_valid_until ON media(valid_until_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_creation_date ON media(creation_date)")
                
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_media_timestamp
                    AFTER UPDATE ON media
                    FOR EACH ROW
                    BEGIN
                        UPDATE media SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                    END
                """)
                
                conn.commit()
                logger.info("Successfully dropped old type column")
        except Exception as e:
            logger.error(f"Error renaming type column to category: {e}")
            raise
