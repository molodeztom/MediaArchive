#!/usr/bin/env python
"""Phase 1 Test Suite - Verify all models and configuration work correctly.

Run this script to test all Phase 1 components:
    python -m pytest tests/test_phase1.py
    or
    python tests/test_phase1.py

This script exercises:
- Python environment
- MediaType enum
- StorageLocation model
- Media model
- Configuration system
- Exception hierarchy
- Application entry point
"""

import sys
from datetime import date
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_python_version() -> bool:
    """Test Python version is 3.10 or higher.
    
    Returns:
        True if version is acceptable, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Python Environment")
    print("=" * 70)
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    print(f"Python version: {version_str}")
    
    if version_info.major >= 3 and version_info.minor >= 10:
        print("✓ PASS: Python 3.10+ detected")
        return True
    else:
        print("✗ FAIL: Python 3.10+ required")
        return False


def test_media_type_enum() -> bool:
    """Test MediaType enum functionality.
    
    Returns:
        True if all tests pass, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 2: MediaType Enum")
    print("=" * 70)
    
    try:
        from models.enums import MediaType
        
        # Test get_all_values
        all_types = MediaType.get_all_values()
        print(f"All types: {all_types}")
        expected_count = 8
        if len(all_types) == expected_count:
            print(f"✓ PASS: Found {expected_count} media types")
        else:
            print(f"✗ FAIL: Expected {expected_count} types, got {len(all_types)}")
            return False
        
        # Test is_valid with valid type
        if MediaType.is_valid("DVD"):
            print("✓ PASS: DVD is recognized as valid")
        else:
            print("✗ FAIL: DVD should be valid")
            return False
        
        # Test is_valid with invalid type
        if not MediaType.is_valid("Cassette"):
            print("✓ PASS: Cassette correctly identified as invalid")
        else:
            print("✗ FAIL: Cassette should be invalid")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_storage_location() -> bool:
    """Test StorageLocation model.
    
    Returns:
        True if all tests pass, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 3: StorageLocation Model")
    print("=" * 70)
    
    try:
        from models.location import StorageLocation
        
        # Create instance
        loc = StorageLocation(
            box="CD Register A",
            place="office cabinet",
            detail="slot 4"
        )
        print(f"Created: {loc}")
        print(f"✓ PASS: StorageLocation created successfully")
        
        # Test is_new
        if loc.is_new():
            print("✓ PASS: New location correctly identified (id=None)")
        else:
            print("✗ FAIL: New location should have id=None")
            return False
        
        # Test repr
        repr_str = repr(loc)
        print(f"Repr: {repr_str}")
        if "StorageLocation" in repr_str:
            print("✓ PASS: Repr contains class name")
        else:
            print("✗ FAIL: Repr should contain class name")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_media_model() -> bool:
    """Test Media model.
    
    Returns:
        True if all tests pass, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 4: Media Model")
    print("=" * 70)
    
    try:
        from models.media import Media
        
        # Create instance
        media = Media(name="Windows 11", media_type="DVD")
        print(f"Created: {media}")
        print(f"✓ PASS: Media created successfully")
        
        # Test is_new
        if media.is_new():
            print("✓ PASS: New media correctly identified (id=None)")
        else:
            print("✗ FAIL: New media should have id=None")
            return False
        
        # Test is_expired (should be False for new media without date)
        if not media.is_expired():
            print("✓ PASS: Media without expiration date is not expired")
        else:
            print("✗ FAIL: Media without expiration should not be expired")
            return False
        
        # Test has_location (should be False)
        if not media.has_location():
            print("✓ PASS: Media without location correctly identified")
        else:
            print("✗ FAIL: Media without location_id should return False")
            return False
        
        # Test with location_id
        media_with_loc = Media(
            name="Test",
            media_type="DVD",
            location_id=1
        )
        if media_with_loc.has_location():
            print("✓ PASS: Media with location correctly identified")
        else:
            print("✗ FAIL: Media with location_id should return True")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_configuration() -> bool:
    """Test configuration module.
    
    Returns:
        True if all tests pass, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 5: Configuration")
    print("=" * 70)
    
    try:
        from utils.config import (
            APP_NAME,
            APP_VERSION,
            DB_PATH,
            MAX_NAME_LENGTH,
            BASE_DIR,
        )
        
        print(f"App: {APP_NAME} v{APP_VERSION}")
        print(f"Base dir: {BASE_DIR}")
        print(f"DB path: {DB_PATH}")
        print(f"Max name length: {MAX_NAME_LENGTH}")
        
        if APP_NAME and APP_VERSION:
            print("✓ PASS: App metadata configured")
        else:
            print("✗ FAIL: App metadata missing")
            return False
        
        if DB_PATH and "media_archive.db" in str(DB_PATH):
            print("✓ PASS: Database path configured correctly")
        else:
            print("✗ FAIL: Database path not configured")
            return False
        
        if MAX_NAME_LENGTH > 0:
            print("✓ PASS: Validation limits configured")
        else:
            print("✗ FAIL: Validation limits not configured")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_exceptions() -> bool:
    """Test exception hierarchy.
    
    Returns:
        True if all tests pass, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 6: Exception Hierarchy")
    print("=" * 70)
    
    try:
        from utils.exceptions import (
            MediaArchiveError,
            ValidationError,
            DatabaseError,
            NotFoundError,
        )
        
        # Test ValidationError
        try:
            raise ValidationError("Test validation error")
        except ValidationError as e:
            print(f"✓ PASS: ValidationError caught: {e}")
        
        # Test DatabaseError
        try:
            raise DatabaseError("Test database error")
        except DatabaseError as e:
            print(f"✓ PASS: DatabaseError caught: {e}")
        
        # Test NotFoundError
        try:
            raise NotFoundError("Test not found error")
        except NotFoundError as e:
            print(f"✓ PASS: NotFoundError caught: {e}")
        
        # Test inheritance
        try:
            raise ValidationError("Test")
        except MediaArchiveError:
            print("✓ PASS: ValidationError is subclass of MediaArchiveError")
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_main_entry_point() -> bool:
    """Test main entry point.
    
    Returns:
        True if main.py can be imported, False otherwise.
    """
    print("\n" + "=" * 70)
    print("TEST 7: Main Entry Point")
    print("=" * 70)
    
    try:
        # Check if main.py exists
        main_path = Path(__file__).parent.parent / "main.py"
        if main_path.exists():
            print(f"✓ PASS: main.py exists at {main_path}")
            return True
        else:
            print(f"✗ FAIL: main.py not found at {main_path}")
            return False
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def main() -> None:
    """Run all Phase 1 tests.
    
    Prints test results and summary.
    """
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  PHASE 1: PROJECT SETUP - TEST SUITE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("Python Environment", test_python_version()))
    results.append(("MediaType Enum", test_media_type_enum()))
    results.append(("StorageLocation Model", test_storage_location()))
    results.append(("Media Model", test_media_model()))
    results.append(("Configuration", test_configuration()))
    results.append(("Exception Hierarchy", test_exceptions()))
    results.append(("Main Entry Point", test_main_entry_point()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Phase 1 is complete and verified!")
        print("\nNext: Phase 2 - Database Layer Implementation")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed - Please review errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
