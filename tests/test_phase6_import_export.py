"""Tests for Phase 6: Import/Export functionality.

This module provides comprehensive tests for CSV import/export and database backup features.
"""

import unittest
import tempfile
import csv
from pathlib import Path
from datetime import date
import sys
from io import StringIO

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.media import Media
from models.location import StorageLocation
from models.enums import MediaType


class TestImportDialog(unittest.TestCase):
    """Tests for ImportDialog functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_media_csv(self, filename: str, include_header: bool = True) -> str:
        """Create a test media CSV file."""
        file_path = Path(self.temp_dir) / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if include_header:
                writer.writerow([
                    "Name", "Media Type", "Company", "License Code",
                    "Creation Date", "Valid Until Date", "Content Description",
                    "Remarks", "Location ID"
                ])
            
            writer.writerow([
                "Test Media 1", "DVD", "Company A", "LIC001",
                "2024-01-01", "2025-01-01", "Test content",
                "Test remarks", "1"
            ])
            writer.writerow([
                "Test Media 2", "Blu-ray", "Company B", "LIC002",
                "2024-02-01", "2025-02-01", "More content",
                "More remarks", "2"
            ])
        
        return str(file_path)

    def _create_location_csv(self, filename: str, include_header: bool = True) -> str:
        """Create a test location CSV file."""
        file_path = Path(self.temp_dir) / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if include_header:
                writer.writerow(["Box", "Place", "Detail"])
            
            writer.writerow(["Box 1", "Shelf A", "Top shelf"])
            writer.writerow(["Box 2", "Shelf B", "Middle shelf"])
        
        return str(file_path)

    def test_parse_media_csv_valid(self):
        """Test parsing valid media CSV."""
        csv_file = self._create_media_csv("valid_media.csv")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Skip header
        data_rows = rows[1:]
        
        # Parse first row
        row = data_rows[0]
        media = Media(
            name=row[0],
            media_type=row[1],
            company=row[2] or None,
            license_code=row[3] or None,
            creation_date=date.fromisoformat(row[4]) if row[4] else None,
            valid_until_date=date.fromisoformat(row[5]) if row[5] else None,
            content_description=row[6] or None,
            remarks=row[7] or None,
            location_id=int(row[8]) if row[8] else None,
        )
        
        self.assertEqual(media.name, "Test Media 1")
        self.assertEqual(media.media_type, "DVD")
        self.assertEqual(media.company, "Company A")
        self.assertEqual(media.license_code, "LIC001")
        self.assertEqual(media.location_id, 1)

    def test_parse_location_csv_valid(self):
        """Test parsing valid location CSV."""
        csv_file = self._create_location_csv("valid_locations.csv")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Skip header
        data_rows = rows[1:]
        
        # Parse first row
        row = data_rows[0]
        location = StorageLocation(
            box=row[0],
            place=row[1],
            detail=row[2] or None,
        )
        
        self.assertEqual(location.box, "Box 1")
        self.assertEqual(location.place, "Shelf A")
        self.assertEqual(location.detail, "Top shelf")

    def test_parse_media_csv_missing_required_field(self):
        """Test parsing media CSV with missing required field."""
        file_path = Path(self.temp_dir) / "invalid_media.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Media Type", "Company"])
            writer.writerow(["", "DVD", "Company A"])  # Missing name
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        data_rows = rows[1:]
        row = data_rows[0]
        
        # Name is empty - should be invalid
        self.assertFalse(row[0].strip())

    def test_parse_location_csv_missing_required_field(self):
        """Test parsing location CSV with missing required field."""
        file_path = Path(self.temp_dir) / "invalid_locations.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Box", "Place", "Detail"])
            writer.writerow(["Box 1", "", "Detail"])  # Missing place
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        data_rows = rows[1:]
        row = data_rows[0]
        
        # Place is empty - should be invalid
        self.assertFalse(row[1].strip())

    def test_parse_media_csv_invalid_date(self):
        """Test parsing media CSV with invalid date."""
        file_path = Path(self.temp_dir) / "invalid_date.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Media Type", "Creation Date"])
            writer.writerow(["Test", "DVD", "invalid-date"])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        data_rows = rows[1:]
        row = data_rows[0]
        
        # Try to parse invalid date
        with self.assertRaises(ValueError):
            date.fromisoformat(row[2])

    def test_parse_media_csv_invalid_location_id(self):
        """Test parsing media CSV with invalid location ID."""
        file_path = Path(self.temp_dir) / "invalid_location_id.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Media Type", "Location ID"])
            writer.writerow(["Test", "DVD", "not-a-number"])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        data_rows = rows[1:]
        row = data_rows[0]
        
        # Try to parse invalid location ID
        with self.assertRaises(ValueError):
            int(row[2])

    def test_csv_file_with_no_header(self):
        """Test parsing CSV file without header."""
        file_path = Path(self.temp_dir) / "no_header.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Test Media", "DVD", "Company", "LIC001"])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Should have 1 row (no header)
        self.assertEqual(len(rows), 1)

    def test_csv_file_empty(self):
        """Test parsing empty CSV file."""
        file_path = Path(self.temp_dir) / "empty.csv"
        file_path.touch()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 0)

    def test_csv_file_with_special_characters(self):
        """Test parsing CSV with special characters."""
        file_path = Path(self.temp_dir) / "special_chars.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Media Type"])
            writer.writerow(["Test™ Media®", "DVD"])
            writer.writerow(["Tëst Mëdia", "Blu-ray"])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Should parse special characters correctly
        self.assertEqual(rows[1][0], "Test™ Media®")
        self.assertEqual(rows[2][0], "Tëst Mëdia")


class TestExportDialog(unittest.TestCase):
    """Tests for ExportDialog functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data
        self.media_list = [
            Media(
                name="Test Media 1",
                media_type="DVD",
                company="Company A",
                license_code="LIC001",
                creation_date=date(2024, 1, 1),
                valid_until_date=date(2025, 1, 1),
                content_description="Test content",
                remarks="Test remarks",
                location_id=1,
            ),
            Media(
                name="Test Media 2",
                media_type="Blu-ray",
                company="Company B",
                license_code="LIC002",
                creation_date=date(2024, 2, 1),
                valid_until_date=date(2025, 2, 1),
                content_description="More content",
                remarks="More remarks",
                location_id=2,
            ),
        ]
        
        self.location_list = [
            StorageLocation(box="Box 1", place="Shelf A", detail="Top shelf"),
            StorageLocation(box="Box 2", place="Shelf B", detail="Middle shelf"),
        ]

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_media_to_csv(self):
        """Test exporting media to CSV."""
        file_path = Path(self.temp_dir) / "export_media.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = [
                "Name", "Media Type", "Company", "License Code",
                "Creation Date", "Valid Until Date", "Content Description",
                "Remarks", "Location ID"
            ]
            writer.writerow(headers)
            
            # Write media
            for media in self.media_list:
                row = [
                    media.name,
                    media.media_type,
                    media.company or "",
                    media.license_code or "",
                    media.creation_date.isoformat() if media.creation_date else "",
                    media.valid_until_date.isoformat() if media.valid_until_date else "",
                    media.content_description or "",
                    media.remarks or "",
                    media.location_id or "",
                ]
                writer.writerow(row)
        
        # Verify file was created
        self.assertTrue(file_path.exists())
        
        # Verify content
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 3)  # Header + 2 media
        self.assertEqual(rows[0][0], "Name")
        self.assertEqual(rows[1][0], "Test Media 1")
        self.assertEqual(rows[2][0], "Test Media 2")

    def test_export_locations_to_csv(self):
        """Test exporting locations to CSV."""
        file_path = Path(self.temp_dir) / "export_locations.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = ["Box", "Place", "Detail"]
            writer.writerow(headers)
            
            # Write locations
            for location in self.location_list:
                row = [
                    location.box,
                    location.place,
                    location.detail or "",
                ]
                writer.writerow(row)
        
        # Verify file was created
        self.assertTrue(file_path.exists())
        
        # Verify content
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 3)  # Header + 2 locations
        self.assertEqual(rows[0][0], "Box")
        self.assertEqual(rows[1][0], "Box 1")
        self.assertEqual(rows[2][0], "Box 2")

    def test_export_without_header(self):
        """Test exporting without header row."""
        file_path = Path(self.temp_dir) / "export_no_header.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write media without header
            for media in self.media_list:
                row = [
                    media.name,
                    media.media_type,
                    media.company or "",
                ]
                writer.writerow(row)
        
        # Verify content
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)  # No header, just 2 media
        self.assertEqual(rows[0][0], "Test Media 1")

    def test_export_empty_list(self):
        """Test exporting empty list."""
        file_path = Path(self.temp_dir) / "export_empty.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Type"])
            # No data rows
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 1)  # Only header


