"""Database schema definitions for Media Archive Manager.

This module contains SQL schema definitions for creating the database tables,
indexes, and triggers. The schema is designed for simplicity and efficiency.
"""

# SQL schema for storage_location table
STORAGE_LOCATION_TABLE = """
CREATE TABLE IF NOT EXISTS storage_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    box TEXT NOT NULL,
    place TEXT NOT NULL,
    detail TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL schema for media table
MEDIA_TABLE = """
CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content_description TEXT,
    remarks TEXT,
    creation_date DATE,
    valid_until_date DATE,
    media_type TEXT,
    type TEXT,
    company TEXT,
    license_code TEXT,
    location_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL
);
"""

# Indexes for storage_location table
STORAGE_LOCATION_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_storage_location_box ON storage_location(box);",
    "CREATE INDEX IF NOT EXISTS idx_storage_location_place ON storage_location(place);",
]

# Indexes for media table
MEDIA_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_media_name ON media(name);",
    "CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type);",
    "CREATE INDEX IF NOT EXISTS idx_media_content_type ON media(type);",
    "CREATE INDEX IF NOT EXISTS idx_media_location ON media(location_id);",
    "CREATE INDEX IF NOT EXISTS idx_media_valid_until ON media(valid_until_date);",
    "CREATE INDEX IF NOT EXISTS idx_media_creation_date ON media(creation_date);",
]

# Trigger to update updated_at timestamp for storage_location
STORAGE_LOCATION_TIMESTAMP_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS update_storage_location_timestamp
AFTER UPDATE ON storage_location
FOR EACH ROW
BEGIN
    UPDATE storage_location SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
"""

# Trigger to update updated_at timestamp for media
MEDIA_TIMESTAMP_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS update_media_timestamp
AFTER UPDATE ON media
FOR EACH ROW
BEGIN
    UPDATE media SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
"""


def get_schema_sql() -> list[str]:
    """Get all SQL statements needed to initialize the database.
    
    Returns:
        List of SQL statements in correct order.
    """
    return [
        STORAGE_LOCATION_TABLE,
        MEDIA_TABLE,
        *STORAGE_LOCATION_INDEXES,
        *MEDIA_INDEXES,
        STORAGE_LOCATION_TIMESTAMP_TRIGGER,
        MEDIA_TIMESTAMP_TRIGGER,
    ]
