"""Tests for Phase 5: Search and Filter functionality.

This module tests the search panel, filter menu, and search/filter operations.

History:
20260307  V1.0: Initial Phase 5 search and filter tests
"""

import unittest
from datetime import date, timedelta
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.database import Database
from business.media_service import MediaService
from business.location_service import LocationService
from models.media import Media
from models.location import StorageLocation
from models.enums import MediaType


class TestSearchPanel(unittest.TestCase):
    """Test search panel functionality."""

    def setUp(self) -> None:
        """Set up test database and services."""
        self.db = Database(":memory:")
        self.db.init_schema()
        self.media_service = MediaService(self.db)
        self.location_service = LocationService(self.db)
        
        # Create test locations
        self.loc1 = self.location_service.create_location("Box1", "Shelf1", "Detail1")
        self.loc2 = self.location_service.create_location("Box2", "Shelf2", "Detail2")
        
        # Create test media
        today = date.today()
        self.media1 = self.media_service.create_media(
            name="Test Media 1",
            media_type=MediaType.DVD,
            company="Company A",
            creation_date=today - timedelta(days=30),
            valid_until_date=today + timedelta(days=30),
            location_id=self.loc1.id
        )
        
        self.media2 = self.media_service.create_media(
            name="Test Media 2",
            media_type=MediaType.BLU_RAY,
            company="Company B",
            creation_date=today - timedelta(days=60),
            valid_until_date=today - timedelta(days=5),  # Expired
            location_id=self.loc2.id
        )
        
        self.media3 = self.media_service.create_media(
            name="Another Media",
            media_type=MediaType.CD,
            company="Company C",
            creation_date=today - timedelta(days=90),
            valid_until_date=today + timedelta(days=60),
            location_id=self.loc1.id
        )

    def tearDown(self) -> None:
        """Clean up test database."""
        self.db.close()

    def test_search_by_name(self) -> None:
        """Test searching media by name."""
        results = self.media_service.search_media_by_name("Test Media")
        self.assertEqual(len(results), 2)
        result_ids = [m.id for m in results]
        self.assertIn(self.media1.id, result_ids)
        self.assertIn(self.media2.id, result_ids)

    def test_search_by_name_exact(self) -> None:
        """Test exact name search."""
        results = self.media_service.search_media_by_name("Test Media 1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media1.id)

    def test_search_by_name_case_insensitive(self) -> None:
        """Test case-insensitive search."""
        results = self.media_service.search_media_by_name("test media")
        self.assertEqual(len(results), 2)

    def test_search_by_name_partial(self) -> None:
        """Test partial name search."""
        results = self.media_service.search_media_by_name("Another")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media3.id)

    def test_search_empty_query(self) -> None:
        """Test search with empty query raises error."""
        with self.assertRaises(Exception):
            self.media_service.search_media_by_name("")

    def test_filter_by_type(self) -> None:
        """Test filtering media by type."""
        results = self.media_service.get_media_by_type(MediaType.DVD)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media1.id)

    def test_filter_by_type_multiple(self) -> None:
        """Test filtering returns multiple items of same type."""
        # Create another DVD
        self.media_service.create_media(
            name="Another DVD",
            media_type=MediaType.DVD,
            location_id=self.loc1.id
        )
        
        results = self.media_service.get_media_by_type(MediaType.DVD)
        self.assertEqual(len(results), 2)

    def test_filter_by_type_bluray(self) -> None:
        """Test filtering by Blu-ray type."""
        results = self.media_service.get_media_by_type(MediaType.BLU_RAY)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media2.id)

    def test_filter_by_location(self) -> None:
        """Test filtering media by location."""
        results = self.media_service.get_media_by_location(self.loc1.id)
        self.assertEqual(len(results), 2)
        result_ids = [m.id for m in results]
        self.assertIn(self.media1.id, result_ids)
        self.assertIn(self.media3.id, result_ids)

    def test_filter_by_location_empty(self) -> None:
        """Test filtering by location with no media."""
        # Create empty location
        loc3 = self.location_service.create_location("Box3", "Shelf3")
        results = self.media_service.get_media_by_location(loc3.id)
        self.assertEqual(len(results), 0)

    def test_get_expired_media(self) -> None:
        """Test getting expired media."""
        results = self.media_service.get_expired_media()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media2.id)

    def test_get_expiring_soon(self) -> None:
        """Test getting media expiring soon."""
        results = self.media_service.get_expiring_soon(days=30)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media1.id)

    def test_get_expiring_soon_extended(self) -> None:
        """Test getting media expiring within extended period."""
        results = self.media_service.get_expiring_soon(days=90)
        # Should include media1 (expires in 30 days) and media2 (already expired)
        self.assertGreaterEqual(len(results), 1)
        result_ids = [m.id for m in results]
        self.assertIn(self.media1.id, result_ids)

    def test_combined_search_and_filter(self) -> None:
        """Test combining search and type filter."""
        # Search by name
        results = self.media_service.search_media_by_name("Test Media")
        self.assertEqual(len(results), 2)
        
        # Filter by type
        results = [m for m in results if m.media_type == MediaType.DVD]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media1.id)

    def test_search_with_location_filter(self) -> None:
        """Test search combined with location filter."""
        # Search by name
        results = self.media_service.search_media_by_name("Test Media")
        self.assertEqual(len(results), 2)
        
        # Filter by location
        results = [m for m in results if m.location_id == self.loc1.id]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media1.id)

    def test_filter_expired_by_type(self) -> None:
        """Test filtering expired media by type."""
        expired = self.media_service.get_expired_media()
        self.assertEqual(len(expired), 1)
        
        # Filter by type
        expired_bluray = [m for m in expired if m.media_type == MediaType.BLU_RAY]
        self.assertEqual(len(expired_bluray), 1)

    def test_media_count_by_location(self) -> None:
        """Test counting media by location."""
        count1 = len(self.media_service.get_media_by_location(self.loc1.id))
        count2 = len(self.media_service.get_media_by_location(self.loc2.id))
        
        self.assertEqual(count1, 2)
        self.assertEqual(count2, 1)

    def test_search_by_date_range(self) -> None:
        """Test searching media by date range."""
        today = date.today()
        start = today - timedelta(days=45)
        end = today - timedelta(days=15)
        
        results = self.media_service.get_media_by_date_range(start, end)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.media1.id)

    def test_search_by_date_range_all(self) -> None:
        """Test date range search returning all media."""
        today = date.today()
        start = today - timedelta(days=100)
        end = today
        
        results = self.media_service.get_media_by_date_range(start, end)
        self.assertEqual(len(results), 3)

    def test_search_by_date_range_none(self) -> None:
        """Test date range search returning no results."""
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=10)
        
        results = self.media_service.get_media_by_date_range(start, end)
        self.assertEqual(len(results), 0)

    def test_invalid_date_range(self) -> None:
        """Test invalid date range raises error."""
        today = date.today()
        start = today
        end = today - timedelta(days=1)
        
        with self.assertRaises(Exception):
            self.media_service.get_media_by_date_range(start, end)

    def test_media_statistics(self) -> None:
        """Test media statistics calculation."""
        stats = self.media_service.get_media_statistics()
        
        self.assertEqual(stats["total_media"], 3)
        self.assertEqual(stats["expired_media"], 1)
        self.assertEqual(stats["expiring_soon"], 1)
        self.assertEqual(stats["media_with_location"], 3)
        self.assertEqual(stats["media_without_location"], 0)
        self.assertEqual(stats["media_by_type"][MediaType.DVD], 1)
        self.assertEqual(stats["media_by_type"][MediaType.BLU_RAY], 1)
        self.assertEqual(stats["media_by_type"][MediaType.CD], 1)

    def test_search_no_results(self) -> None:
        """Test search returning no results."""
        results = self.media_service.search_media_by_name("Nonexistent")
        self.assertEqual(len(results), 0)

    def test_filter_nonexistent_type(self) -> None:
        """Test filtering by nonexistent type."""
        results = self.media_service.get_media_by_type(MediaType.OTHER)
        # OTHER type may or may not have media, just check it doesn't error
        self.assertIsInstance(results, list)

    def test_filter_nonexistent_location(self) -> None:
        """Test filtering by nonexistent location."""
        results = self.media_service.get_media_by_location(999)
        self.assertEqual(len(results), 0)

    def test_search_with_special_characters(self) -> None:
        """Test search with special characters."""
        # Create media with special characters
        self.media_service.create_media(
            name="Test & Media (Special)",
            media_type=MediaType.DVD,
            location_id=self.loc1.id
        )
        
        results = self.media_service.search_media_by_name("Special")
        self.assertEqual(len(results), 1)

    def test_multiple_filters_combined(self) -> None:
        """Test combining multiple filters."""
        # Get all media
        results = self.media_service.get_all_media()
        
        # Filter by type
        results = [m for m in results if m.media_type == MediaType.DVD]
        self.assertEqual(len(results), 1)
        
        # Filter by location
        results = [m for m in results if m.location_id == self.loc1.id]
        self.assertEqual(len(results), 1)
        
        # Check not expired
        results = [m for m in results if not m.valid_until_date or m.valid_until_date >= date.today()]
        self.assertEqual(len(results), 1)

    def test_search_performance_large_dataset(self) -> None:
        """Test search performance with larger dataset."""
        # Create many media items
        for i in range(50):
            self.media_service.create_media(
                name=f"Media {i}",
                media_type=MediaType.DVD if i % 2 == 0 else MediaType.BLU_RAY,
                location_id=self.loc1.id if i % 3 == 0 else self.loc2.id
            )
        
        # Search should still be fast
        results = self.media_service.search_media_by_name("Media 25")
        self.assertEqual(len(results), 1)
        
        # Filter should work
        results = self.media_service.get_media_by_type(MediaType.DVD)
        self.assertGreater(len(results), 0)


