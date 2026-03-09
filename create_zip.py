#!/usr/bin/env python3
"""Create ZIP archive for portable distribution."""

import shutil
from pathlib import Path

source_dir = Path('dist/MediaArchiveManager')
zip_file = Path('dist/MediaArchiveManager_v2.1.0_Portable')

print(f"Creating ZIP archive...")
print(f"Source: {source_dir}")
print(f"Output: {zip_file}.zip")

# Create ZIP archive
shutil.make_archive(str(zip_file), 'zip', str(source_dir.parent), source_dir.name)

# Verify
zip_path = Path(f"{zip_file}.zip")
if zip_path.exists():
    size = zip_path.stat().st_size
    size_mb = size / (1024 * 1024)
    print(f"[OK] ZIP archive created successfully")
    print(f"[OK] ZIP file size: {size_mb:.2f} MB")
    print(f"[OK] ZIP file location: {zip_path}")
else:
    print(f"[ERROR] ZIP file not found")
    exit(1)
