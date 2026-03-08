"""Tests for encoding detection utility.

This module tests the encoding detector for various file encodings,
particularly Windows-1252 (ANSI) files from Microsoft Access.
"""

import unittest
import tempfile
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.encoding_detector import EncodingDetector


class TestEncodingDetector(unittest.TestCase):
    """Tests for encoding detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_utf8_encoding(self):
        """Test detecting UTF-8 encoded file."""
        file_path = Path(self.temp_dir) / "utf8.txt"
        content = "Hello, World! UTF-8 test: café"
        file_path.write_text(content, encoding='utf-8')
        
        detected = EncodingDetector.detect_encoding(file_path)
        self.assertEqual(detected, 'utf-8')

    def test_detect_windows1252_encoding(self):
        """Test detecting Windows-1252 encoded file."""
        file_path = Path(self.temp_dir) / "windows1252.txt"
        content = "Windows-1252 test: äöü"
        file_path.write_text(content, encoding='windows-1252')
        
        detected = EncodingDetector.detect_encoding(file_path)
        self.assertIn(detected, ['windows-1252', 'cp1252', 'iso-8859-1', 'latin-1'])

    def test_detect_iso88591_encoding(self):
        """Test detecting ISO-8859-1 encoded file."""
        file_path = Path(self.temp_dir) / "iso88591.txt"
        content = "ISO-8859-1 test: àáâãäå"
        file_path.write_text(content, encoding='iso-8859-1')
        
        detected = EncodingDetector.detect_encoding(file_path)
        self.assertIn(detected, ['iso-8859-1', 'latin-1', 'windows-1252', 'cp1252'])

    def test_detect_utf8_with_bom(self):
        """Test detecting UTF-8 with BOM."""
        file_path = Path(self.temp_dir) / "utf8_bom.txt"
        content = "UTF-8 with BOM"
        file_path.write_text(content, encoding='utf-8-sig')
        
        detected = EncodingDetector.detect_encoding(file_path)
        self.assertIn(detected, ['utf-8', 'utf-8-sig'])

    def test_detect_nonexistent_file(self):
        """Test detecting encoding of nonexistent file."""
        file_path = Path(self.temp_dir) / "nonexistent.txt"
        
        detected = EncodingDetector.detect_encoding(file_path)
        self.assertEqual(detected, 'utf-8')  # Should default to utf-8

    def test_read_file_with_fallback_utf8(self):
        """Test reading UTF-8 file with fallback."""
        file_path = Path(self.temp_dir) / "utf8_read.txt"
        content = "Hello, World! UTF-8 test: café"
        file_path.write_text(content, encoding='utf-8')
        
        read_content, encoding = EncodingDetector.read_file_with_fallback(file_path)
        self.assertEqual(read_content, content)
        self.assertEqual(encoding, 'utf-8')

    def test_read_file_with_fallback_windows1252(self):
        """Test reading Windows-1252 file with fallback."""
        file_path = Path(self.temp_dir) / "windows1252_read.txt"
        content = "Windows-1252 test: äöü"
        file_path.write_text(content, encoding='windows-1252')
        
        read_content, encoding = EncodingDetector.read_file_with_fallback(file_path)
        self.assertEqual(read_content, content)
        self.assertIn(encoding, ['windows-1252', 'cp1252', 'iso-8859-1', 'latin-1'])

    def test_read_file_with_fallback_mixed_content(self):
        """Test reading file with mixed ASCII and special characters."""
        file_path = Path(self.temp_dir) / "mixed.txt"
        content = "ASCII text with special chars: äöü ñ é"
        file_path.write_text(content, encoding='windows-1252')
        
        read_content, encoding = EncodingDetector.read_file_with_fallback(file_path)
        self.assertEqual(read_content, content)

    def test_read_file_with_fallback_csv_like(self):
        """Test reading CSV-like content with special characters."""
        file_path = Path(self.temp_dir) / "data.csv"
        content = "Name;Description\nCafé;Spécial édition\nNaïve;Tëst"
        file_path.write_text(content, encoding='windows-1252')
        
        read_content, encoding = EncodingDetector.read_file_with_fallback(file_path)
        self.assertEqual(read_content, content)

    def test_encoding_priority_order(self):
        """Test that encoding priority list is correct."""
        priority = EncodingDetector.ENCODING_PRIORITY
        
        # UTF-8 should be first
        self.assertEqual(priority[0], 'utf-8')
        
        # Windows-1252 should be early (common for Access)
        self.assertIn('windows-1252', priority)
        
        # Should have fallback options
        self.assertGreater(len(priority), 3)

    def test_read_access_exported_csv(self):
        """Test reading CSV exported from Microsoft Access (Windows-1252)."""
        file_path = Path(self.temp_dir) / "access_export.csv"
        
        # Simulate Access export with German characters
        content = "ID;Name;Beschreibung\n1;Café;Spécial édition\n2;Naïve;Tëst"
        file_path.write_text(content, encoding='windows-1252')
        
        # Should be able to read without errors
        read_content, encoding = EncodingDetector.read_file_with_fallback(file_path)
        self.assertIn("Café", read_content)
        self.assertIn("Spécial", read_content)
        self.assertIn("Naïve", read_content)

    def test_detect_encoding_with_special_chars(self):
        """Test encoding detection with various special characters."""
        file_path = Path(self.temp_dir) / "special.txt"
        
        # Characters that differ between UTF-8 and Windows-1252
        content = "Test: ä ö ü ß € ™ ®"
        file_path.write_text(content, encoding='windows-1252')
        
        detected = EncodingDetector.detect_encoding(file_path)
        
        # Should detect one of the Windows encodings
        self.assertIn(detected, ['windows-1252', 'cp1252', 'iso-8859-1', 'latin-1'])


if __name__ == '__main__':
    unittest.main()