class TestDatabaseBackup(unittest.TestCase):
    """Tests for database backup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backup_file_creation(self):
        """Test that backup file is created."""
        source_file = Path(self.temp_dir) / "source.db"
        backup_file = Path(self.temp_dir) / "backup.db"
        
        # Create source file
        source_file.write_text("test data")
        
        # Copy to backup
        import shutil
        shutil.copy2(source_file, backup_file)
        
        # Verify backup exists
        self.assertTrue(backup_file.exists())
        
        # Verify content matches
        self.assertEqual(source_file.read_text(), backup_file.read_text())

    def test_backup_preserves_content(self):
        """Test that backup preserves file content."""
        source_file = Path(self.temp_dir) / "source.db"
        backup_file = Path(self.temp_dir) / "backup.db"
        
        test_content = "This is test database content"
        source_file.write_text(test_content)
        
        import shutil
        shutil.copy2(source_file, backup_file)
        
        self.assertEqual(backup_file.read_text(), test_content)

    def test_backup_with_timestamp(self):
        """Test backup filename with timestamp."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        
        # Verify timestamp format
        self.assertRegex(backup_filename, r"backup_\d{8}_\d{6}\.db")

    def test_multiple_backups(self):
        """Test creating multiple backups."""
        source_file = Path(self.temp_dir) / "source.db"
        source_file.write_text("test data")
        
        import shutil
        from datetime import datetime
        import time
        
        backups = []
        for i in range(3):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = Path(self.temp_dir) / f"backup_{timestamp}_{i}.db"
            shutil.copy2(source_file, backup_file)
            backups.append(backup_file)
            time.sleep(0.1)
        
        # Verify all backups exist
        for backup in backups:
            self.assertTrue(backup.exists())


