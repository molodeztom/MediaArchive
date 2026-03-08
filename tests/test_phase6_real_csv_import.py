"""Tests for Phase 6a and 6b: Real CSV import/export with Access format.

This module provides comprehensive integration tests for importing real CSV files
in Access database format and exporting them back to CSV.
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

from business.access_csv_mapper import (
    AccessMediaTypeMapper,
    AccessDateConverter,
    AccessCSVMapper,
    AccessLocationMapper,
)
from models.media import Media
from models.location import StorageLocation
from models.enums import MediaType
from data.database import Database
from data.media_repository import MediaRepository
from data.location_repository import LocationRepository


class TestRealCSVImport(unittest.TestCase):
    """Tests for importing real CSV files in Access format."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        
        # Initialize database
        self.db = Database(str(self.db_path))
        self.db.init_schema()
        
        self.media_repo = MediaRepository(self.db)
        self.location_repo = LocationRepository(self.db)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_access_locations_csv(self, filename: str) -> str:
        """Create a realistic Access locations CSV file."""
        file_path = Path(self.temp_dir) / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Header: Box;Ort;Typ
            writer.writerow(["Box", "Ort", "Typ"])
            
            # Real-world location data
            writer.writerow(["1", "Regal A", "Oben"])
            writer.writerow(["2", "Regal A", "Mitte"])
            writer.writerow(["3", "Regal A", "Unten"])
            writer.writerow(["4", "Regal B", "Oben"])
            writer.writerow(["5", "Regal B", "Mitte"])
            writer.writerow(["6", "Schrank 1", "Fach 1"])
            writer.writerow(["7", "Schrank 1", "Fach 2"])
            writer.writerow(["8", "Schrank 2", "Fach 1"])
        
        return str(file_path)

    def _create_access_media_csv(self, filename: str) -> str:
        """Create a realistic Access media CSV file."""
        file_path = Path(self.temp_dir) / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Header: ID;Name;Firma;Box;Position;Code;Art;Bemerkung;Datum;Verfällt am
            writer.writerow([
                "ID", "Name", "Firma", "Box", "Position", "Code", "Art", 
                "Bemerkung", "Datum", "Verfällt am"
            ])
            
            # Real-world media data
            writer.writerow([
                "1", "Windows 10 Pro", "Microsoft", "1", "Regal A", 
                "XXXXX-XXXXX-XXXXX", "Program", "Operating System", 
                "01.01.2020", "01.01.2025"
            ])
            writer.writerow([
                "2", "Office 365", "Microsoft", "2", "Regal A", 
                "YYYYY-YYYYY-YYYYY", "Program", "Productivity Suite", 
                "15.03.2021", "15.03.2026"
            ])
            writer.writerow([
                "3", "Backup Archive 2024", "Internal", "3", "Regal A", 
                "", "Backup", "Full system backup", 
                "31.12.2023", "31.12.2024"
            ])
            writer.writerow([
                "4", "Photo Collection 2023", "Personal", "4", "Regal B", 
                "", "Archive", "Family photos and videos", 
                "01.01.2023", ""
            ])
            writer.writerow([
                "5", "Linux Mint 21", "Linux Foundation", "5", "Regal B", 
                "", "Program", "Linux Distribution", 
                "10.08.2022", ""
            ])
            writer.writerow([
                "6", "Game Collection", "Various", "6", "Schrank 1", 
                "", "Game", "Retro games collection", 
                "01.06.2020", ""
            ])
            writer.writerow([
                "7", "Documentation Archive", "Internal", "7", "Schrank 1", 
                "", "Archive", "Project documentation", 
                "15.02.2024", ""
            ])
            writer.writerow([
                "8", "Software Development Kit", "Oracle", "8", "Schrank 2", 
                "SDK-2024-001", "Program", "Java Development Kit", 
                "20.01.2024", "20.01.2027"
            ])
        
        return str(file_path)

    def test_import_locations_from_access_csv(self):
        """Test importing locations from Access CSV format."""
        csv_file = self._create_access_locations_csv("locations.csv")
        
        # Read and parse CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        # Parse locations
        locations, errors = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=True
        )
        
        # Verify parsing
        self.assertEqual(len(locations), 8)
        self.assertEqual(len(errors), 0)
        
        # Verify first location
        self.assertEqual(locations[0].box, "1")
        self.assertEqual(locations[0].place, "Regal A")
        self.assertEqual(locations[0].detail, "Oben")
        self.assertEqual(locations[0].id, 1)
        
        # Verify last location
        self.assertEqual(locations[7].box, "8")
        self.assertEqual(locations[7].place, "Schrank 2")
        self.assertEqual(locations[7].detail, "Fach 1")
        self.assertEqual(locations[7].id, 8)

    def test_import_media_from_access_csv(self):
        """Test importing media from Access CSV format."""
        # First import locations
        locations_csv = self._create_access_locations_csv("locations.csv")
        with open(locations_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        locations, _ = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=True
        )
        
        # Now import media
        media_csv = self._create_access_media_csv("media.csv")
        with open(media_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        media_list, errors = AccessCSVMapper.parse_media_rows(
            rows,
            locations,
            skip_header=True
        )
        
        # Verify parsing
        self.assertEqual(len(media_list), 8)
        self.assertEqual(len(errors), 0)
        
        # Verify first media
        self.assertEqual(media_list[0].name, "Windows 10 Pro")
        self.assertEqual(media_list[0].company, "Microsoft")
        self.assertEqual(media_list[0].media_type, "Unknown")  # Default when not in CSV
        self.assertEqual(media_list[0].type, "Program")  # Art field stored in type
        self.assertEqual(media_list[0].license_code, "XXXXX-XXXXX-XXXXX")
        self.assertEqual(media_list[0].creation_date, date(2020, 1, 1))
        self.assertEqual(media_list[0].valid_until_date, date(2025, 1, 1))
        self.assertEqual(media_list[0].location_id, 1)
        
        # Verify backup media
        self.assertEqual(media_list[2].name, "Backup Archive 2024")
        self.assertEqual(media_list[2].media_type, "Unknown")  # Default when not in CSV
        self.assertEqual(media_list[2].type, "Backup")  # Art field stored in type
        
        # Verify media without valid_until_date
        self.assertEqual(media_list[3].name, "Photo Collection 2023")
        self.assertIsNone(media_list[3].valid_until_date)

    def test_import_and_store_in_database(self):
        """Test importing CSV and storing in database."""
        # Import locations
        locations_csv = self._create_access_locations_csv("locations.csv")
        with open(locations_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        locations, _ = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=True
        )
        
        # Store locations in database
        for location in locations:
            self.location_repo.create(location)
        
        # Import media
        media_csv = self._create_access_media_csv("media.csv")
        with open(media_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        media_list, _ = AccessCSVMapper.parse_media_rows(
            rows,
            locations,
            skip_header=True
        )
        
        # Store media in database
        for media in media_list:
            self.media_repo.create(media)
        
        # Verify data in database
        all_media = self.media_repo.get_all()
        self.assertEqual(len(all_media), 8)
        
        all_locations = self.location_repo.get_all()
        self.assertEqual(len(all_locations), 8)
        
        # Verify specific media
        windows_media = [m for m in all_media if m.name == "Windows 10 Pro"][0]
        self.assertEqual(windows_media.company, "Microsoft")
        self.assertEqual(windows_media.media_type, "Unknown")

    def test_export_imported_data_to_csv(self):
        """Test exporting imported data back to CSV."""
        # Import locations
        locations_csv = self._create_access_locations_csv("locations.csv")
        with open(locations_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        locations, _ = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=True
        )
        
        # Import media
        media_csv = self._create_access_media_csv("media.csv")
        with open(media_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        media_list, _ = AccessCSVMapper.parse_media_rows(
            rows,
            locations,
            skip_header=True
        )
        
        # Export media to CSV
        export_file = Path(self.temp_dir) / "export_media.csv"
        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = [
                "Name", "Media Type", "Company", "License Code",
                "Creation Date", "Valid Until Date", "Content Description",
                "Remarks", "Location ID"
            ]
            writer.writerow(headers)
            
            # Write media
            for media in media_list:
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
        
        # Verify export file
        self.assertTrue(export_file.exists())
        
        # Read and verify content
        with open(export_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 9)  # Header + 8 media
        self.assertEqual(rows[0][0], "Name")
        self.assertEqual(rows[1][0], "Windows 10 Pro")
        self.assertEqual(rows[1][1], "DVD")
        self.assertEqual(rows[1][2], "Microsoft")

    def test_round_trip_import_export(self):
        """Test round-trip: import CSV -> store -> export CSV."""
        # Import locations
        locations_csv = self._create_access_locations_csv("locations.csv")
        with open(locations_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        locations, _ = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=True
        )
        
        # Store locations
        for location in locations:
            self.location_repo.create(location)
        
        # Import media
        media_csv = self._create_access_media_csv("media.csv")
        with open(media_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        media_list, _ = AccessCSVMapper.parse_media_rows(
            rows,
            locations,
            skip_header=True
        )
        
        # Store media
        for media in media_list:
            self.media_repo.create(media)
        
        # Retrieve from database
        retrieved_media = self.media_repo.get_all()
        retrieved_locations = self.location_repo.get_all()
        
        # Export to CSV
        export_media_file = Path(self.temp_dir) / "export_media.csv"
        with open(export_media_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Media Type", "Company", "License Code", 
                           "Creation Date", "Valid Until Date", "Content Description"])
            for media in retrieved_media:
                writer.writerow([
                    media.name,
                    media.media_type,
                    media.company or "",
                    media.license_code or "",
                    media.creation_date.isoformat() if media.creation_date else "",
                    media.valid_until_date.isoformat() if media.valid_until_date else "",
                    media.content_description or "",
                ])
        
        # Verify round-trip
        self.assertEqual(len(retrieved_media), 8)
        self.assertEqual(len(retrieved_locations), 8)
        
        # Verify specific data integrity
        windows = [m for m in retrieved_media if m.name == "Windows 10 Pro"][0]
        self.assertEqual(windows.company, "Microsoft")
        self.assertEqual(windows.media_type, "Unknown")
        self.assertEqual(windows.creation_date, date(2020, 1, 1))

    def test_import_with_missing_locations(self):
        """Test importing media when some locations don't exist."""
        # Create minimal locations
        locations = [
            StorageLocation(box="1", place="Regal A", detail="Oben"),
        ]
        locations[0].id = 1
        
        # Import full media CSV
        media_csv = self._create_access_media_csv("media.csv")
        with open(media_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        media_list, errors = AccessCSVMapper.parse_media_rows(
            rows,
            locations,
            skip_header=True
        )
        
        # Should import all media, but some won't have location_id
        self.assertEqual(len(media_list), 8)
        self.assertEqual(len(errors), 0)
        
        # First media should have location
        self.assertEqual(media_list[0].location_id, 1)
        
        # Other media should not have location
        for media in media_list[1:]:
            self.assertIsNone(media.location_id)

    def test_import_media_with_special_characters(self):
        """Test importing media with special characters."""
        file_path = Path(self.temp_dir) / "special_chars.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            writer.writerow([
                "ID", "Name", "Firma", "Box", "Position", "Code", "Art", 
                "Bemerkung", "Datum", "Verfällt am"
            ])
            writer.writerow([
                "1", "Café™ Collection®", "Société Générale", "1", "Regal A", 
                "CODE-123", "Archive", "Spécial édition", 
                "01.01.2020", "01.01.2025"
            ])
            writer.writerow([
                "2", "Tëst Mëdia", "Tëst Company", "1", "Regal A", 
                "", "Program", "Tëst dëscription", 
                "15.03.2021", ""
            ])
        
        # Create location
        locations = [StorageLocation(box="1", place="Regal A", detail="Oben")]
        locations[0].id = 1
        
        # Parse
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        media_list, errors = AccessCSVMapper.parse_media_rows(
            rows,
            locations,
            skip_header=True
        )
        
        # Verify special characters are preserved
        self.assertEqual(len(media_list), 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(media_list[0].name, "Café™ Collection®")
        self.assertEqual(media_list[0].company, "Société Générale")
        self.assertEqual(media_list[1].name, "Tëst Mëdia")


class TestCSVFormatVariations(unittest.TestCase):
    """Tests for different CSV format variations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_csv_with_comma_delimiter(self):
        """Test parsing CSV with comma delimiter."""
        file_path = Path(self.temp_dir) / "comma_delimited.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',')
            
            writer.writerow([
                "ID", "Name", "Firma", "Box", "Position", "Code", "Art", 
                "Bemerkung", "Datum", "Verfällt am"
            ])
            writer.writerow([
                "1", "Test Media", "Company", "1", "Shelf A", "CODE", 
                "Program", "Description", "01.01.2020", "01.01.2025"
            ])
        
        # Parse with comma delimiter
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], "Test Media")

    def test_csv_with_semicolon_delimiter(self):
        """Test parsing CSV with semicolon delimiter."""
        file_path = Path(self.temp_dir) / "semicolon_delimited.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            writer.writerow([
                "ID", "Name", "Firma", "Box", "Position", "Code", "Art", 
                "Bemerkung", "Datum", "Verfällt am"
            ])
            writer.writerow([
                "1", "Test Media", "Company", "1", "Shelf A", "CODE", 
                "Program", "Description", "01.01.2020", "01.01.2025"
            ])
        
        # Parse with semicolon delimiter
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], "Test Media")

    def test_csv_with_quoted_fields(self):
        """Test parsing CSV with quoted fields containing delimiters."""
        file_path = Path(self.temp_dir) / "quoted_fields.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            
            writer.writerow([
                "ID", "Name", "Firma", "Box", "Position", "Code", "Art", 
                "Bemerkung", "Datum", "Verfällt am"
            ])
            writer.writerow([
                "1", "Test; Media", "Company; Inc.", "1", "Shelf A", "CODE", 
                "Program", "Description; with; semicolons", "01.01.2020", "01.01.2025"
            ])
        
        # Parse
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], "Test; Media")
        self.assertEqual(rows[1][2], "Company; Inc.")


if __name__ == '__main__':
    unittest.main()
