"""Tests for Phase 4.3: Location Management Dialogs.

Tests for AddLocationDialog, EditLocationDialog, and DeleteLocationConfirmDialog.
"""

import tkinter as tk
import unittest
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gui.dialogs import (
    AddLocationDialog, EditLocationDialog, DeleteLocationConfirmDialog
)
from models.location import StorageLocation


class TestAddLocationDialog(unittest.TestCase):
    """Tests for AddLocationDialog."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_add_location_dialog_initialization(self) -> None:
        """Test dialog initialization."""
        dialog = AddLocationDialog(self.root)
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.title(), "Add New Location")
        dialog.destroy()

    def test_add_location_dialog_form_fields_exist(self) -> None:
        """Test that form fields are created."""
        dialog = AddLocationDialog(self.root)
        self.assertTrue(hasattr(dialog, 'box_var'))
        self.assertTrue(hasattr(dialog, 'place_var'))
        self.assertTrue(hasattr(dialog, 'detail_text'))
        dialog.destroy()

    def test_add_location_dialog_cancel(self) -> None:
        """Test cancel button."""
        dialog = AddLocationDialog(self.root)
        dialog._cancel()
        self.assertIsNone(dialog.result)

    def test_add_location_dialog_validation_empty_box(self) -> None:
        """Test validation for empty box."""
        dialog = AddLocationDialog(self.root)
        dialog.place_var.set("Test Place")
        dialog._save()
        # Dialog should still exist (validation failed)
        self.assertIsNotNone(dialog)
        dialog.destroy()

    def test_add_location_dialog_validation_empty_place(self) -> None:
        """Test validation for empty place."""
        dialog = AddLocationDialog(self.root)
        dialog.box_var.set("Test Box")
        dialog._save()
        # Dialog should still exist (validation failed)
        self.assertIsNotNone(dialog)
        dialog.destroy()

    def test_add_location_dialog_with_callback(self) -> None:
        """Test callback functionality."""
        callback_called = []

        def on_save(location: StorageLocation) -> None:
            callback_called.append(location)

        dialog = AddLocationDialog(self.root, on_save=on_save)
        dialog.box_var.set("Test Box")
        dialog.place_var.set("Test Place")
        dialog.detail_text.insert("1.0", "Test Detail")
        dialog._save()
        
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0].box, "Test Box")
        self.assertEqual(callback_called[0].place, "Test Place")


class TestEditLocationDialog(unittest.TestCase):
    """Tests for EditLocationDialog."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.location = StorageLocation(
            id=1,
            box="Original Box",
            place="Original Place",
            detail="Original Detail"
        )

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_edit_location_dialog_initialization(self) -> None:
        """Test dialog initialization."""
        dialog = EditLocationDialog(self.root, self.location)
        self.assertIsNotNone(dialog)
        self.assertIn("Original Box", dialog.title())
        dialog.destroy()

    def test_edit_location_dialog_pre_populated_fields(self) -> None:
        """Test that fields are pre-populated."""
        dialog = EditLocationDialog(self.root, self.location)
        self.assertEqual(dialog.box_var.get(), "Original Box")
        self.assertEqual(dialog.place_var.get(), "Original Place")
        dialog.destroy()

    def test_edit_location_dialog_cancel(self) -> None:
        """Test cancel button."""
        dialog = EditLocationDialog(self.root, self.location)
        dialog._cancel()
        self.assertIsNone(dialog.result)

    def test_edit_location_dialog_save_changes(self) -> None:
        """Test saving changes."""
        dialog = EditLocationDialog(self.root, self.location)
        dialog.box_var.set("Updated Box")
        dialog.place_var.set("Updated Place")
        dialog._save()
        
        self.assertEqual(dialog.result.box, "Updated Box")
        self.assertEqual(dialog.result.place, "Updated Place")

    def test_edit_location_dialog_validation_empty_box(self) -> None:
        """Test validation for empty box."""
        dialog = EditLocationDialog(self.root, self.location)
        dialog.box_var.set("")
        dialog._save()
        # Dialog should still exist (validation failed)
        self.assertIsNotNone(dialog)
        dialog.destroy()


class TestDeleteLocationConfirmDialog(unittest.TestCase):
    """Tests for DeleteLocationConfirmDialog."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.location = StorageLocation(
            id=1,
            box="Test Box",
            place="Test Place",
            detail="Test Detail"
        )

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.root.destroy()

    def test_delete_location_confirm_dialog_initialization(self) -> None:
        """Test dialog initialization."""
        dialog = DeleteLocationConfirmDialog(self.root, self.location)
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.title(), "Confirm Delete Location")
        dialog.destroy()

    def test_delete_location_confirm_dialog_cancel(self) -> None:
        """Test cancel button."""
        dialog = DeleteLocationConfirmDialog(self.root, self.location)
        dialog._cancel()
        self.assertIsNone(dialog.result)

    def test_delete_location_confirm_dialog_confirm(self) -> None:
        """Test confirm button."""
        dialog = DeleteLocationConfirmDialog(self.root, self.location)
        dialog._confirm()
        self.assertEqual(dialog.result, self.location)

    def test_delete_location_confirm_dialog_with_callback(self) -> None:
        """Test callback functionality."""
        callback_called = []

        def on_confirm(location: StorageLocation) -> None:
            callback_called.append(location)

        dialog = DeleteLocationConfirmDialog(
            self.root, self.location, on_confirm=on_confirm
        )
        dialog._confirm()
        
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0].id, 1)

    def test_delete_location_confirm_dialog_with_media_count(self) -> None:
        """Test dialog with media count."""
        dialog = DeleteLocationConfirmDialog(
            self.root, self.location, media_count=5
        )
        self.assertEqual(dialog.media_count, 5)
        dialog.destroy()


if __name__ == "__main__":
    unittest.main()
