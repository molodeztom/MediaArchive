"""Tests for Phase 6a: Access CSV mapper functionality.

This module provides comprehensive tests for the Access CSV mapper that converts
Access database export format to Media Archive format.
"""

import unittest
from datetime import date
import sys
from pathlib import Path

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
from utils.exceptions import ValidationError


class TestAccessMediaTypeMapper(unittest.TestCase):
    """Tests for media type mapping."""

    def test_map_archive_to_dvd(self):
        """Test mapping Archive to DVD."""
        result = AccessMediaTypeMapper.map_media_type("Archive")
        self.assertEqual(result, "DVD")

    def test_map_image_to_dvd(self):
        """Test mapping Image to DVD."""
        result = AccessMediaTypeMapper.map_media_type("Image")
        self.assertEqual(result, "DVD")

    def test_map_lexica_to_dvd(self):
        """Test mapping Lexica to DVD."""
        result = AccessMediaTypeMapper.map_media_type("Lexica")
        self.assertEqual(result, "DVD")

    def test_map_program_to_dvd(self):
        """Test mapping Program to DVD."""
        result = AccessMediaTypeMapper.map_media_type("Program")
        self.assertEqual(result, "DVD")

    def test_map_backup_to_external_hdd(self):
        """Test mapping Backup to External-HDD."""
        result = AccessMediaTypeMapper.map_media_type("Backup")
        self.assertEqual(result, "External-HDD")

    def test_map_game_to_dvd(self):
        """Test mapping Game to DVD."""
        result = AccessMediaTypeMapper.map_media_type("Game")
        self.assertEqual(result, "DVD")

    def test_map_unknown_to_other(self):
        """Test mapping unknown type to Other."""
        result = AccessMediaTypeMapper.map_media_type("Unknown")
        self.assertEqual(result, "Other")

    def test_map_empty_to_other(self):
        """Test mapping empty string to Other."""
        result = AccessMediaTypeMapper.map_media_type("")
        self.assertEqual(result, "Other")

    def test_map_whitespace_to_other(self):
        """Test mapping whitespace to Other."""
        result = AccessMediaTypeMapper.map_media_type("   ")
        self.assertEqual(result, "Other")


class TestAccessDateConverter(unittest.TestCase):
    """Tests for date conversion."""

    def test_convert_valid_date(self):
        """Test converting valid date DD.MM.YYYY."""
        result = AccessDateConverter.convert_date("07.03.2024")
        self.assertEqual(result, date(2024, 3, 7))

    def test_convert_date_with_time(self):
        """Test converting date with time (time part ignored)."""
        result = AccessDateConverter.convert_date("07.03.2024 14:30")
        self.assertEqual(result, date(2024, 3, 7))

    def test_convert_date_with_seconds(self):
        """Test converting date with time including seconds."""
        result = AccessDateConverter.convert_date("07.03.2024 14:30:45")
        self.assertEqual(result, date(2024, 3, 7))

    def test_convert_empty_date(self):
        """Test converting empty date string."""
        result = AccessDateConverter.convert_date("")
        self.assertIsNone(result)

    def test_convert_whitespace_date(self):
        """Test converting whitespace date string."""
        result = AccessDateConverter.convert_date("   ")
        self.assertIsNone(result)

    def test_convert_invalid_date_format(self):
        """Test converting invalid date format."""
        with self.assertRaises(ValidationError):
            AccessDateConverter.convert_date("2024-03-07")

    def test_convert_invalid_date_values(self):
        """Test converting invalid date values."""
        with self.assertRaises(ValidationError):
            AccessDateConverter.convert_date("32.13.2024")

    def test_convert_date_with_leading_zeros(self):
        """Test converting date with leading zeros."""
        result = AccessDateConverter.convert_date("01.01.2024")
        self.assertEqual(result, date(2024, 1, 1))

    def test_convert_date_end_of_month(self):
        """Test converting end of month date."""
        result = AccessDateConverter.convert_date("31.12.2024")
        self.assertEqual(result, date(2024, 12, 31))