class TestFilterMenu(unittest.TestCase):
    """Test filter menu functionality."""

    def setUp(self) -> None:
        """Set up test database and services."""
        self.db = Database(":memory:")
        self.db.init_schema()
        self.media_service = MediaService(self.db)
        self.location_service = LocationService(self.db)
        
        # Create test data
        self.loc1 = self.location_service.create_location("Box1", "Shelf1")
        self.media1 = self.media_service.create_media(
            name="DVD Media",
            media_type=MediaType.DVD,
            location_id=self.loc1.id
        )

    def tearDown(self) -> None:
        """Clean up test database."""
        self.db.close()

    def test_filter_menu_types_available(self) -> None:
        """Test all media types are available for filtering."""
        types = MediaType.get_all_values()
        self.assertGreater(len(types), 0)
        self.assertIn(MediaType.DVD, types)

    def test_filter_menu_locations_available(self) -> None:
        """Test locations are available for filtering."""
        locations = self.location_service.get_all_locations()
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0].id, self.loc1.id)

    def test_filter_menu_clear_filters(self) -> None:
        """Test clearing all filters."""
        # Apply filter
        results = self.media_service.get_media_by_type(MediaType.DVD)
        self.assertEqual(len(results), 1)
        
        # Clear filter (get all)
        results = self.media_service.get_all_media()
        self.assertEqual(len(results), 1)


