"""Tests for Phase 9E: Date Picker and Logging Preferences.

This module provides comprehensive tests for Phase 9E features:
- Date picker widget functionality
- Logging preferences (enable/disable, log level)
- Auto-set creation date for new media

History:
20260309  V1.0: Initial Phase 9E test suite
"""

import unittest
import logging
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.database import Database
from data.preferences_repository import PreferencesRepository
from business.media_service import MediaService
from gui.logging_config import configure_logging, set_logging_enabled, set_logging_level, is_logging_enabled
from utils.date_utils import format_date, parse_date


class TestDatePickerFunctionality(unittest.TestCase):
    """Test date picker widget functionality."""

    def test_format_date_with_valid_date(self):
        """Test formatting a valid date."""
        test_date = date(2026, 3, 9)
        formatted = format_date(test_date)
        self.assertEqual(formatted, "09.03.2026")

    def test_format_date_with_none(self):
        """Test formatting None returns empty string."""
        formatted = format_date(None)
        self.assertEqual(formatted, "")

    def test_parse_date_with_dd_mm_yyyy_format(self):
        """Test parsing date in DD.MM.YYYY format."""
        parsed = parse_date("09.03.2026")
        self.assertEqual(parsed, date(2026, 3, 9))

    def test_parse_date_with_yyyy_mm_dd_format(self):
        """Test parsing date in YYYY-MM-DD format (backward compatibility)."""
        parsed = parse_date("2026-03-09")
        self.assertEqual(parsed, date(2026, 3, 9))

    def test_parse_date_with_empty_string(self):
        """Test parsing empty string returns None."""
        parsed = parse_date("")
        self.assertIsNone(parsed)

    def test_parse_date_with_whitespace(self):
        """Test parsing whitespace-only string returns None."""
        parsed = parse_date("   ")
        self.assertIsNone(parsed)

    def test_parse_date_with_invalid_format(self):
        """Test parsing invalid date format raises ValueError."""
        with self.assertRaises(ValueError):
            parse_date("invalid-date")

    def test_parse_date_with_invalid_day(self):
        """Test parsing invalid day raises ValueError."""
        with self.assertRaises(ValueError):
            parse_date("32.03.2026")

    def test_parse_date_with_invalid_month(self):
        """Test parsing invalid month raises ValueError."""
        with self.assertRaises(ValueError):
            parse_date("09.13.2026")

    def test_date_roundtrip(self):
        """Test formatting and parsing date roundtrip."""
        original_date = date(2026, 3, 9)
        formatted = format_date(original_date)
        parsed = parse_date(formatted)
        self.assertEqual(parsed, original_date)


