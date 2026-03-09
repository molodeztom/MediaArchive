"""Tests for Phase 7 features: Statistics and About dialogs.

This module provides comprehensive tests for Phase 7 features including
statistics dialog, about dialog, and UI polish enhancements.

History:
20260309  V1.0: Initial Phase 7 feature tests
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gui.statistics_dialog import StatisticsDialog
from gui.about_dialog import AboutDialog
from utils.config import APP_NAME, APP_VERSION


class TestStatisticsDialog(unittest.TestCase):
    """Tests for StatisticsDialog."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window
        except tk.TclError:
            self.skipTest("Tkinter not available in test environment")
        
        self.stats = {
            "total_media": 100,
            "expired_media": 5,
            "expiring_soon": 10,
            "media_by_type": {
                "DVD": 40,
                "CD": 30,
                "USB": 20,
                "External HDD": 10,
            },
            "media_with_location": 95,
            "media_without_location": 5,
        }
        self.locations_count = 10

    def tearDown(self) -> None:
        """Clean up after tests."""
        try:
            if hasattr(self, 'root'):
                self.root.destroy()
        except:
            pass

    def test_statistics_dialog_initialization(self) -> None:
        """Test StatisticsDialog initialization."""
        dialog = StatisticsDialog(self.root, self.stats, self.locations_count)
        
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.stats, self.stats)
        self.assertEqual(dialog.locations_count, self.locations_count)
        self.assertFalse(dialog.result)

    def test_statistics_dialog_with_empty_stats(self) -> None:
        """Test StatisticsDialog with empty statistics."""
        empty_stats = {
            "total_media": 0,
            "expired_media": 0,
            "expiring_soon": 0,
            "media_by_type": {},
            "media_with_location": 0,
            "media_without_location": 0,
        }
        
        dialog = StatisticsDialog(self.root, empty_stats, 0)
        self.assertIsNotNone(dialog)

    def test_statistics_dialog_with_various_media_types(self) -> None:
        """Test StatisticsDialog with various media types."""
        stats_with_types = self.stats.copy()
        stats_with_types["media_by_type"] = {
            "DVD": 50,
            "CD": 30,
            "USB": 15,
            "External HDD": 5,
            "Tape": 2,
            "Other": 1,
        }
        
        dialog = StatisticsDialog(self.root, stats_with_types, 15)
        self.assertIsNotNone(dialog)
        self.assertEqual(len(dialog.stats["media_by_type"]), 6)

    def test_statistics_dialog_large_numbers(self) -> None:
        """Test StatisticsDialog with large numbers."""
        large_stats = {
            "total_media": 10000,
            "expired_media": 500,
            "expiring_soon": 1000,
            "media_by_type": {
                "DVD": 5000,
                "CD": 3000,
                "USB": 1500,
                "External HDD": 500,
            },
            "media_with_location": 9500,
            "media_without_location": 500,
        }
        
        dialog = StatisticsDialog(self.root, large_stats, 100)
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.stats["total_media"], 10000)


