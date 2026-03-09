"""Tests for Phase 4: Media management dialogs.

Tests the dialog windows for adding, editing, and deleting media items.
"""

import unittest
import tkinter as tk
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from src.gui.dialogs import (
    BaseDialog,
    AddMediaDialog,
    EditMediaDialog,
    DeleteConfirmDialog,
)
from src.models.media import Media
from src.models.location import StorageLocation


class TestBaseDialog(unittest.TestCase):
    """Test BaseDialog class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_base_dialog_initialization(self) -> None:
        """Test BaseDialog initialization."""
        dialog = BaseDialog(self.root, "Test Dialog")
        self.assertEqual(dialog.title(), "Test Dialog")
        self.assertIsNone(dialog.result)
        dialog.destroy()

    def test_base_dialog_is_modal(self) -> None:
        """Test that BaseDialog is modal."""
        dialog = BaseDialog(self.root, "Test Dialog")
        # Modal dialogs have grab_set() called
        self.assertTrue(dialog.grab_current())
        dialog.destroy()


class TestAddMediaDialog(unittest.TestCase):
    """Test AddMediaDialog class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.locations = [
            StorageLocation(id=1, box="Box A", place="Shelf 1"),
            StorageLocation(id=2, box="Box B", place="Shelf 2"),
        ]

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_add_media_dialog_initialization(self) -> None:
        """Test AddMediaDialog initialization."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        self.assertEqual(dialog.title(), "Add New Media")
        self.assertIsNone(dialog.result)
        dialog.destroy()

    def test_add_media_dialog_form_fields_exist(self) -> None:
        """Test that all form fields are created."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        
        # Check that form variables exist
        self.assertIsNotNone(dialog.name_var)
        self.assertIsNotNone(dialog.media_type_var)
        self.assertIsNotNone(dialog.company_var)
        self.assertIsNotNone(dialog.license_var)
        self.assertIsNotNone(dialog.creation_date_var)
        self.assertIsNotNone(dialog.valid_until_var)
        self.assertIsNotNone(dialog.box_var)
        
        dialog.destroy()

    def test_add_media_dialog_cancel(self) -> None:
        """Test cancelling AddMediaDialog."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        dialog._cancel()
        self.assertIsNone(dialog.result)

    def test_add_media_dialog_validation_empty_name(self) -> None:
        """Test validation for empty name."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        dialog.name_var.set("")
        dialog.media_type_var.set("CD")
        
        with patch('tkinter.messagebox.showwarning'):
            dialog._save()
        
        self.assertIsNone(dialog.result)
        dialog.destroy()

    def test_add_media_dialog_validation_empty_type(self) -> None:
        """Test that empty media type defaults to 'Unknown'."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        dialog.name_var.set("Test Media")
        dialog.media_type_var.set("")
        
        dialog.on_save = Mock()
        dialog._save()
        
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result.media_type, "Unknown")
        dialog.destroy()

    def test_add_media_dialog_invalid_date_format(self) -> None:
        """Test validation for invalid date format."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        dialog.name_var.set("Test Media")
        dialog.media_type_var.set("CD")
        dialog.creation_date_var.set("invalid-date")
        
        with patch('tkinter.messagebox.showerror'):
            dialog._save()
        
        self.assertIsNone(dialog.result)
        dialog.destroy()

    def test_add_media_dialog_valid_date_format(self) -> None:
        """Test validation for valid date format."""
        categories = ["Archive", "Backup"]
        dialog = AddMediaDialog(self.root, self.locations, categories)
        dialog.name_var.set("Test Media")
        dialog.media_type_var.set("CD")
        dialog.creation_date_var.set("2024-01-15")
        
        # Mock the on_save callback
        dialog.on_save = Mock()
        dialog._save()
        
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result.name, "Test Media")
        self.assertEqual(dialog.result.media_type, "CD")
        self.assertEqual(dialog.result.creation_date, date(2024, 1, 15))
        dialog.destroy()

    def test_add_media_dialog_with_callback(self) -> None:
        """Test AddMediaDialog with callback."""
        categories = ["Archive", "Backup"]
        callback = Mock()
        dialog = AddMediaDialog(self.root, self.locations, categories, on_save=callback)
        
        dialog.name_var.set("Test Media")
        dialog.media_type_var.set("DVD")
        
        dialog._save()
        
        self.assertIsNotNone(dialog.result)
        # Verify callback was called
        callback.assert_called_once()
        dialog.destroy()


