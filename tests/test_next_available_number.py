"""Tests for next available number feature.

This module tests the get_next_number() method to ensure it finds
the first unused number in the sequence, not necessarily the highest.

History:
20260309  V1.0: Created test suite for next available number feature
"""

import unittest
from datetime import date
from pathlib import Path
import sys
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.database import Database
from business.media_service import MediaService


class TestNextAvailableNumber(unittest.TestCase):
    """Test next available number functionality."""
    
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
    
    def test_empty_database_returns_1(self):
        """Test that empty database returns 1."""
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "1")
    
    def test_sequential_numbers_returns_next(self):
        """Test sequential numbers 1,2,3 returns 4."""
        # Create media with numbers 1, 2, 3
        self.service.create_media(name="Media 1", media_type="CD", number="1")
        self.service.create_media(name="Media 2", media_type="CD", number="2")
        self.service.create_media(name="Media 3", media_type="CD", number="3")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "4")
    
    def test_gap_in_sequence_returns_first_gap(self):
        """Test that gap in sequence returns first unused number.
        
        If numbers 1, 2, 4, 5 exist, should return 3.
        """
        # Create media with numbers 1, 2, 4, 5
        self.service.create_media(name="Media 1", media_type="CD", number="1")
        self.service.create_media(name="Media 2", media_type="CD", number="2")
        self.service.create_media(name="Media 4", media_type="CD", number="4")
        self.service.create_media(name="Media 5", media_type="CD", number="5")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "3")
    
    def test_multiple_gaps_returns_first_gap(self):
        """Test that multiple gaps returns first unused number.
        
        If numbers 1, 3, 5, 7 exist, should return 2.
        """
        # Create media with numbers 1, 3, 5, 7
        self.service.create_media(name="Media 1", media_type="CD", number="1")
        self.service.create_media(name="Media 3", media_type="CD", number="3")
        self.service.create_media(name="Media 5", media_type="CD", number="5")
        self.service.create_media(name="Media 7", media_type="CD", number="7")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "2")
    
    def test_large_gap_at_start_returns_1(self):
        """Test that large gap at start returns 1.
        
        If numbers 5, 10, 15 exist, should return 1.
        """
        # Create media with numbers 5, 10, 15
        self.service.create_media(name="Media 5", media_type="CD", number="5")
        self.service.create_media(name="Media 10", media_type="CD", number="10")
        self.service.create_media(name="Media 15", media_type="CD", number="15")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "1")
    
    def test_non_numeric_numbers_ignored(self):
        """Test that non-numeric numbers are ignored.
        
        If numbers ABC, XYZ, 1, 2 exist, should return 3.
        """
        # Create media with mixed numeric and non-numeric numbers
        self.service.create_media(name="Media ABC", media_type="CD", number="ABC")
        self.service.create_media(name="Media XYZ", media_type="CD", number="XYZ")
        self.service.create_media(name="Media 1", media_type="CD", number="1")
        self.service.create_media(name="Media 2", media_type="CD", number="2")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "3")
    
    def test_only_non_numeric_returns_1(self):
        """Test that only non-numeric numbers returns 1."""
        # Create media with only non-numeric numbers
        self.service.create_media(name="Media ABC", media_type="CD", number="ABC")
        self.service.create_media(name="Media XYZ", media_type="CD", number="XYZ")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "1")
    
    def test_no_number_field_ignored(self):
        """Test that media without number field are ignored."""
        # Create media without number
        self.service.create_media(name="Media No Number", media_type="CD")
        self.service.create_media(name="Media 1", media_type="CD", number="1")
        self.service.create_media(name="Media 2", media_type="CD", number="2")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "3")
    
    def test_single_number_returns_next(self):
        """Test that single number returns next."""
        # Create media with only number 1
        self.service.create_media(name="Media 1", media_type="CD", number="1")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "2")
    
    def test_single_number_not_1_returns_1(self):
        """Test that single number not 1 returns 1."""
        # Create media with only number 5
        self.service.create_media(name="Media 5", media_type="CD", number="5")
        
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "1")
    
    def test_large_numbers_with_gap(self):
        """Test large numbers with gap.
        
        If numbers 100, 101, 103, 104 exist, should return 1 (first unused).
        """
        # Create media with numbers 100, 101, 103, 104
        self.service.create_media(name="Media 100", media_type="CD", number="100")
        self.service.create_media(name="Media 101", media_type="CD", number="101")
        self.service.create_media(name="Media 103", media_type="CD", number="103")
        self.service.create_media(name="Media 104", media_type="CD", number="104")
        
        next_num = self.service.get_next_number()
        # Should return 1 since 1 is the first unused number
        self.assertEqual(next_num, "1")
    
    def test_soft_deleted_media_included(self):
        """Test that soft-deleted media are included in calculation.
        
        This ensures we don't reuse numbers of deleted items.
        """
        # Create media with numbers 1, 2, 3
        media1 = self.service.create_media(name="Media 1", media_type="CD", number="1")
        media2 = self.service.create_media(name="Media 2", media_type="CD", number="2")
        media3 = self.service.create_media(name="Media 3", media_type="CD", number="3")
        
        # Soft delete media 2
        self.service.delete_media_soft(media2.id)
        
        # Next number should still be 4 (not 2, even though 2 is deleted)
        next_num = self.service.get_next_number()
        self.assertEqual(next_num, "4")


if __name__ == "__main__":
    unittest.main()
