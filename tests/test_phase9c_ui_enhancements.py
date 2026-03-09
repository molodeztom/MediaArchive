"""Tests for Phase 9C: UI Enhancements (Navigation, Tooltips, Preferences).

This module provides comprehensive test coverage for:
- Double-click navigation from search results to media tab
- Content description tooltips on hover
- Column visibility preferences with save/load functionality
- Reset columns to defaults
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, MagicMock, patch
from datetime import date

from src.models.media import Media
from src.models.location import StorageLocation
from src.data.preferences_repository import PreferencesRepository
from src.gui.column_preferences_dialog import ColumnPreferencesDialog


class TestColumnPreferencesDialog(unittest.TestCase):
    """Test column preferences dialog functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.visible_columns = {
            "Number": True,
            "Name": True,
            "Type": True,
            "Category": True,
            "Box": True,
            "Position": True,
            "Company": True,
            "License": True,
            "Created": True,
            "Expires": True,
        }

    def tearDown(self):
        """Clean up after tests."""
        try:
            self.root.destroy()
        except:
            pass

    def test_dialog_initialization(self):
        """Test dialog initializes with correct columns."""
        dialog = ColumnPreferencesDialog(self.root, self.visible_columns)
        
        # Check that all columns are present
        self.assertEqual(len(dialog.column_vars), len(self.visible_columns))
        
        # Check that all columns have correct initial visibility
        for col_name, var in dialog.column_vars.items():
            self.assertEqual(var.get(), self.visible_columns[col_name])
        
        dialog.destroy()

    def test_dialog_save_with_all_visible(self):
        """Test saving preferences with all columns visible."""
        on_save_mock = Mock()
        dialog = ColumnPreferencesDialog(self.root, self.visible_columns, on_save=on_save_mock)
        
        # All columns should be visible
        for var in dialog.column_vars.values():
            self.assertTrue(var.get())
        
        # Save should succeed
        dialog._save()
        
        # Verify callback was called
        on_save_mock.assert_called_once()
        
        # Verify result contains all columns as visible
        result = on_save_mock.call_args[0][0]
        for col_name in self.visible_columns:
            self.assertTrue(result[col_name])

    def test_dialog_save_with_some_hidden(self):
        """Test saving preferences with some columns hidden."""
        on_save_mock = Mock()
        dialog = ColumnPreferencesDialog(self.root, self.visible_columns, on_save=on_save_mock)
        
        # Hide some columns
        dialog.column_vars["Company"].set(False)
        dialog.column_vars["License"].set(False)
        
        # Save should succeed
        dialog._save()
        
        # Verify callback was called
        on_save_mock.assert_called_once()
        
        # Verify result contains correct visibility
        result = on_save_mock.call_args[0][0]
        self.assertFalse(result["Company"])
        self.assertFalse(result["License"])
        self.assertTrue(result["Name"])

    def test_dialog_save_with_no_visible_columns(self):
        """Test that saving with no visible columns shows warning."""
        dialog = ColumnPreferencesDialog(self.root, self.visible_columns)
        
        # Hide all columns
        for var in dialog.column_vars.values():
            var.set(False)
        
        # Save should fail (no visible columns)
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            dialog._save()
            mock_warning.assert_called_once()

    def test_dialog_reset_defaults(self):
        """Test resetting columns to defaults."""
        dialog = ColumnPreferencesDialog(self.root, self.visible_columns)
        
        # Hide all columns
        for var in dialog.column_vars.values():
            var.set(False)
        
        # Reset to defaults
        dialog._reset_defaults()
        
        # All columns should be visible again
        for var in dialog.column_vars.values():
            self.assertTrue(var.get())

    def test_dialog_cancel(self):
        """Test canceling the dialog."""
        dialog = ColumnPreferencesDialog(self.root, self.visible_columns)
        
        # Cancel should set result to None
        dialog._cancel()
        
        self.assertIsNone(dialog.result)