class TestExpiredMediaView(unittest.TestCase):
    """Test expired media view functionality."""

    def setUp(self) -> None:
        """Set up test database and services."""
        self.db = Database(":memory:")
        self.db.init_schema()
        self.media_service = MediaService(self.db)
        self.location_service = LocationService(self.db)
        
        today = date.today()
        
        # Create expired media
        self.expired = self.media_service.create_media(
            name="Expired Media",
            media_type=MediaType.DVD,
            valid_until_date=today - timedelta(days=1)
        )
        
        # Create valid media
        self.valid = self.media_service.create_media(
            name="Valid Media",
            media_type=MediaType.BLU_RAY,
            valid_until_date=today + timedelta(days=30)
        )

    def tearDown(self) -> None:
        """Clean up test database."""
        self.db.close()

    def test_show_expired_media(self) -> None:
        """Test showing only expired media."""
        expired = self.media_service.get_expired_media()
        self.assertEqual(len(expired), 1)
        self.assertEqual(expired[0].id, self.expired.id)

    def test_show_all_media(self) -> None:
        """Test showing all media."""
        all_media = self.media_service.get_all_media()
        self.assertEqual(len(all_media), 2)

    def test_expired_media_count(self) -> None:
        """Test counting expired media."""
        stats = self.media_service.get_media_statistics()
        self.assertEqual(stats["expired_media"], 1)

    def test_expired_media_highlighting(self) -> None:
        """Test identifying expired media for highlighting."""
        all_media = self.media_service.get_all_media()
        
        expired_count = 0
        for media in all_media:
            if media.valid_until_date and media.valid_until_date < date.today():
                expired_count += 1
        
        self.assertEqual(expired_count, 1)


if __name__ == "__main__":
    unittest.main()
