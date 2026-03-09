#!/usr/bin/env python3
"""Create initial database for portable distribution."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path('src')))

from data.database import Database

# Create database in dist folder
db_path = Path('dist/MediaArchiveManager/data/media_archive.db')
print(f"Creating database at: {db_path}")

db = Database(str(db_path))
db.init_schema()
db.close()

if db_path.exists():
    size = db_path.stat().st_size
    print(f"[OK] Database created successfully")
    print(f"[OK] Database size: {size} bytes")
else:
    print(f"[ERROR] Database file not found")
    sys.exit(1)
