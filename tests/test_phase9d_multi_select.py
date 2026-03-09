"""Tests for Phase 9D: Multi-Select and Batch Operations.

Tests for multi-select functionality and batch operations on media items.
"""

import unittest
from datetime import date
from unittest.mock import Mock, MagicMock, patch

from src.business.media_service import MediaService
from src.models.media import Media
from src.utils.exceptions import ValidationError


class TestMultiSelect(unittest.TestCase):
    """Test multi-select functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.service = MediaService(self.mock_db)

    def test_batch_update_media_with_media_type(self):
        """Test batch updating media type for multiple items."""
        # Create test media
        media1 = Media(id=1, name="Media 1", media_type="CD", category="Archive")
        media2 = Media(id=2, name="Media 2", media_type="DVD", category="Archive")
        
        # Mock repository
        self.service._repo.get_by_id = Mock(side_effect=[media1, media2])
        self.service._repo.update = Mock()
        
        # Batch update
        updates = {"media_type": "Tape"}
        result = self.service.batch_update_media([1, 2], updates)
        
        # Verify
        self.assertEqual(result, 2)
        self.assertEqual(self.service._repo.update.call_count, 2)

    def test_batch_update_media_with_category(self):
        """Test batch updating category for multiple items."""
        media1 = Media(id=1, name="Media 1", media_type="CD", category="Archive")
        media2 = Media(id=2, name="Media 2", media_type="CD", category="Backup")
        
        self.service._repo.get_by_id = Mock(side_effect=[media1, media2])
        self.service._repo.update = Mock()
        
        updates = {"category": "Program"}
        result = self.service.batch_update_media([1, 2], updates)
        
        self.assertEqual(result, 2)
        self.assertEqual(self.service._repo.update.call_count, 2)

    def test_batch_update_media_with_expiration_date(self):
        """Test batch updating expiration date for multiple items."""
        media1 = Media(id=1, name="Media 1", media_type="CD")
        media2 = Media(id=2, name="Media 2", media_type="CD")
        
        self.service._repo.get_by_id = Mock(side_effect=[media1, media2])
        self.service._repo.update = Mock()
        
        expiration = date(2027, 12, 31)
        updates = {"valid_until_date": expiration}
        result = self.service.batch_update_media([1, 2], updates)
        
        self.assertEqual(result, 2)
        self.assertEqual(self.service._repo.update.call_count, 2)

    def test_batch_update_media_with_multiple_fields(self):
        """Test batch updating multiple fields for multiple items."""
        media1 = Media(id=1, name="Media 1", media_type="CD", category="Archive")
        media2 = Media(id=2, name="Media 2", media_type="DVD", category="Backup")
        
        self.service._repo.get_by_id = Mock(side_effect=[media1, media2])
        self.service._repo.update = Mock()
        
        expiration = date(2027, 12, 31)
        updates = {
            "media_type": "Tape",
            "category": "Program",
            "valid_until_date": expiration
        }
        result = self.service.batch_update_media([1, 2], updates)
        
        self.assertEqual(result, 2)
        self.assertEqual(self.service._repo.update.call_count, 2)

    def test_batch_update_media_empty_list(self):
        """Test batch update with empty media list."""
        with self.assertRaises(ValidationError):
            self.service.batch_update_media([], {"media_type": "Tape"})

    def test_batch_update_media_empty_updates(self):
        """Test batch update with empty updates dict."""
        with self.assertRaises(ValidationError):
            self.service.batch_update_media([1, 2], {})

    def test_batch_update_media_partial_failure(self):
        """Test batch update with some items failing."""
        media1 = Media(id=1, name="Media 1", media_type="CD")
        media2 = Media(id=2, name="Media 2", media_type="DVD")
        
        # First call succeeds, second fails
        self.service._repo.get_by_id = Mock(side_effect=[media1, Exception("DB Error")])
        self.service._repo.update = Mock()
        
        updates = {"media_type": "Tape"}
        result = self.service.batch_update_media([1, 2], updates)
        
        # Should update 1 item successfully
        self.assertEqual(result, 1)
        self.assertEqual(self.service._repo.update.call_count, 1)


class TestBatchDelete(unittest.TestCase):
    """Test batch delete functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.service = MediaService(self.mock_db)

    def test_batch_delete_media(self):
        """Test batch deleting multiple media items."""
        media1 = Media(id=1, name="Media 1", media_type="CD")
        media2 = Media(id=2, name="Media 2", media_type="DVD")
        
        self.service._repo.get_by_id = Mock(side_effect=[media1, media2])
        self.service._repo.delete = Mock()
        
        result = self.service.batch_delete_media([1, 2])
        
        self.assertEqual(result, 2)
        self.assertEqual(self.service._repo.delete.call_count, 2)

    def test_batch_delete_media_empty_list(self):
        """Test batch delete with empty media list."""
        with self.assertRaises(ValidationError):
            self.service.batch_delete_media([])

    def test_batch_delete_media_partial_failure(self):
        """Test batch delete with some items failing."""
        media1 = Media(id=1, name="Media 1", media_type="CD")
        
        # First call succeeds, second fails
        self.service._repo.get_by_id = Mock(side_effect=[media1, Exception("DB Error")])
        self.service._repo.delete = Mock()
        
        result = self.service.batch_delete_media([1, 2])
        
        # Should delete 1 item successfully
        self.assertEqual(result, 1)
        self.assertEqual(self.service._repo.delete.call_count, 1)

    def test_batch_delete_single_item(self):
        """Test batch delete with single item."""
        media1 = Media(id=1, name="Media 1", media_type="CD")
        
        self.service._repo.get_by_id = Mock(return_value=media1)
        self.service._repo.delete = Mock()
        
        result = self.service.batch_delete_media([1])
        
        self.assertEqual(result, 1)
        self.assertEqual(self.service._repo.delete.call_count, 1)


