#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database layer tests for Media Archive Manager.

Tests the database connection, schema initialization, and repositories.
"""

import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.database import Database
from data.location_repository import LocationRepository
from data.media_repository import MediaRepository
from models.location import StorageLocation
from models.media import Media
from utils.exceptions import DatabaseError, NotFoundError


def test_database_connection() -> bool:
    """Test database connection and initialization."""
    print("\n" + "=" * 70)
    print("TEST 1: Database Connection and Schema")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            
            conn = db.connect()
            print("[PASS] Database connection established")
            
            db.init_schema()
            print("[PASS] Database schema initialized")
            
            cursor = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            if "storage_location" in tables and "media" in tables:
                print("[PASS] All required tables created")
            else:
                print(f"[FAIL] Missing tables. Found: {tables}")
                return False
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_location_repository() -> bool:
    """Test LocationRepository CRUD operations."""
    print("\n" + "=" * 70)
    print("TEST 2: LocationRepository CRUD")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            repo = LocationRepository(db)
            
            loc = StorageLocation(
                box="CD Register A",
                place="office cabinet",
                detail="slot 4"
            )
            created = repo.create(loc)
            
            if created.id is not None:
                print(f"[PASS] Created location with id={created.id}")
            else:
                print("[FAIL] Location id not set")
                return False
            
            retrieved = repo.get_by_id(created.id)
            if retrieved.box == "CD Register A":
                print("[PASS] Retrieved location by id")
            else:
                print("[FAIL] Retrieved location data mismatch")
                return False
            
            retrieved.detail = "slot 5"
            updated = repo.update(retrieved)
            
            verified = repo.get_by_id(updated.id)
            if verified.detail == "slot 5":
                print("[PASS] Updated location")
            else:
                print("[FAIL] Update not persisted")
                return False
            
            results = repo.search_by_box("CD")
            if len(results) > 0:
                print("[PASS] Search by box works")
            else:
                print("[FAIL] Search by box failed")
                return False
            
            repo.delete(created.id)
            try:
                repo.get_by_id(created.id)
                print("[FAIL] Delete did not remove location")
                return False
            except NotFoundError:
                print("[PASS] Deleted location")
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_media_repository() -> bool:
    """Test MediaRepository CRUD operations."""
    print("\n" + "=" * 70)
    print("TEST 3: MediaRepository CRUD")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            media_repo = MediaRepository(db)
            
            media = Media(
                name="Windows 11",
                media_type="DVD",
                content_description="Operating System",
                creation_date=date.today(),
            )
            created = media_repo.create(media)
            
            if created.id is not None:
                print(f"[PASS] Created media with id={created.id}")
            else:
                print("[FAIL] Media id not set")
                return False
            
            retrieved = media_repo.get_by_id(created.id)
            if retrieved.name == "Windows 11":
                print("[PASS] Retrieved media by id")
            else:
                print("[FAIL] Retrieved media data mismatch")
                return False
            
            retrieved.remarks = "Test remark"
            updated = media_repo.update(retrieved)
            
            verified = media_repo.get_by_id(updated.id)
            if verified.remarks == "Test remark":
                print("[PASS] Updated media")
            else:
                print("[FAIL] Update not persisted")
                return False
            
            results = media_repo.search_by_name("Windows")
            if len(results) > 0:
                print("[PASS] Search by name works")
            else:
                print("[FAIL] Search by name failed")
                return False
            
            results = media_repo.search_by_type("DVD")
            if len(results) > 0:
                print("[PASS] Search by type works")
            else:
                print("[FAIL] Search by type failed")
                return False
            
            media_repo.delete(created.id)
            try:
                media_repo.get_by_id(created.id)
                print("[FAIL] Delete did not remove media")
                return False
            except NotFoundError:
                print("[PASS] Deleted media")
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_expiration_queries() -> bool:
    """Test media expiration queries."""
    print("\n" + "=" * 70)
    print("TEST 4: Media Expiration Queries")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            media_repo = MediaRepository(db)
            
            expired = Media(
                name="Expired Media",
                media_type="CD",
                valid_until_date=date.today() - timedelta(days=10),
            )
            media_repo.create(expired)
            
            expiring = Media(
                name="Expiring Soon",
                media_type="DVD",
                valid_until_date=date.today() + timedelta(days=15),
            )
            media_repo.create(expiring)
            
            valid = Media(
                name="Valid Media",
                media_type="DVD",
                valid_until_date=date.today() + timedelta(days=100),
            )
            media_repo.create(valid)
            
            expired_list = media_repo.get_expired_media()
            if len(expired_list) >= 1:
                print(f"[PASS] Found {len(expired_list)} expired media")
            else:
                print("[FAIL] Should find expired media")
                return False
            
            expiring_list = media_repo.get_expiring_soon(30)
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


def test_relationships() -> bool:
    """Test media-location relationships."""
    print("\n" + "=" * 70)
    print("TEST 5: Media-Location Relationships")
    print("=" * 70)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)
            db.init_schema()
            
            loc_repo = LocationRepository(db)
            media_repo = MediaRepository(db)
            
            loc = StorageLocation(
                box="CD Register A",
                place="office cabinet",
                detail="slot 4"
            )
            created_loc = loc_repo.create(loc)
            
            media = Media(
                name="Test Media",
                media_type="DVD",
                location_id=created_loc.id,
            )
            created_media = media_repo.create(media)
            
            if created_media.location_id == created_loc.id:
                print("[PASS] Media linked to location")
            else:
                print("[FAIL] Location link not set")
                return False
            
            results = media_repo.search_by_location(created_loc.id)
            if len(results) > 0:
                print("[PASS] Found media by location")
            else:
                print("[FAIL] Should find media by location")
                return False
            
            db.close()
            return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def main() -> None:
    """Run all database tests."""
    print("\n")
    print("=" * 70)
    print("PHASE 2: DATABASE LAYER - TEST SUITE".center(70))
    print("=" * 70)
    
    results = []
    
    results.append(("Database Connection & Schema", test_database_connection()))
    results.append(("LocationRepository CRUD", test_location_repository()))
    results.append(("MediaRepository CRUD", test_media_repository()))
    results.append(("Media Expiration Queries", test_expiration_queries()))
    results.append(("Media-Location Relationships", test_relationships()))
    
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
        print("\n[SUCCESS] ALL TESTS PASSED - Phase 2 is complete and verified!")
        print("\nNext: Phase 3 - Business Logic Layer Implementation")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {total - passed} test(s) failed - Please review errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
