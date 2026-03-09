"""Tests for Phase 9B: Soft Delete functionality.

This module tests the soft delete feature including:
- Soft delete operations
- Restore operations
- Permanent delete operations
- Filtering deleted items
- Statistics with deleted items
- Search with deleted items

History:
20260309  V1.0: Initial soft delete test suite
"""

import pytest
from datetime import date
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.database import Database
from business.media_service import MediaService
from models.media import Media


class TestSoftDelete:
    """Test soft delete functionality."""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create test database."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path))
        db.init_schema()
        yield db
        db.close()
    
    @pytest.fixture
    def service(self, db):
        """Create media service."""
        return MediaService(db)
    
    def test_soft_delete_marks_as_deleted(self, service):
        """Test that soft delete marks item as deleted."""
        # Create media
        media = service.create_media(
            name="Test Media",
            media_type="CD-ROM"
        )
        
        # Soft delete
        service.delete_media(media.id)
        
        # Verify marked as deleted
        deleted_media = service.get_media(media.id)
        assert deleted_media.is_deleted is True
    
    def test_deleted_items_hidden_by_default(self, service):
        """Test that deleted items are hidden by default."""
        # Create and delete media
        media1 = service.create_media(name="Media 1", media_type="CD-ROM")
        media2 = service.create_media(name="Media 2", media_type="DVD")
        service.delete_media(media1.id)
        
        # Get all media (should exclude deleted)
        all_media = service.get_all_media()
        assert len(all_media) == 1
        assert all_media[0].id == media2.id
    
    def test_include_deleted_shows_all(self, service):
        """Test that include_deleted parameter shows all items."""
        # Create and delete media
        media1 = service.create_media(name="Media 1", media_type="CD-ROM")
        media2 = service.create_media(name="Media 2", media_type="DVD")
        service.delete_media(media1.id)
        
        # Get all media including deleted
        all_media = service.get_all_media(include_deleted=True)
        assert len(all_media) == 2
    
    def test_restore_media(self, service):
        """Test restoring deleted media."""
        # Create and delete media
        media = service.create_media(name="Test Media", media_type="CD-ROM")
        service.delete_media(media.id)
        
        # Restore
        service.restore_media(media.id)
        
        # Verify restored
        restored_media = service.get_media(media.id)
        assert restored_media.is_deleted is False
        
        # Should appear in default list
        all_media = service.get_all_media()
        assert len(all_media) == 1
    
    def test_permanent_delete(self, service):
        """Test permanent deletion."""
        # Create and delete media
        media = service.create_media(name="Test Media", media_type="CD-ROM")
        service.delete_media(media.id)
        
        # Permanently delete
        service.delete_media_permanent(media.id)
        
        # Verify completely removed
        with pytest.raises(Exception):
            service.get_media(media.id)
        
        # Should not appear even with include_deleted
        all_media = service.get_all_media(include_deleted=True)
        assert len(all_media) == 0
    
    def test_statistics_exclude_deleted(self, service):
        """Test that statistics exclude deleted items."""
        # Create media
        media1 = service.create_media(name="Media 1", media_type="CD-ROM")
        media2 = service.create_media(name="Media 2", media_type="CD-ROM")
        media3 = service.create_media(name="Media 3", media_type="DVD")
        
        # Delete one
        service.delete_media(media1.id)
        
        # Get statistics
        stats = service.get_media_statistics()
        
        # Should only count active media
        assert stats["total_media"] == 2
        assert stats["deleted_media"] == 1
        assert stats["media_by_type"]["CD-ROM"] == 1
        assert stats["media_by_type"]["DVD"] == 1
    
    def test_search_excludes_deleted(self, service):
        """Test that search excludes deleted items by default."""
        # Create media
        media1 = service.create_media(name="Test Media 1", media_type="CD-ROM")
        media2 = service.create_media(name="Test Media 2", media_type="CD-ROM")
        
        # Delete one
        service.delete_media(media1.id)
        
        # Search
        results = service.search_media_by_name("Test")
        
        # Should only find active media
        assert len(results) == 1
        assert results[0].id == media2.id
    
    def test_multiple_delete_restore_cycles(self, service):
        """Test multiple delete/restore cycles."""
        # Create media
        media = service.create_media(name="Test Media", media_type="CD-ROM")
        
        # Delete and restore multiple times
        for _ in range(3):
            service.delete_media(media.id)
            assert service.get_media(media.id).is_deleted is True
            
            service.restore_media(media.id)
            assert service.get_media(media.id).is_deleted is False
    
    def test_delete_already_deleted(self, service):
        """Test deleting already deleted item."""
        # Create and delete media
        media = service.create_media(name="Test Media", media_type="CD-ROM")
        service.delete_media(media.id)
        
        # Delete again (should not raise error)
        service.delete_media(media.id)
        
        # Should still be deleted
        assert service.get_media(media.id).is_deleted is True
    
    def test_restore_non_deleted(self, service):
        """Test restoring non-deleted item."""
        # Create media (not deleted)
        media = service.create_media(name="Test Media", media_type="CD-ROM")
        
        # Restore (should not raise error)
        service.restore_media(media.id)
        
        # Should still be active
        assert service.get_media(media.id).is_deleted is False
    
    def test_get_deleted_media(self, service):
        """Test getting only deleted media."""
        # Create media
        media1 = service.create_media(name="Media 1", media_type="CD-ROM")
        media2 = service.create_media(name="Media 2", media_type="DVD")
        media3 = service.create_media(name="Media 3", media_type="CD-ROM")
        
        # Delete some
        service.delete_media(media1.id)
        service.delete_media(media3.id)
        
        # Get deleted media
        deleted = service.get_deleted_media()
        
        # Should only get deleted items
        assert len(deleted) == 2
        deleted_ids = {m.id for m in deleted}
        assert media1.id in deleted_ids
        assert media3.id in deleted_ids
        assert media2.id not in deleted_ids
    
    def test_expired_media_excludes_deleted(self, service):
        """Test that expired media query excludes deleted items."""
        # Create expired media
        past_date = date(2020, 1, 1)
        media1 = service.create_media(
            name="Expired 1",
            media_type="CD-ROM",
            valid_until_date=past_date
        )
        media2 = service.create_media(
            name="Expired 2",
            media_type="DVD",
            valid_until_date=past_date
        )
        
        # Delete one
        service.delete_media(media1.id)
        
        # Get expired media
        expired = service.get_expired_media()
        
        # Should only get active expired media
        assert len(expired) == 1
        assert expired[0].id == media2.id
    
    def test_expiring_soon_excludes_deleted(self, service):
        """Test that expiring soon query excludes deleted items."""
        # Create media expiring soon
        future_date = date.today().replace(day=1)  # First day of current month
        media1 = service.create_media(
            name="Expiring 1",
            media_type="CD-ROM",
            valid_until_date=future_date
        )
        media2 = service.create_media(
            name="Expiring 2",
            media_type="DVD",
            valid_until_date=future_date
        )
        
        # Delete one
        service.delete_media(media1.id)
        
        # Get expiring soon
        expiring = service.get_expiring_soon(30)
        
        # Should only get active expiring media
        assert len(expiring) == 1
        assert expiring[0].id == media2.id
