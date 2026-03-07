"""Tests for Phase 4.4: Search and Filter Functionality.

Tests for search and filter functionality in the main window.
"""

import tkinter as tk
import unittest
from pathlib import Path
import sys
from datetime import date

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.database import Database
from business.location_service import LocationService
from business.media_service import MediaService
from models.media import Media
from models.location import StorageLocation


class TestSearchAndFilter(unittest.TestCase):
    """Tests for search and filter functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create in-memory database
        self.db = Database(":memory:")
        self.db.init_schema()
        
        # Initialize services
        self.location_service = LocationService(self.db)
        self.media_service = MediaService(self.db)
        
        # Create test data
        self.loc1 = self.location_service.create_location("Box 1", "Shelf A")
        self.loc2 = self.location_service.create_location("Box 2", "Shelf B")
        
        self.media1 = self.media_service.create_media(
            name="Test Media 1",
            media_type="DVD",
            location_id=self.loc1.id,
            valid_until_date=date(2026, 12, 31)
        )
        
        self.media2 = self.media_service.create_media(
            name="Test Media 2",
            media_type="Blu-ray",
            location_id=self.loc2.id,
            valid_until_date=date(2024, 1, 1)  # Expired
        )
        
        self.media3 = self.media_service.create_media(
            name="Another Media",
            media_type="DVD",
            location_id=self.loc1.id,
            valid_until_date=date(2026, 6, 30)
        )

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.db.close()

    def test_search_by_name(self) -> None:
        """Test searching by name."""
        results = self.media_service.search_media_by_name("Test")
        self.assertEqual(len(results), 2)
        
        results = self.media_service.search_media_by_name("Another")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Another Media")

    def test_filter_by_type(self) -> None:
        """Test filtering by media type."""
        results = self.media_service.get_media_by_type("DVD")
        self.assertEqual(len(results), 2)
        
        results = self.media_service.get_media_by_type("Blu-ray")
        self.assertEqual(len(results), 1)

    def test_filter_by_location(self) -> None:
        """Test filtering by location."""
        results = self.media_service.get_media_by_location(self.loc1.id)
        self.assertEqual(len(results), 2)
        
        results = self.media_service.get_media_by_location(self.loc2.id)
        self.assertEqual(len(results), 1)

    def test_get_expired_media(self) -> None:
        """Test getting expired media."""
        results = self.media_service.get_expired_media()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test Media 2")

    def test_get_expiring_soon(self) -> None:
        """Test getting media expiring soon."""
        results = self.media_service.get_expiring_soon(days=365)
        # Should include media expiring within 365 days from today
        # Since we're in 2026, media expiring in 2026 should be included
        self.assertGreaterEqual(len(results), 2)

    def test_combined_search_and_filter(self) -> None:
        """Test combining search and filter."""
        # Search for "Test" and filter by DVD type
        results = self.media_service.search_media_by_name("Test")
        results = [m for m in results if m.media_type == "DVD"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test Media 1")

    def test_search_with_location_filter(self) -> None:
        """Test search with location filter."""
        # Search for "Media" in location 1
        results = self.media_service.search_media_by_name("Media")
        results = [m for m in results if m.location_id == self.loc1.id]
        self.assertEqual(len(results), 2)  # "Test Media 1" and "Another Media"

    def test_filter_expired_by_type(self) -> None:
        """Test filtering expired media by type."""
        expired = self.media_service.get_expired_media()
        expired_dvd = [m for m in expired if m.media_type == "DVD"]
        self.assertEqual(len(expired_dvd), 0)
        
        expired_bluray = [m for m in expired if m.media_type == "Blu-ray"]
        self.assertEqual(len(expired_bluray), 1)

    def test_search_empty_query(self) -> None:
        """Test search with empty query."""
        with self.assertRaises(Exception):
            self.media_service.search_media_by_name("")

    def test_filter_nonexistent_location(self) -> None:
        """Test filtering by nonexistent location."""
        results = self.media_service.get_media_by_location(999)
        self.assertEqual(len(results), 0)

    def test_media_count_by_location(self) -> None:
        """Test counting media by location."""
        count_loc1 = len(self.media_service.get_media_by_location(self.loc1.id))
        count_loc2 = len(self.media_service.get_media_by_location(self.loc2.id))
        
        self.assertEqual(count_loc1, 2)
        self.assertEqual(count_loc2, 1)


if __name__ == "__main__":
    unittest.main()