class TestAccessCSVMapper(unittest.TestCase):
    """Tests for media CSV mapping."""

    def setUp(self):
        """Set up test fixtures."""
        self.locations = [
            StorageLocation(box="Box 1", place="Shelf A", detail="Top shelf"),
            StorageLocation(box="Box 2", place="Shelf B", detail="Middle shelf"),
        ]
        # Set IDs manually for testing
        self.locations[0].id = 1
        self.locations[1].id = 2

    def test_parse_valid_media_row(self):
        """Test parsing valid media row."""
        row = [
            "1",  # ID
            "Windows 10 Pro",  # Name
            "Microsoft",  # Company
            "Box 1",  # Box
            "Shelf A",  # Place
            "XXXXX-XXXXX-XXXXX",  # License Code
            "Program",  # Art (Content Type)
            "Operating System",  # Bemerkung (Content Description)
            "01.01.2020",  # Datum (Creation Date)
            "01.01.2025",  # Verfällt am (Valid Until Date)
        ]
        
        media, error = AccessCSVMapper.parse_media_row(row, self.locations)
        
        self.assertIsNone(error)
        self.assertIsNotNone(media)
        self.assertEqual(media.name, "Windows 10 Pro")
        self.assertEqual(media.company, "Microsoft")
        self.assertEqual(media.media_type, "Unknown")  # Default when not in CSV
        self.assertEqual(media.type, "Program")  # Art field stored in type
        self.assertEqual(media.license_code, "XXXXX-XXXXX-XXXXX")
        self.assertEqual(media.content_description, "Operating System")
        self.assertEqual(media.creation_date, date(2020, 1, 1))
        self.assertEqual(media.valid_until_date, date(2025, 1, 1))
        self.assertEqual(media.location_id, 1)  # Box 1, Shelf A

    def test_parse_media_row_missing_name(self):
        """Test parsing media row with missing name."""
        row = [
            "1",  # ID
            "",  # Name (missing)
            "Microsoft",  # Company
            "Box 1",  # Box
            "Shelf A",  # Place
            "CODE",  # License Code
            "Program",  # Art
            "Description",  # Bemerkung
            "01.01.2020",  # Datum
            "01.01.2025",  # Verfällt am
        ]
        
        media, error = AccessCSVMapper.parse_media_row(row, self.locations)
        
        self.assertIsNone(media)
        self.assertIsNotNone(error)
        self.assertIn("Name is required", error)

    def test_parse_media_row_missing_media_type(self):
        """Test parsing media row with missing Art field (now optional)."""
        row = [
            "1",  # ID
            "Test Media",  # Name
            "Company",  # Company
            "Box 1",  # Box
            "Shelf A",  # Place
            "CODE",  # License Code
            "",  # Art (missing - now optional)
            "Description",  # Bemerkung
            "01.01.2020",  # Datum
            "01.01.2025",  # Verfällt am
        ]
        
        media, error = AccessCSVMapper.parse_media_row(row, self.locations)
        
        # Art field is now optional, so media should be created successfully
        self.assertIsNone(error)
        self.assertIsNotNone(media)
        self.assertEqual(media.name, "Test Media")
        self.assertEqual(media.media_type, "Unknown")  # Default when not in CSV
        self.assertIsNone(media.type)  # Art field is empty, so type is None
        self.assertEqual(media.content_description, "Description")

    def test_parse_media_row_location_not_found(self):
        """Test parsing media row with location not found."""
        row = [
            "1",  # ID
            "Test Media",  # Name
            "Company",  # Company
            "Box 99",  # Box (not found)
            "Shelf Z",  # Place (not found)
            "CODE",  # License Code
            "Program",  # Art
            "Description",  # Bemerkung
            "01.01.2020",  # Datum
            "01.01.2025",  # Verfällt am
        ]
        
        media, error = AccessCSVMapper.parse_media_row(row, self.locations)
        
        self.assertIsNone(error)
        self.assertIsNotNone(media)
        self.assertIsNone(media.location_id)  # Location not found

    def test_parse_media_row_insufficient_columns(self):
        """Test parsing media row with insufficient columns."""
        row = ["1", "Test Media", "Company"]  # Only 3 columns
        
        media, error = AccessCSVMapper.parse_media_row(row, self.locations)
        
        self.assertIsNone(media)
        self.assertIsNotNone(error)
        self.assertIn("insufficient columns", error)

    def test_parse_media_rows_with_header(self):
        """Test parsing multiple media rows with header."""
        rows = [
            ["ID", "Name", "Firma", "Box", "Position", "Code", "Art", "Bemerkung", "Datum", "Verfällt am"],  # Header
            ["1", "Media 1", "Company 1", "Box 1", "Shelf A", "CODE1", "Program", "Desc 1", "01.01.2020", "01.01.2025"],
            ["2", "Media 2", "Company 2", "Box 2", "Shelf B", "CODE2", "Backup", "Desc 2", "02.02.2020", "02.02.2025"],
        ]
        
        media_list, errors = AccessCSVMapper.parse_media_rows(rows, self.locations, skip_header=True)
        
        self.assertEqual(len(media_list), 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(media_list[0].name, "Media 1")
        self.assertEqual(media_list[1].name, "Media 2")

    def test_parse_media_rows_with_errors(self):
        """Test parsing multiple media rows with some errors."""
        rows = [
            ["ID", "Name", "Firma", "Box", "Position", "Code", "Art", "Bemerkung", "Datum", "Verfällt am"],  # Header
            ["1", "Media 1", "Company 1", "Box 1", "Shelf A", "CODE1", "Program", "Desc 1", "01.01.2020", "01.01.2025"],
            ["2", "", "Company 2", "Box 2", "Shelf B", "CODE2", "Backup", "Desc 2", "02.02.2020", "02.02.2025"],  # Missing name
        ]
        
        media_list, errors = AccessCSVMapper.parse_media_rows(rows, self.locations, skip_header=True)
        
        self.assertEqual(len(media_list), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("Name is required", errors[0])


class TestAccessLocationMapper(unittest.TestCase):
    """Tests for location CSV mapping."""

    def test_parse_valid_location_row(self):
        """Test parsing valid location row."""
        row = ["Box 1", "Shelf A", "Top shelf"]
        
        location, error = AccessLocationMapper.parse_location_row(row)
        
        self.assertIsNone(error)
        self.assertIsNotNone(location)
        self.assertEqual(location.box, "Box 1")
        self.assertEqual(location.place, "Shelf A")
        self.assertEqual(location.detail, "Top shelf")

    def test_parse_location_row_without_detail(self):
        """Test parsing location row without detail."""
        row = ["Box 1", "Shelf A"]
        
        location, error = AccessLocationMapper.parse_location_row(row)
        
        self.assertIsNone(error)
        self.assertIsNotNone(location)
        self.assertEqual(location.box, "Box 1")
        self.assertEqual(location.place, "Shelf A")
        self.assertIsNone(location.detail)

    def test_parse_location_row_missing_box(self):
        """Test parsing location row with missing box."""
        row = ["", "Shelf A", "Detail"]
        
        location, error = AccessLocationMapper.parse_location_row(row)
        
        self.assertIsNone(location)
        self.assertIsNotNone(error)
        self.assertIn("Box is required", error)

    def test_parse_location_row_missing_place(self):
        """Test parsing location row with missing place."""
        row = ["Box 1", "", "Detail"]
        
        location, error = AccessLocationMapper.parse_location_row(row)
        
        self.assertIsNone(location)
        self.assertIsNotNone(error)
        self.assertIn("Place is required", error)

    def test_parse_location_row_insufficient_columns(self):
        """Test parsing location row with insufficient columns."""
        row = ["Box 1"]  # Only 1 column
        
        location, error = AccessLocationMapper.parse_location_row(row)
        
        self.assertIsNone(location)
        self.assertIsNotNone(error)
        self.assertIn("insufficient columns", error)

    def test_parse_location_rows_with_header(self):
        """Test parsing multiple location rows with header."""
        rows = [
            ["Box", "Place", "Detail"],  # Header
            ["Box 1", "Shelf A", "Top shelf"],
            ["Box 2", "Shelf B", "Middle shelf"],
        ]
        
        location_list, errors = AccessLocationMapper.parse_location_rows(rows, skip_header=True)
        
        self.assertEqual(len(location_list), 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(location_list[0].box, "Box 1")
        self.assertEqual(location_list[1].box, "Box 2")

    def test_parse_location_rows_with_errors(self):
        """Test parsing multiple location rows with some errors."""
        rows = [
            ["Box", "Place", "Detail"],  # Header
            ["Box 1", "Shelf A", "Top shelf"],
            ["", "Shelf B", "Middle shelf"],  # Missing box
        ]
        
        location_list, errors = AccessLocationMapper.parse_location_rows(rows, skip_header=True)
        
        self.assertEqual(len(location_list), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("Box is required", errors[0])

    def test_parse_location_with_internal_id(self):
        """Test parsing location with internal ID."""
        row = ["Box 1", "Shelf A", "Top shelf"]
        
        location, error = AccessLocationMapper.parse_location_row(row, internal_id=42)
        
        self.assertIsNone(error)
        self.assertIsNotNone(location)
        self.assertEqual(location.id, 42)
        self.assertEqual(location.box, "Box 1")

    def test_parse_location_rows_with_internal_ids(self):
        """Test parsing multiple location rows with internal ID generation."""
        rows = [
            ["Box", "Ort", "Typ"],  # Header (new format)
            ["1", "Regal A", "Oben"],
            ["2", "Regal B", "Mitte"],
            ["3", "Regal C", "Unten"],
        ]
        
        location_list, errors = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=True
        )
        
        self.assertEqual(len(location_list), 3)
        self.assertEqual(len(errors), 0)
        # Check internal IDs are generated sequentially
        self.assertEqual(location_list[0].id, 1)
        self.assertEqual(location_list[1].id, 2)
        self.assertEqual(location_list[2].id, 3)
        # Check box numbers are preserved for user reference
        self.assertEqual(location_list[0].box, "1")
        self.assertEqual(location_list[1].box, "2")
        self.assertEqual(location_list[2].box, "3")

    def test_parse_location_rows_without_internal_ids(self):
        """Test parsing location rows without internal ID generation."""
        rows = [
            ["Box", "Place", "Detail"],
            ["Box 1", "Shelf A", "Top shelf"],
            ["Box 2", "Shelf B", "Middle shelf"],
        ]
        
        location_list, errors = AccessLocationMapper.parse_location_rows(
            rows,
            skip_header=True,
            generate_internal_ids=False
        )
        
        self.assertEqual(len(location_list), 2)
        self.assertEqual(len(errors), 0)
        # Check internal IDs are not set
        self.assertIsNone(location_list[0].id)
        self.assertIsNone(location_list[1].id)

    def test_parse_location_new_format_ort_typ(self):
        """Test parsing location with new format (Box;Ort;Typ)."""
        row = ["1", "Regal A", "Oben"]
        
        location, error = AccessLocationMapper.parse_location_row(row)
        
        self.assertIsNone(error)
        self.assertIsNotNone(location)
        self.assertEqual(location.box, "1")  # Box number visible to user
        self.assertEqual(location.place, "Regal A")  # Ort (Place)
        self.assertEqual(location.detail, "Oben")  # Typ (Detail)


if __name__ == '__main__':
    unittest.main()
