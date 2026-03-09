"""Tests for Phase 9B: Soft Delete functionality.

This module tests the soft delete feature including:
- Soft delete operations
- Restore operations
- Permanent delete operations
- Filtering deleted items
- Statistics with deleted items
- Search with deleted items

History:
20260309  V1.0: Initial soft delete tests
"""

import pytest
from datetime import date
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
    
    def test_search_includes_deleted_when_requested(self, service):
        """Test that search includes deleted items when requested."""
        # Create media
        media1 = service.create_media(name="Test Media 1", media_type="CD-ROM")
        media2 = service.create_media(name="Test Media 2", media_type="CD-ROM")
        
        # Delete one
        service.delete_media(media1.id)
        
        # Search with include_deleted
        results = service.search_media_by_name("Test", include_deleted=True)
        
        # Should find both
        assert len(results) == 2
    
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
    
    def test_soft_delete_alias(self, service):
        """Test that delete_media_soft is an alias for delete_media."""
        # Create media
        media = service.create_media(name="Test Media", media_type="CD-ROM")
        
        # Use soft delete alias
        service.delete_media_soft(media.id)
        
        # Verify marked as deleted
        deleted_media = service.get_media(media.id)
        assert deleted_media.is_deleted is True
    
    def test_deleted_media_with_dates(self, service):
        """Test soft delete with media that has dates."""
        # Create media with dates
        media = service.create_media(
            name="Test Media",
            media_type="CD-ROM",
            creation_date=date(2026, 1, 1),
            valid_until_date=date(2027, 1, 1)
        )
        
        # Soft delete
        service.delete_media(media.id)
        
        # Verify dates are preserved
        deleted_media = service.get_media(media.id)
        assert deleted_media.is_deleted is True
        assert deleted_media.creation_date == date(2026, 1, 1)
        assert deleted_media.valid_until_date == date(2027, 1, 1)
    
    def test_deleted_media_with_location(self, service):
        """Test soft delete with media that has location."""
        # Create media with location_id
        media = service.create_media(
            name="Test Media",
            media_type="CD-ROM",
            location_id=1
        )
        
        # Soft delete
        service.delete_media(media.id)
        
        # Verify location is preserved
        deleted_media = service.get_media(media.id)
        assert deleted_media.is_deleted is True
        assert deleted_media.location_id == 1
    
    def test_permanent_delete_removes_completely(self, service):
        """Test that permanent delete removes all traces."""
        # Create media
        media = service.create_media(
            name="Test Media",
            media_type="CD-ROM",
            number="42",
            category="Archive"
        )
        media_id = media.id
        
        # Soft delete first
        service.delete_media(media_id)
        
        # Verify it's deleted
        deleted_media = service.get_media(media_id)
        assert deleted_media.is_deleted is True
        
        # Permanently delete
        service.delete_media_permanent(media_id)
        
        # Verify completely gone
        with pytest.raises(Exception):
            service.get_media(media_id)
        
        # Should not appear in any list
        all_media = service.get_all_media(include_deleted=True)
        assert len(all_media) == 0
        
        deleted_media = service.get_deleted_media()
        assert len(deleted_media) == 0