class TestEditMediaDialog(unittest.TestCase):
    """Test EditMediaDialog class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.media = Media(
            id=1,
            name="Test Media",
            media_type="CD",
            company="Test Company",
            license_code="ABC123",
            creation_date=date(2024, 1, 1),
            valid_until_date=date(2025, 1, 1),
            content_description="Test content",
            remarks="Test remarks",
            location_id=1,
        )
        
        self.locations = [
            StorageLocation(id=1, box="Box A", place="Shelf 1"),
            StorageLocation(id=2, box="Box B", place="Shelf 2"),
        ]

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_edit_media_dialog_initialization(self) -> None:
        """Test EditMediaDialog initialization."""
        categories = ["Archive", "Backup"]
        dialog = EditMediaDialog(self.root, self.media, self.locations, categories)
        self.assertIn("Edit Media", dialog.title())
        self.assertIsNone(dialog.result)
        dialog.destroy()

    def test_edit_media_dialog_pre_populated_fields(self) -> None:
        """Test that form fields are pre-populated."""
        categories = ["Archive", "Backup"]
        dialog = EditMediaDialog(self.root, self.media, self.locations, categories)
        
        self.assertEqual(dialog.name_var.get(), "Test Media")
        self.assertEqual(dialog.media_type_var.get(), "CD")
        self.assertEqual(dialog.company_var.get(), "Test Company")
        self.assertEqual(dialog.license_var.get(), "ABC123")
        
        dialog.destroy()

    def test_edit_media_dialog_cancel(self) -> None:
        """Test cancelling EditMediaDialog."""
        categories = ["Archive", "Backup"]
        dialog = EditMediaDialog(self.root, self.media, self.locations, categories)
        dialog._cancel()
        self.assertIsNone(dialog.result)

    def test_edit_media_dialog_save_changes(self) -> None:
        """Test saving changes in EditMediaDialog."""
        categories = ["Archive", "Backup"]
        dialog = EditMediaDialog(self.root, self.media, self.locations, categories)
        
        dialog.name_var.set("Updated Media")
        dialog.media_type_var.set("DVD")
        
        # Mock the on_save callback
        dialog.on_save = Mock()
        dialog._save()
        
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result.name, "Updated Media")
        self.assertEqual(dialog.result.media_type, "DVD")
        dialog.destroy()

    def test_edit_media_dialog_validation_empty_name(self) -> None:
        """Test validation for empty name."""
        categories = ["Archive", "Backup"]
        dialog = EditMediaDialog(self.root, self.media, self.locations, categories)
        dialog.name_var.set("")
        
        with patch('tkinter.messagebox.showwarning'):
            dialog._save()
        
        self.assertIsNone(dialog.result)
        dialog.destroy()


class TestDeleteConfirmDialog(unittest.TestCase):
    """Test DeleteConfirmDialog class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.media = Media(
            id=1,
            name="Test Media",
            media_type="CD",
            company="Test Company",
            license_code="ABC123",
            creation_date=date(2024, 1, 1),
            valid_until_date=date(2025, 1, 1),
            content_description="Test content",
            remarks="Test remarks",
            location_id=1,
        )

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_delete_confirm_dialog_initialization(self) -> None:
        """Test DeleteConfirmDialog initialization."""
        dialog = DeleteConfirmDialog(self.root, self.media)
        self.assertEqual(dialog.title(), "Confirm Delete")
        self.assertIsNone(dialog.result)
        dialog.destroy()

    def test_delete_confirm_dialog_cancel(self) -> None:
        """Test cancelling DeleteConfirmDialog."""
        dialog = DeleteConfirmDialog(self.root, self.media)
        dialog._cancel()
        self.assertIsNone(dialog.result)

    def test_delete_confirm_dialog_confirm(self) -> None:
        """Test confirming deletion."""
        dialog = DeleteConfirmDialog(self.root, self.media)
        
        # Mock the on_confirm callback
        dialog.on_confirm = Mock()
        dialog._confirm()
        
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result.id, self.media.id)
        dialog.destroy()

    def test_delete_confirm_dialog_with_callback(self) -> None:
        """Test DeleteConfirmDialog with callback."""
        callback = Mock()
        dialog = DeleteConfirmDialog(self.root, self.media, on_confirm=callback)
        
        dialog._confirm()
        
        self.assertIsNotNone(dialog.result)
        # Verify callback was called
        callback.assert_called_once()
        dialog.destroy()


class TestDialogIntegration(unittest.TestCase):
    """Integration tests for dialogs."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.locations = [
            StorageLocation(id=1, box="Box A", place="Shelf 1"),
            StorageLocation(id=2, box="Box B", place="Shelf 2"),
        ]

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_add_edit_delete_workflow(self) -> None:
        """Test complete add-edit-delete workflow."""
        categories = ["Archive", "Backup"]
        # Add media
        add_dialog = AddMediaDialog(self.root, self.locations, categories)
        add_dialog.name_var.set("Workflow Test")
        add_dialog.media_type_var.set("CD")
        add_dialog.on_save = Mock()
        
        add_dialog._save()
        
        added_media = add_dialog.result
        self.assertIsNotNone(added_media)
        self.assertEqual(added_media.name, "Workflow Test")
        
        # Edit media
        added_media.id = 1
        edit_dialog = EditMediaDialog(self.root, added_media, self.locations, categories)
        edit_dialog.name_var.set("Updated Workflow Test")
        edit_dialog.on_save = Mock()
        
        edit_dialog._save()
        
        updated_media = edit_dialog.result
        self.assertIsNotNone(updated_media)
        self.assertEqual(updated_media.name, "Updated Workflow Test")
        
        # Delete media
        delete_dialog = DeleteConfirmDialog(self.root, updated_media)
        delete_dialog.on_confirm = Mock()
        
        delete_dialog._confirm()
        
        deleted_media = delete_dialog.result
        self.assertIsNotNone(deleted_media)
        self.assertEqual(deleted_media.id, updated_media.id)


if __name__ == "__main__":
    unittest.main()
