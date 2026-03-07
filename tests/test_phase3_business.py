#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Business logic layer tests for Media Archive Manager.

Tests the service layer with validation and business rules.
"""

import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from business.location_service import LocationService
from business.media_service import MediaService
from data.database import Database
from utils.exceptions import ValidationError, NotFoundError


def test_location_service() -> bool:
    """Test LocationService operations."""
    print("\n" + "=" * 70)
    print("TEST 1: LocationService")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            service = LocationService(db)
            
            # Test create with validation
            loc = service.create_location(
                box="CD Register A",
                place="office cabinet",
                detail="slot 4"
            )
            print(f"[PASS] Created location: {loc.id}")
            
            # Test get
            retrieved = service.get_location(loc.id)
            if retrieved.box == "CD Register A":
                print("[PASS] Retrieved location")
            else:
                print("[FAIL] Location data mismatch")
                return False
            
            # Test update
            updated = service.update_location(loc.id, detail="slot 5")
            if updated.detail == "slot 5":
                print("[PASS] Updated location")
            else:
                print("[FAIL] Update failed")
                return False
            
            # Test search
            results = service.search_locations("CD")
            if len(results) > 0:
                print("[PASS] Search works")
            else:
                print("[FAIL] Search failed")
                return False
            
            # Test validation - empty box
            try:
                service.create_location("", "place")
                print("[FAIL] Should reject empty box")
                return False
            except ValidationError:
                print("[PASS] Validation rejects empty box")
            
            # Test delete
            service.delete_location(loc.id)
            try:
                service.get_location(loc.id)
                print("[FAIL] Delete failed")
                return False
            except NotFoundError:
                print("[PASS] Deleted location")
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_media_service() -> bool:
    """Test MediaService operations."""
    print("\n" + "=" * 70)
    print("TEST 2: MediaService")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            service = MediaService(db)
            
            # Test create with validation
            media = service.create_media(
                name="Windows 11",
                media_type="DVD",
                content_description="Operating System",
                creation_date=date.today()
            )
            print(f"[PASS] Created media: {media.id}")
            
            # Test get
            retrieved = service.get_media(media.id)
            if retrieved.name == "Windows 11":
                print("[PASS] Retrieved media")
            else:
                print("[FAIL] Media data mismatch")
                return False
            
            # Test update
            updated = service.update_media(media.id, remarks="Test remark")
            if updated.remarks == "Test remark":
                print("[PASS] Updated media")
            else:
                print("[FAIL] Update failed")
                return False
            
            # Test search by name
            results = service.search_media_by_name("Windows")
            if len(results) > 0:
                print("[PASS] Search by name works")
            else:
                print("[FAIL] Search by name failed")
                return False
            
            # Test get by type
            results = service.get_media_by_type("DVD")
            if len(results) > 0:
                print("[PASS] Get by type works")
            else:
                print("[FAIL] Get by type failed")
                return False
            
            # Test validation - empty name
            try:
                service.create_media("", "DVD")
                print("[FAIL] Should reject empty name")
                return False
            except ValidationError:
                print("[PASS] Validation rejects empty name")
            
            # Test validation - invalid type
            try:
                service.create_media("Test", "InvalidType")
                print("[FAIL] Should reject invalid type")
                return False
            except ValidationError:
                print("[PASS] Validation rejects invalid type")
            
            # Test delete
            service.delete_media(media.id)
            try:
                service.get_media(media.id)
                print("[FAIL] Delete failed")
                return False
            except NotFoundError:
                print("[PASS] Deleted media")
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_expiration_logic() -> bool:
    """Test media expiration logic."""
    print("\n" + "=" * 70)
    print("TEST 3: Media Expiration Logic")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            service = MediaService(db)
            
            # Create expired media
            expired = service.create_media(
                name="Expired",
                media_type="CD",
                valid_until_date=date.today() - timedelta(days=10)
            )
            
            # Create expiring soon
            expiring = service.create_media(
                name="Expiring Soon",
                media_type="DVD",
                valid_until_date=date.today() + timedelta(days=15)
            )
            
            # Create valid media
            valid = service.create_media(
                name="Valid",
                media_type="DVD",
                valid_until_date=date.today() + timedelta(days=100)
            )
            
            # Test get expired
            expired_list = service.get_expired_media()
            if len(expired_list) >= 1:
                print(f"[PASS] Found {len(expired_list)} expired media")
            else:
                print("[FAIL] Should find expired media")
                return False
            
            # Test get expiring soon
            expiring_list = service.get_expiring_soon(30)
            if len(expiring_list) >= 1:
                print(f"[PASS] Found {len(expiring_list)} expiring soon")
            else:
                print("[FAIL] Should find expiring media")
                return False
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_statistics() -> bool:
    """Test media statistics."""
    print("\n" + "=" * 70)
    print("TEST 4: Media Statistics")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            loc_service = LocationService(db)
            media_service = MediaService(db)
            
            # Create location
            loc = loc_service.create_location("Box A", "Cabinet")
            
            # Create media
            m1 = media_service.create_media("Media 1", "DVD", location_id=loc.id)
            m2 = media_service.create_media("Media 2", "CD")
            m3 = media_service.create_media("Media 3", "DVD")
            
            # Get statistics
            stats = media_service.get_media_statistics()
            
            if stats["total_media"] == 3:
                print(f"[PASS] Total media: {stats['total_media']}")
            else:
                print(f"[FAIL] Expected 3 media, got {stats['total_media']}")
                return False
            
            if stats["media_with_location"] == 1:
                print(f"[PASS] Media with location: {stats['media_with_location']}")
            else:
                print(f"[FAIL] Expected 1 with location, got {stats['media_with_location']}")
                return False
            
            if stats["media_by_type"]["DVD"] == 2:
                print(f"[PASS] DVD count: {stats['media_by_type']['DVD']}")
            else:
                print(f"[FAIL] Expected 2 DVDs, got {stats['media_by_type'].get('DVD', 0)}")
                return False
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_validation() -> bool:
    """Test input validation."""
    print("\n" + "=" * 70)
    print("TEST 5: Input Validation")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            loc_service = LocationService(db)
            media_service = MediaService(db)
            
            # Test location validation
            validation_tests = [
                ("empty_box", lambda: loc_service.create_location("", "place"), True),
                ("empty_place", lambda: loc_service.create_location("box", ""), True),
                ("valid_location", lambda: loc_service.create_location("box", "place"), False),
            ]
            
            for test_name, test_func, should_fail in validation_tests:
                try:
                    test_func()
                    if should_fail:
                        print(f"[FAIL] {test_name} should have failed")
                        return False
                    else:
                        print(f"[PASS] {test_name} passed")
                except ValidationError:
                    if should_fail:
                        print(f"[PASS] {test_name} correctly rejected")
                    else:
                        print(f"[FAIL] {test_name} should have passed")
                        return False
            
            # Test media validation
            media_tests = [
                ("empty_name", lambda: media_service.create_media("", "DVD"), True),
                ("invalid_type", lambda: media_service.create_media("Test", "Invalid"), True),
                ("valid_media", lambda: media_service.create_media("Test", "DVD"), False),
            ]
            
            for test_name, test_func, should_fail in media_tests:
                try:
                    test_func()
                    if should_fail:
                        print(f"[FAIL] {test_name} should have failed")
                        return False
                    else:
                        print(f"[PASS] {test_name} passed")
                except ValidationError:
                    if should_fail:
                        print(f"[PASS] {test_name} correctly rejected")
                    else:
                        print(f"[FAIL] {test_name} should have passed")
                        return False
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def main() -> None:
    """Run all business logic tests."""
    print("\n")
    print("=" * 70)
    print("PHASE 3: BUSINESS LOGIC LAYER - TEST SUITE".center(70))
    print("=" * 70)
    
    results = []
    
    results.append(("LocationService", test_location_service()))
    results.append(("MediaService", test_media_service()))
    results.append(("Expiration Logic", test_expiration_logic()))
    results.append(("Media Statistics", test_statistics()))
    results.append(("Input Validation", test_validation()))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED - Phase 3 is complete and verified!")
        print("\nNext: Phase 4 - GUI Layer Implementation")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {total - passed} test(s) failed - Please review errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