class TestLoggingPreferences(unittest.TestCase):
    """Test logging preferences functionality."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = Database(str(self.db_path))
        self.db.init_schema()
        self.prefs_repo = PreferencesRepository(self.db)

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_set_logging_enabled_true(self):
        """Test setting logging enabled to True."""
        self.prefs_repo.set_logging_enabled(True)
        enabled = self.prefs_repo.get_logging_enabled()
        self.assertTrue(enabled)

    def test_set_logging_enabled_false(self):
        """Test setting logging enabled to False."""
        self.prefs_repo.set_logging_enabled(False)
        enabled = self.prefs_repo.get_logging_enabled()
        self.assertFalse(enabled)

    def test_get_logging_enabled_default(self):
        """Test getting logging enabled with default value."""
        enabled = self.prefs_repo.get_logging_enabled(default=True)
        self.assertTrue(enabled)

    def test_set_logging_level_debug(self):
        """Test setting logging level to DEBUG."""
        self.prefs_repo.set_logging_level("DEBUG")
        level = self.prefs_repo.get_logging_level()
        self.assertEqual(level, "DEBUG")

    def test_set_logging_level_info(self):
        """Test setting logging level to INFO."""
        self.prefs_repo.set_logging_level("INFO")
        level = self.prefs_repo.get_logging_level()
        self.assertEqual(level, "INFO")

    def test_set_logging_level_warning(self):
        """Test setting logging level to WARNING."""
        self.prefs_repo.set_logging_level("WARNING")
        level = self.prefs_repo.get_logging_level()
        self.assertEqual(level, "WARNING")

    def test_set_logging_level_error(self):
        """Test setting logging level to ERROR."""
        self.prefs_repo.set_logging_level("ERROR")
        level = self.prefs_repo.get_logging_level()
        self.assertEqual(level, "ERROR")

    def test_set_logging_level_critical(self):
        """Test setting logging level to CRITICAL."""
        self.prefs_repo.set_logging_level("CRITICAL")
        level = self.prefs_repo.get_logging_level()
        self.assertEqual(level, "CRITICAL")

    def test_set_logging_level_invalid(self):
        """Test setting invalid logging level raises ValueError."""
        with self.assertRaises(ValueError):
            self.prefs_repo.set_logging_level("INVALID")

    def test_get_logging_level_default(self):
        """Test getting logging level with default value."""
        level = self.prefs_repo.get_logging_level(default="WARNING")
        self.assertEqual(level, "WARNING")


class TestLoggingConfiguration(unittest.TestCase):
    """Test logging configuration functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_configure_logging_enabled(self):
        """Test configuring logging as enabled."""
        configure_logging(log_level=logging.INFO, enabled=True)
        self.assertTrue(is_logging_enabled())

    def test_configure_logging_disabled(self):
        """Test configuring logging as disabled."""
        configure_logging(log_level=logging.INFO, enabled=False)
        self.assertFalse(is_logging_enabled())

    def test_set_logging_enabled_true(self):
        """Test enabling logging dynamically."""
        configure_logging(enabled=False)
        self.assertFalse(is_logging_enabled())
        set_logging_enabled(True)
        self.assertTrue(is_logging_enabled())

    def test_set_logging_enabled_false(self):
        """Test disabling logging dynamically."""
        configure_logging(enabled=True)
        self.assertTrue(is_logging_enabled())
        set_logging_enabled(False)
        self.assertFalse(is_logging_enabled())

    def test_set_logging_level_debug(self):
        """Test setting logging level to DEBUG."""
        configure_logging(log_level=logging.INFO, enabled=True)
        set_logging_level(logging.DEBUG)
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.DEBUG)

    def test_set_logging_level_warning(self):
        """Test setting logging level to WARNING."""
        configure_logging(log_level=logging.INFO, enabled=True)
        set_logging_level(logging.WARNING)
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.WARNING)