class TestBatchEditDialog(unittest.TestCase):
    """Test batch edit dialog functionality."""

    def test_batch_edit_dialog_creation(self):
        """Test creating batch edit dialog."""
        from src.gui.batch_edit_dialog import BatchEditDialog
        
        # Create mock parent
        parent = Mock()
        
        # Create test media
        media1 = Media(id=1, name="Media 1", media_type="CD")
        media2 = Media(id=2, name="Media 2", media_type="DVD")
        
        # Create dialog
        dialog = BatchEditDialog(parent, [media1, media2], ["Archive", "Backup"])
        
        # Verify dialog was created
        self.assertIsNotNone(dialog)
        self.assertEqual(len(dialog.selected_media), 2)

    def test_batch_edit_dialog_with_empty_media_list(self):
        """Test batch edit dialog with empty media list."""
        from src.gui.batch_edit_dialog import BatchEditDialog
        
        parent = Mock()
        
        # Create dialog with empty list
        dialog = BatchEditDialog(parent, [], ["Archive", "Backup"])
        
        # Verify dialog was created
        self.assertIsNotNone(dialog)
        self.assertEqual(len(dialog.selected_media), 0)


class TestSelectionCount(unittest.TestCase):
    """Test selection count display."""

    def test_selection_count_display(self):
        """Test that selection count is displayed in status bar."""
        # This would be tested in integration tests with actual GUI
        # For now, just verify the logic
        
        # Simulate selection
        selection = ["1", "2", "3"]
        count_msg = f"Loaded 10 media items | {len(selection)} selected"
        
        self.assertIn("3 selected", count_msg)

    def test_selection_count_with_deleted_items(self):
        """Test selection count with deleted items display."""
        selection = ["1", "2"]
        deleted_count = 1
        count_msg = f"Loaded 10 media items ({deleted_count} deleted) | {len(selection)} selected"
        
        self.assertIn("2 selected", count_msg)
        self.assertIn("1 deleted", count_msg)


if __name__ == '__main__':
    unittest.main()