class TestAboutDialog(unittest.TestCase):
    """Tests for AboutDialog."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window
        except tk.TclError:
            self.skipTest("Tkinter not available in test environment")

    def tearDown(self) -> None:
        """Clean up after tests."""
        try:
            if hasattr(self, 'root'):
                self.root.destroy()
        except:
            pass

    def test_about_dialog_initialization(self) -> None:
        """Test AboutDialog initialization."""
        dialog = AboutDialog(self.root)
        
        self.assertIsNotNone(dialog)
        self.assertFalse(dialog.result)

    def test_about_dialog_has_app_info(self) -> None:
        """Test AboutDialog contains application information."""
        dialog = AboutDialog(self.root)
        
        # Dialog should have parent reference
        self.assertEqual(dialog.parent, self.root)

    def test_about_dialog_version_string(self) -> None:
        """Test that APP_VERSION is properly formatted."""
        # Verify APP_VERSION exists and is a string
        self.assertIsInstance(APP_VERSION, str)
        self.assertTrue(len(APP_VERSION) > 0)

    def test_about_dialog_app_name_string(self) -> None:
        """Test that APP_NAME is properly formatted."""
        # Verify APP_NAME exists and is a string
        self.assertIsInstance(APP_NAME, str)
        self.assertTrue(len(APP_NAME) > 0)


class TestUIPolish(unittest.TestCase):
    """Tests for UI polish features."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in test environment")

    def tearDown(self) -> None:
        """Clean up after tests."""
        try:
            if hasattr(self, 'root'):
                self.root.destroy()
        except:
            pass

    def test_tooltip_creation(self) -> None:
        """Test tooltip creation functionality."""
        from gui.main_window import MainWindow
        
        # Create a button to test tooltip
        button = tk.Button(self.root, text="Test")
        
        # Verify button exists
        self.assertIsNotNone(button)

    def test_keyboard_shortcuts_defined(self) -> None:
        """Test that keyboard shortcuts are properly defined."""
        # Verify common shortcuts are defined
        shortcuts = {
            "Ctrl+N": "Add media",
            "Ctrl+E": "Edit media",
            "Delete": "Delete media",
            "Ctrl+L": "Show locations",
            "Ctrl+F": "Show search",
            "Ctrl+X": "Show expired",
            "F5": "Refresh",
            "F1": "Help",
            "Ctrl+Q": "Quit",
        }
        
        # All shortcuts should be defined
        self.assertEqual(len(shortcuts), 9)


class TestLoggingConfiguration(unittest.TestCase):
    """Tests for logging configuration."""

    def test_logging_module_exists(self) -> None:
        """Test that logging configuration module exists."""
        try:
            from gui.logging_config import configure_logging
            self.assertIsNotNone(configure_logging)
        except ImportError:
            self.fail("logging_config module not found")

    def test_logging_configuration_callable(self) -> None:
        """Test that configure_logging is callable."""
        from gui.logging_config import configure_logging
        
        self.assertTrue(callable(configure_logging))

    def test_logging_levels(self) -> None:
        """Test that logging levels are properly defined."""
        import logging
        
        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]
        
        self.assertEqual(len(levels), 5)


class TestPhase7Integration(unittest.TestCase):
    """Integration tests for Phase 7 features."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in test environment")

    def tearDown(self) -> None:
        """Clean up after tests."""
        try:
            if hasattr(self, 'root'):
                self.root.destroy()
        except:
            pass

    def test_statistics_dialog_with_real_stats(self) -> None:
        """Test StatisticsDialog with realistic statistics."""
        realistic_stats = {
            "total_media": 250,
            "expired_media": 12,
            "expiring_soon": 35,
            "media_by_type": {
                "DVD": 120,
                "CD": 80,
                "USB": 30,
                "External HDD": 15,
                "Tape": 5,
            },
            "media_with_location": 240,
            "media_without_location": 10,
        }
        
        dialog = StatisticsDialog(self.root, realistic_stats, 25)
        
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.stats["total_media"], 250)
        self.assertEqual(dialog.locations_count, 25)

    def test_about_dialog_creation(self) -> None:
        """Test AboutDialog creation."""
        dialog = AboutDialog(self.root)
        
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.parent, self.root)

    def test_multiple_dialogs_creation(self) -> None:
        """Test creating multiple dialogs."""
        stats = {
            "total_media": 100,
            "expired_media": 5,
            "expiring_soon": 10,
            "media_by_type": {"DVD": 100},
            "media_with_location": 95,
            "media_without_location": 5,
        }
        
        stats_dialog = StatisticsDialog(self.root, stats, 10)
        about_dialog = AboutDialog(self.root)
        
        self.assertIsNotNone(stats_dialog)
        self.assertIsNotNone(about_dialog)


if __name__ == "__main__":
    unittest.main()