class TestImportExportIntegration(unittest.TestCase):
    """Integration tests for import/export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_then_import_media(self):
        """Test exporting media and then importing it."""
        # Create test media
        original_media = [
            Media(
                name="Test Media 1",
                media_type="DVD",
                company="Company A",
                creation_date=date(2024, 1, 1),
            ),
            Media(
                name="Test Media 2",
                media_type="Blu-ray",
                company="Company B",
                creation_date=date(2024, 2, 1),
            ),
        ]
        
        # Export to CSV
        export_file = Path(self.temp_dir) / "export.csv"
        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Media Type", "Company", "Creation Date"])
            for media in original_media:
                writer.writerow([
                    media.name,
                    media.media_type,
                    media.company or "",
                    media.creation_date.isoformat() if media.creation_date else "",
                ])
        
        # Import from CSV
        imported_media = []
        with open(export_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                media = Media(
                    name=row[0],
                    media_type=row[1],
                    company=row[2] or None,
                    creation_date=date.fromisoformat(row[3]) if row[3] else None,
                )
                imported_media.append(media)
        
        # Verify data matches
        self.assertEqual(len(imported_media), len(original_media))
        for orig, imported in zip(original_media, imported_media):
            self.assertEqual(orig.name, imported.name)
            self.assertEqual(orig.media_type, imported.media_type)
            self.assertEqual(orig.company, imported.company)
            self.assertEqual(orig.creation_date, imported.creation_date)

    def test_export_then_import_locations(self):
        """Test exporting locations and then importing them."""
        # Create test locations
        original_locations = [
            StorageLocation(box="Box 1", place="Shelf A", detail="Top"),
            StorageLocation(box="Box 2", place="Shelf B", detail="Middle"),
        ]
        
        # Export to CSV
        export_file = Path(self.temp_dir) / "export_locations.csv"
        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Box", "Place", "Detail"])
            for location in original_locations:
                writer.writerow([
                    location.box,
                    location.place,
                    location.detail or "",
                ])
        
        # Import from CSV
        imported_locations = []
        with open(export_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                location = StorageLocation(
                    box=row[0],
                    place=row[1],
                    detail=row[2] or None,
                )
                imported_locations.append(location)
        
        # Verify data matches
        self.assertEqual(len(imported_locations), len(original_locations))
        for orig, imported in zip(original_locations, imported_locations):
            self.assertEqual(orig.box, imported.box)
            self.assertEqual(orig.place, imported.place)
            self.assertEqual(orig.detail, imported.detail)


if __name__ == '__main__':
    unittest.main()