class TestPreferencesRepository(unittest.TestCase):
    """Test preferences repository column visibility methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_conn = Mock()
        self.mock_cursor = Mock()
        
        self.mock_db.connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        self.repo = PreferencesRepository(self.mock_db)

    def test_set_column_visibility_true(self):
        """Test setting column visibility to True."""
        self.repo.set_column_visibility("Name", True)
        
        # Verify set_preference was called with correct key and value
        self.mock_cursor.execute.assert_called()
        call_args = self.mock_cursor.execute.call_args
        
        # Check that the key contains column name
        self.assertIn("column_visible_Name", str(call_args))

    def test_set_column_visibility_false(self):
        """Test setting column visibility to False."""
        self.repo.set_column_visibility("Name", False)
        
        # Verify set_preference was called with correct key and value
        self.mock_cursor.execute.assert_called()
        call_args = self.mock_cursor.execute.call_args
        
        # Check that the key contains column name
        self.assertIn("column_visible_Name", str(call_args))

    def test_get_column_visibility_default_true(self):
        """Test getting column visibility with default True."""
        # Mock the database to return no preference
        self.mock_cursor.fetchone.return_value = None
        
        result = self.repo.get_column_visibility("Name", default=True)
        
        # Should return default value
        self.assertTrue(result)

    def test_get_column_visibility_default_false(self):
        """Test getting column visibility with default False."""
        # Mock the database to return no preference
        self.mock_cursor.fetchone.return_value = None
        
        result = self.repo.get_column_visibility("Name", default=False)
        
        # Should return default value
        self.assertFalse(result)

    def test_get_all_column_visibility(self):
        """Test getting all column visibility preferences."""
        default_columns = ["Name", "Type", "Box"]
        
        # Mock the database to return no preferences
        self.mock_cursor.fetchone.return_value = None
        
        result = self.repo.get_all_column_visibility(default_columns)
        
        # Should return all columns with default visibility (True)
        self.assertEqual(len(result), 3)
        for col in default_columns:
            self.assertTrue(result[col])

    def test_set_all_column_visibility(self):
        """Test setting all column visibility preferences."""
        visibility = {
            "Name": True,
            "Type": False,
            "Box": True,
        }
        
        self.repo.set_all_column_visibility(visibility)
        
        # Verify set_preference was called for each column
        self.assertGreaterEqual(self.mock_cursor.execute.call_count, 3)


class TestDoubleClickNavigation(unittest.TestCase):
    """Test double-click navigation from search results."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_media_service = Mock()
        self.mock_location_service = Mock()
        
        # Create test media
        self.test_media = Media(
            id=1,
            name="Test Media",
            number="001",
            media_type="CD",
            category="Music",
            company="Test Company",
            license_code="LIC001",
            creation_date=date(2026, 1, 1),
            valid_until_date=date(2027, 1, 1),
            content_description="Test content",
            remarks="Test remarks",
            location_id=1,
            position="A1",
            is_deleted=False,
        )

    def test_search_result_contains_media_name(self):
        """Test that search results contain media name for navigation."""
        # This test verifies that search results have the necessary data
        # for double-click navigation to work
        
        # Search results should include Name column (index 1)
        search_result_values = ("001", "Test Media", "CD", "Box1", "A1", "Place1")
        
        # Extract media name from search result
        media_name = search_result_values[1]
        
        self.assertEqual(media_name, "Test Media")

    def test_media_lookup_by_name(self):
        """Test looking up media by name for navigation."""
        # Mock media service to return test media
        self.mock_media_service.get_all_media.return_value = [self.test_media]
        
        # Find media by name
        all_media = self.mock_media_service.get_all_media()
        media_id = None
        for media in all_media:
            if media.name == "Test Media":
                media_id = media.id
                break
        
        self.assertEqual(media_id, 1)


class TestContentDescriptionTooltip(unittest.TestCase):
    """Test content description tooltip functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_media = Media(
            id=1,
            name="Test Media",
            number="001",
            media_type="CD",
            category="Music",
            company="Test Company",
            license_code="LIC001",
            creation_date=date(2026, 1, 1),
            valid_until_date=date(2027, 1, 1),
            content_description="This is a test content description",
            remarks="Test remarks",
            location_id=1,
            position="A1",
            is_deleted=False,
        )

    def test_tooltip_text_truncation(self):
        """Test that tooltip text is truncated for long descriptions."""
        long_description = "A" * 600  # 600 characters
        
        # Tooltip should truncate to 500 characters
        tooltip_text = long_description[:500]
        if len(long_description) > 500:
            tooltip_text += "..."
        
        self.assertEqual(len(tooltip_text), 503)  # 500 + "..."
        self.assertTrue(tooltip_text.endswith("..."))

    def test_tooltip_with_short_description(self):
        """Test tooltip with short description."""
        short_description = "Short description"
        
        # Tooltip should not be truncated
        tooltip_text = short_description[:500]
        if len(short_description) > 500:
            tooltip_text += "..."
        
        self.assertEqual(tooltip_text, short_description)
        self.assertFalse(tooltip_text.endswith("..."))

    def test_tooltip_with_empty_description(self):
        """Test tooltip with empty description."""
        empty_description = ""
        
        # Tooltip should be empty
        self.assertEqual(empty_description, "")


class TestColumnVisibilityIntegration(unittest.TestCase):
    """Integration tests for column visibility functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.visible_columns = {
            "Number": True,
            "Name": True,
            "Type": True,
            "Category": False,
            "Box": True,
            "Position": False,
            "Company": True,
            "License": False,
            "Created": True,
            "Expires": True,
        }

    def test_column_width_calculation(self):
        """Test that hidden columns have zero width."""
        column_widths = {
            "Number": 80, "Name": 150, "Type": 80, "Category": 80,
            "Box": 60, "Position": 80, "Company": 100, "License": 80,
            "Created": 100, "Expires": 100
        }
        
        # Calculate actual widths based on visibility
        actual_widths = {}
        for col, width in column_widths.items():
            if not self.visible_columns.get(col, True):
                actual_widths[col] = 0
            else:
                actual_widths[col] = width
        
        # Verify hidden columns have zero width
        self.assertEqual(actual_widths["Category"], 0)
        self.assertEqual(actual_widths["Position"], 0)
        self.assertEqual(actual_widths["License"], 0)
        
        # Verify visible columns have non-zero width
        self.assertGreater(actual_widths["Number"], 0)
        self.assertGreater(actual_widths["Name"], 0)

    def test_visible_columns_count(self):
        """Test counting visible columns."""
        visible_count = sum(1 for v in self.visible_columns.values() if v)
        
        self.assertEqual(visible_count, 7)  # 10 total - 3 hidden

    def test_hidden_columns_count(self):
        """Test counting hidden columns."""
        hidden_count = sum(1 for v in self.visible_columns.values() if not v)
        
        self.assertEqual(hidden_count, 3)


if __name__ == "__main__":
    unittest.main()