class TestAutoSetCreationDate(unittest.TestCase):
    """Test auto-set creation date functionality."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = Database(str(self.db_path))
        self.db.init_schema()
        self.service = MediaService(self.db)

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_auto_set_creation_date_enabled(self):
        """Test auto-setting creation date when enabled."""
        media = self.service.create_media(
            name="Test Media",
            media_type="CD",
            auto_set_creation_date=True
        )
        self.assertIsNotNone(media.creation_date)
        self.assertEqual(media.creation_date, date.today())

    def test_auto_set_creation_date_disabled(self):
        """Test not auto-setting creation date when disabled."""
        media = self.service.create_media(
            name="Test Media",
            media_type="CD",
            auto_set_creation_date=False
        )
        self.assertIsNone(media.creation_date)

    def test_auto_set_creation_date_with_explicit_date(self):
        """Test not overriding explicit creation date."""
        explicit_date = date(2020, 1, 1)
        media = self.service.create_media(
            name="Test Media",
            media_type="CD",
            creation_date=explicit_date,
            auto_set_creation_date=True
        )
        self.assertEqual(media.creation_date, explicit_date)

    def test_auto_set_creation_date_default_enabled(self):
        """Test auto-set creation date is enabled by default."""
        media = self.service.create_media(
            name="Test Media",
            media_type="CD"
        )
        self.assertIsNotNone(media.creation_date)
        self.assertEqual(media.creation_date, date.today())

    def test_multiple_media_with_auto_set_creation_date(self):
        """Test creating multiple media with auto-set creation date."""
        media1 = self.service.create_media(
            name="Media 1",
            media_type="CD"
        )
        media2 = self.service.create_media(
            name="Media 2",
            media_type="DVD"
        )
        
        self.assertEqual(media1.creation_date, date.today())
        self.assertEqual(media2.creation_date, date.today())


class TestDatePickerIntegration(unittest.TestCase):
    """Test date picker integration with media operations."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = Database(str(self.db_path))
        self.db.init_schema()
        self.service = MediaService(self.db)

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_create_media_with_parsed_dates(self):
        """Test creating media with dates parsed from strings."""
        creation_date_str = "09.03.2026"
        valid_until_str = "09.03.2027"
        
        creation_date = parse_date(creation_date_str)
        valid_until_date = parse_date(valid_until_str)
        
        media = self.service.create_media(
            name="Test Media",
            media_type="CD",
            creation_date=creation_date,
            valid_until_date=valid_until_date,
            auto_set_creation_date=False
        )
        
        self.assertEqual(media.creation_date, date(2026, 3, 9))
        self.assertEqual(media.valid_until_date, date(2027, 3, 9))

    def test_format_dates_for_display(self):
        """Test formatting dates for display."""
        media = self.service.create_media(
            name="Test Media",
            media_type="CD",
            valid_until_date=date(2027, 3, 9)
        )
        
        creation_formatted = format_date(media.creation_date)
        valid_until_formatted = format_date(media.valid_until_date)
        
        self.assertEqual(creation_formatted, format_date(date.today()))
        self.assertEqual(valid_until_formatted, "09.03.2027")

    def test_update_media_with_new_dates(self):
        """Test updating media with new dates."""
        media = self.service.create_media(
            name="Test Media",
            media_type="CD"
        )
        
        new_creation_date = date(2020, 1, 1)
        new_valid_until = date(2030, 12, 31)
        
        updated = self.service.update_media(
            media.id,
            creation_date=new_creation_date,
            valid_until_date=new_valid_until
        )
        
        self.assertEqual(updated.creation_date, new_creation_date)
        self.assertEqual(updated.valid_until_date, new_valid_until)


class TestLoggingPreferencesIntegration(unittest.TestCase):
    """Test logging preferences integration."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = Database(str(self.db_path))
        self.db.init_schema()
        self.prefs_repo = PreferencesRepository(self.db)

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_save_and_restore_logging_preferences(self):
        """Test saving and restoring logging preferences."""
        # Save preferences
        self.prefs_repo.set_logging_enabled(False)
        self.prefs_repo.set_logging_level("DEBUG")
        
        # Restore preferences
        enabled = self.prefs_repo.get_logging_enabled()
        level = self.prefs_repo.get_logging_level()
        
        self.assertFalse(enabled)
        self.assertEqual(level, "DEBUG")

    def test_logging_preferences_persistence(self):
        """Test logging preferences persist across sessions."""
        # First session: set preferences
        self.prefs_repo.set_logging_enabled(True)
        self.prefs_repo.set_logging_level("WARNING")
        
        # Simulate new session by creating new repository
        prefs_repo2 = PreferencesRepository(self.db)
        
        # Second session: retrieve preferences
        enabled = prefs_repo2.get_logging_enabled()
        level = prefs_repo2.get_logging_level()
        
        self.assertTrue(enabled)
        self.assertEqual(level, "WARNING")

    def test_logging_preferences_with_defaults(self):
        """Test logging preferences with default values."""
        # Get preferences without setting them
        enabled = self.prefs_repo.get_logging_enabled(default=True)
        level = self.prefs_repo.get_logging_level(default="INFO")
        
        self.assertTrue(enabled)
        self.assertEqual(level, "INFO")


if __name__ == "__main__":
    unittest.main()
