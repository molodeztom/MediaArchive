# Phase 9B: Soft Delete and Deleted Items Management - Implementation Plan

## Overview

Phase 9B implements soft delete functionality for media items, allowing users to mark items as deleted without permanently removing them from the database. This provides a safety net for accidental deletions and allows for data recovery.

**Status**: Ready for Implementation  
**Priority**: High  
**Dependencies**: None (backend already implemented)

## Current Implementation Status

### ✅ Already Implemented (Backend)

1. **Database Layer**
   - [`is_deleted`](src/data/migrations.py:291) column added to media table (INTEGER DEFAULT 0)
   - Index created on `is_deleted` column for performance
   - Migration script handles existing databases

2. **Model Layer**
   - [`is_deleted`](src/models/media.py:50) field added to Media dataclass (bool, default False)
   - Field properly serialized/deserialized in repository

3. **Repository Layer** ([`src/data/media_repository.py`](src/data/media_repository.py:1))
   - [`delete()`](src/data/media_repository.py:215) - Soft deletes by setting is_deleted=1
   - [`soft_delete()`](src/data/media_repository.py:240) - Alias for delete()
   - [`restore()`](src/data/media_repository.py:252) - Restores by setting is_deleted=0
   - [`permanent_delete()`](src/data/media_repository.py:277) - Physically removes from database
   - [`get_all()`](src/data/media_repository.py:114) - Accepts `include_deleted` parameter
   - [`get_deleted_media()`](src/data/media_repository.py:141) - Returns only deleted items
   - All search methods respect `include_deleted` parameter

4. **Service Layer** ([`src/business/media_service.py`](src/business/media_service.py:1))
   - [`delete_media()`](src/business/media_service.py:254) - Soft deletes media
   - [`delete_media_soft()`](src/business/media_service.py:270) - Alias for delete_media()
   - [`restore_media()`](src/business/media_service.py:281) - Restores deleted media
   - [`delete_media_permanent()`](src/business/media_service.py:297) - Permanently deletes
   - [`get_all_media()`](src/business/media_service.py:145) - Accepts `include_deleted` parameter
   - [`get_deleted_media()`](src/business/media_service.py:158) - Returns deleted items

### ❌ Missing Implementation (Frontend)

1. **Main Window UI**
   - No toggle button to show/hide deleted items
   - Deleted items not visually distinguished
   - No way to restore deleted items from UI
   - No way to permanently delete items from UI

2. **Statistics**
   - Statistics include deleted items (should exclude by default)
   - No separate count for deleted items

3. **Search/Filter**
   - Search doesn't respect deleted filter
   - No option to include deleted items in search

4. **Dialogs**
   - No restore confirmation dialog
   - No permanent delete confirmation dialog
   - Delete dialog doesn't explain soft delete behavior

5. **Testing**
   - No comprehensive tests for soft delete functionality

## Implementation Tasks

### Task 1: Update Main Window Toolbar

**File**: [`src/gui/main_window.py`](src/gui/main_window.py:182)

**Changes**:
1. Add instance variable `show_deleted` (bool, default False)
2. Add "Show Deleted" toggle button to toolbar after "Expired" button
3. Button should toggle between "Show Deleted" and "Hide Deleted"
4. Clicking button should:
   - Toggle `show_deleted` flag
   - Refresh media list
   - Update button text
   - Update status bar

**Implementation**:
```python
# In _create_toolbar() after exp_btn
ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

self.show_deleted = False
self.deleted_btn = ttk.Button(
    toolbar, 
    text="Show Deleted", 
    command=self._toggle_deleted
)
self.deleted_btn.pack(side=tk.LEFT, padx=2)
self._create_tooltip(self.deleted_btn, "Show/hide deleted media items")

# Add method
def _toggle_deleted(self) -> None:
    """Toggle display of deleted media items."""
    self.show_deleted = not self.show_deleted
    self.deleted_btn.config(
        text="Hide Deleted" if self.show_deleted else "Show Deleted"
    )
    self._refresh_media_list()
    status = "Showing deleted items" if self.show_deleted else "Hiding deleted items"
    self.status_var.set(status)
```

### Task 2: Update Media List Display

**File**: [`src/gui/main_window.py`](src/gui/main_window.py:398)

**Changes**:
1. Modify [`_refresh_media_list()`](src/gui/main_window.py:398) to pass `include_deleted` parameter
2. Add visual indicators for deleted items:
   - Gray out text (foreground color)
   - Add strikethrough effect (tags)
   - Optionally add "[DELETED]" prefix to name

**Implementation**:
```python
def _refresh_media_list(self) -> None:
    """Refresh media list in media tab."""
    try:
        # Clear existing items
        for item in self.media_tree.get_children():
            self.media_tree.delete(item)
        
        # Load media with deleted filter
        media_list = self.media_service.get_all_media(
            include_deleted=self.show_deleted
        )
        
        # Sort media by current sort column and direction
        media_list = self._sort_media_list(media_list, self.media_sort_column, self.media_sort_reverse)
        
        # Create location lookup for display
        locations = self.location_service.get_all_locations()
        location_map = {loc.id: loc for loc in locations}
        
        # Configure tags for deleted items
        self.media_tree.tag_configure("deleted", foreground="gray", font=("TkDefaultFont", 9, "overstrike"))
        
        for media in media_list:
            created = format_date(media.creation_date) if media.creation_date else "N/A"
            expires = format_date(media.valid_until_date) if media.valid_until_date else "N/A"
            company = media.company if media.company else "N/A"
            license_code = media.license_code if media.license_code else "N/A"
            position = media.position if media.position else "N/A"
            number = media.number if media.number else "N/A"
            category = media.category if media.category else "N/A"
            
            # Get box from location table
            if media.location_id and media.location_id in location_map:
                box = location_map[media.location_id].box
            else:
                box = "N/A"
            
            # Add [DELETED] prefix if deleted
            name = f"[DELETED] {media.name}" if media.is_deleted else media.name
            
            # Use media.id as the item ID in treeview for later retrieval
            tags = ("deleted",) if media.is_deleted else ()
            self.media_tree.insert("", tk.END, iid=str(media.id), values=(
                number,
                name,
                media.media_type,
                category,
                box,
                position,
                company,
                license_code,
                created,
                expires
            ), tags=tags)
        
        count_msg = f"Loaded {len(media_list)} media items"
        if self.show_deleted:
            deleted_count = sum(1 for m in media_list if m.is_deleted)
            count_msg += f" ({deleted_count} deleted)"
        self.status_var.set(count_msg)
        logger.debug(f"Refreshed media list: {len(media_list)} items")
    except Exception as e:
        logger.error(f"Failed to refresh media list: {e}")
        messagebox.showerror("Error", f"Failed to load media: {e}")
```

### Task 3: Add Context Menu for Deleted Items

**File**: [`src/gui/main_window.py`](src/gui/main_window.py:229)

**Changes**:
1. Add right-click context menu to media tree
2. Show different options based on item's deleted status:
   - For normal items: Edit, Delete, View Location
   - For deleted items: Restore, Permanent Delete, View Details

**Implementation**:
```python
# In _create_media_tab() after binding double-click
self.media_tree.bind("<Button-3>", self._on_media_right_click)

def _on_media_right_click(self, event) -> None:
    """Handle right-click on media item to show context menu."""
    try:
        # Select item under cursor
        item = self.media_tree.identify_row(event.y)
        if not item:
            return
        
        self.media_tree.selection_set(item)
        
        # Get media details
        media_id = int(item)
        media = self.media_service.get_media(media_id)
        
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0)
        
        if media.is_deleted:
            # Options for deleted items
            menu.add_command(label="Restore", command=self._restore_media)
            menu.add_separator()
            menu.add_command(label="Permanent Delete", command=self._permanent_delete_media)
        else:
            # Options for normal items
            menu.add_command(label="Edit", command=self._edit_media)
            menu.add_command(label="Delete", command=self._delete_media)
            menu.add_separator()
            if media.location_id:
                menu.add_command(label="View Location", command=lambda: self._jump_to_location(media.location_id))
        
        # Show menu at cursor position
        menu.post(event.x_root, event.y_root)
        
    except Exception as e:
        logger.error(f"Error showing context menu: {e}")

def _jump_to_location(self, location_id: int) -> None:
    """Jump to location tab and select location."""
    self.notebook.select(1)  # Switch to locations tab
    location_iid = str(location_id)
    if location_iid in self.location_tree.get_children():
        self.location_tree.selection_set(location_iid)
        self.location_tree.see(location_iid)
```

### Task 4: Add Restore Functionality

**File**: [`src/gui/main_window.py`](src/gui/main_window.py:756)

**Changes**:
1. Add [`_restore_media()`](src/gui/main_window.py:756) method
2. Show confirmation dialog before restoring
3. Refresh media list after restore

**Implementation**:
```python
def _restore_media(self) -> None:
    """Restore a soft-deleted media item."""
    try:
        # Get selected media
        selection = self.media_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a media item to restore")
            return
        
        # Get media ID from treeview item ID
        item = selection[0]
        media_id = int(item)
        
        # Get media details
        media = self.media_service.get_media(media_id)
        
        # Confirm restore
        result = messagebox.askyesno(
            "Restore Media",
            f"Restore media item?\n\n"
            f"Name: {media.name}\n"
            f"Type: {media.media_type}\n\n"
            f"This will make the item visible again."
        )
        
        if result:
            self.media_service.restore_media(media_id)
            self.status_var.set(f"Restored media: {media.name}")
            self._refresh_media_list()
            logger.info(f"Restored media: {media_id}")
    except Exception as e:
        logger.error(f"Error restoring media: {e}")
        messagebox.showerror("Error", f"Failed to restore media: {e}")
```

### Task 5: Add Permanent Delete Functionality

**File**: [`src/gui/main_window.py`](src/gui/main_window.py:756)

**Changes**:
1. Add [`_permanent_delete_media()`](src/gui/main_window.py:756) method
2. Show strong warning dialog before permanent deletion
3. Require explicit confirmation (e.g., type "DELETE")
4. Refresh media list after deletion

**Implementation**:
```python
def _permanent_delete_media(self) -> None:
    """Permanently delete a media item from database."""
    try:
        # Get selected media
        selection = self.media_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a media item to delete")
            return
        
        # Get media ID from treeview item ID
        item = selection[0]
        media_id = int(item)
        
        # Get media details
        media = self.media_service.get_media(media_id)
        
        # Show strong warning
        result = messagebox.askyesno(
            "⚠️ PERMANENT DELETE",
            f"PERMANENTLY delete media item?\n\n"
            f"Name: {media.name}\n"
            f"Type: {media.media_type}\n\n"
            f"⚠️ WARNING: This action CANNOT be undone!\n"
            f"The item will be permanently removed from the database.\n\n"
            f"Are you absolutely sure?",
            icon="warning"
        )
        
        if result:
            # Second confirmation
            result2 = messagebox.askyesno(
                "⚠️ FINAL CONFIRMATION",
                f"This is your last chance!\n\n"
                f"Permanently delete '{media.name}'?\n\n"
                f"This action is IRREVERSIBLE!",
                icon="warning"
            )
            
            if result2:
                self.media_service.delete_media_permanent(media_id)
                self.status_var.set(f"Permanently deleted media: {media.name}")
                self._refresh_media_list()
                logger.info(f"Permanently deleted media: {media_id}")
    except Exception as e:
        logger.error(f"Error permanently deleting media: {e}")
        messagebox.showerror("Error", f"Failed to permanently delete media: {e}")
```

### Task 6: Update Delete Dialog

**File**: [`src/gui/dialogs.py`](src/gui/dialogs.py:625)

**Changes**:
1. Update [`DeleteConfirmDialog`](src/gui/dialogs.py:625) to explain soft delete
2. Add information that item can be restored
3. Optionally add checkbox for "Permanent delete" (advanced users)

**Implementation**:
```python
class DeleteConfirmDialog(BaseDialog):
    """Dialog for confirming media deletion (soft delete)."""
    
    def __init__(self, parent: tk.Widget, media, on_confirm=None) -> None:
        """Initialize delete confirmation dialog.
        
        Args:
            parent: Parent window.
            media: Media object to delete.
            on_confirm: Callback function when deletion is confirmed.
        """
        super().__init__(parent, "Confirm Delete")
        self.media = media
        self.on_confirm = on_confirm
        self.result = False
        logger.debug(f"DeleteConfirmDialog initialized for media: {media.id}")
    
    def _create_content(self) -> None:
        """Create dialog content."""
        # Info icon and message
        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Info message
        info_label = ttk.Label(
            info_frame,
            text="ℹ️ Soft Delete: The item will be hidden but can be restored later.",
            foreground="blue",
            font=("Arial", 9, "italic")
        )
        info_label.pack(anchor=tk.W)
        
        # Media details
        details_frame = ttk.LabelFrame(self.content_frame, text="Media Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(details_frame, text=f"Name: {self.media.name}", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Label(details_frame, text=f"Type: {self.media.media_type}").pack(anchor=tk.W, pady=2)
        if self.media.number:
            ttk.Label(details_frame, text=f"Number: {self.media.number}").pack(anchor=tk.W, pady=2)
        
        # Warning message
        warning_label = ttk.Label(
            self.content_frame,
            text="Delete this media item?\n\nYou can restore it later from 'Show Deleted' view.",
            justify=tk.LEFT
        )
        warning_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self._on_confirm).pack(side=tk.RIGHT)
```

### Task 7: Update Statistics

**File**: [`src/business/media_service.py`](src/business/media_service.py:436)

**Changes**:
1. Modify [`get_media_statistics()`](src/business/media_service.py:436) to exclude deleted items by default
2. Add separate count for deleted items
3. Update statistics dialog to show deleted count

**Implementation**:
```python
def get_media_statistics(self) -> dict:
    """Get statistics about media collection.
    
    Returns:
        Dictionary with statistics (excludes deleted items by default).
    """
    # Get active media (not deleted)
    all_media = self._repo.get_all(include_deleted=False)
    
    # Get deleted media separately
    deleted_media = self._repo.get_deleted_media()
    
    expired = self._repo.get_expired_media(include_deleted=False)
    expiring_soon = self._repo.get_expiring_soon(30, include_deleted=False)
    
    # Count by type (active only)
    by_type = {}
    for media in all_media:
        by_type[media.media_type] = by_type.get(media.media_type, 0) + 1
    
    stats = {
        "total_media": len(all_media),
        "deleted_media": len(deleted_media),
        "expired_media": len(expired),
        "expiring_soon": len(expiring_soon),
        "media_by_type": by_type,
        "media_with_location": sum(1 for m in all_media if m.has_location()),
        "media_without_location": sum(1 for m in all_media if not m.has_location()),
    }
    
    logger.debug(f"Media statistics: {stats}")
    return stats
```

**File**: [`src/gui/statistics_dialog.py`](src/gui/statistics_dialog.py:116)

**Changes**:
```python
# In _create_overview_tab(), add after total_media:
self._add_stat_row(scrollable_frame, "Deleted Media:", str(self.stats.get("deleted_media", 0)))
```

### Task 8: Update Search to Respect Deleted Filter

**File**: [`src/gui/main_window.py`](src/gui/main_window.py:996)

**Changes**:
1. Modify [`_perform_search()`](src/gui/main_window.py:996) to exclude deleted items by default
2. Add option to include deleted items in search (checkbox in search panel)

**Implementation**:
```python
def _perform_search(self) -> None:
    """Perform search based on search criteria."""
    try:
        # Clear existing results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Get search criteria from search panel
        criteria = self.search_panel.get_search_criteria()
        query = criteria["query"]
        type_filter = criteria["type_filter"]
        box_filter = criteria.get("box_filter", "All")
        place_filter = criteria.get("place_filter", "")
        show_expired = criteria["show_expired"]
        date_from = criteria["date_from"]
        date_to = criteria["date_to"]
        
        # Start with all media or search results
        # Exclude deleted items unless show_deleted is enabled
        if query:
            results = self.media_service.search_media_by_name(query)
        else:
            results = self.media_service.get_all_media(include_deleted=self.show_deleted)
        
        # Filter out deleted items if not showing deleted
        if not self.show_deleted:
            results = [m for m in results if not m.is_deleted]
        
        # ... rest of search logic remains the same ...
```

### Task 9: Add Comprehensive Tests

**File**: `tests/test_phase9b_soft_delete.py` (new file)

**Test Cases**:
1. Test soft delete marks item as deleted
2. Test deleted items hidden by default
3. Test restore functionality
4. Test permanent delete
5. Test statistics exclude deleted items
6. Test search excludes deleted items
7. Test include_deleted parameter
8. Test multiple delete/restore cycles
9. Test edge cases (delete already deleted, restore non-deleted, etc.)

**Implementation**:
```python
"""Tests for Phase 9B: Soft Delete functionality.

This module tests the soft delete feature including:
- Soft delete operations
- Restore operations
- Permanent delete operations
- Filtering deleted items
- Statistics with deleted items
- Search with deleted items
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
```

### Task 10: Update Documentation

**File**: `docs/PHASE9B_SOFT_DELETE.md` (new file)

**Content**:
- Feature overview
- User guide (how to use soft delete)
- Technical implementation details
- API documentation
- Migration guide

## UI/UX Design

### Visual Indicators for Deleted Items

1. **Text Styling**
   - Gray foreground color (#808080)
   - Strikethrough font style
   - "[DELETED]" prefix in name column

2. **Toggle Button States**
   - Default: "Show Deleted" (blue/normal)
   - Active: "Hide Deleted" (highlighted)

3. **Context Menu**
   - Normal items: Edit | Delete | View Location
   - Deleted items: Restore | Permanent Delete | View Details

### Dialog Designs

#### Soft Delete Confirmation
```
┌─────────────────────────────────────┐
│ Confirm Delete                   [X]│
├─────────────────────────────────────┤
│ ℹ️ Soft Delete: The item will be   │
│   hidden but can be restored later. │
│                                     │
│ ┌─ Media Details ─────────────────┐│
│ │ Name: My Important CD           ││
│ │ Type: CD-ROM                    ││
│ │ Number: 42                      ││
│ └─────────────────────────────────┘│
│                                     │
│ Delete this media item?             │
│                                     │
│ You can restore it later from       │
│ 'Show Deleted' view.                │
│                                     │
│              [Cancel]  [Delete]     │
└─────────────────────────────────────┘
```

#### Restore Confirmation
```
┌─────────────────────────────────────┐
│ Restore Media                    [X]│
├─────────────────────────────────────┤
│ Restore media item?                 │
│                                     │
│ Name: My Important CD               │
│ Type: CD-ROM                        │
│                                     │
│ This will make the item visible     │
│ again.                              │
│                                     │
│                [No]  [Yes]          │
└─────────────────────────────────────┘
```

#### Permanent Delete Confirmation
```
┌─────────────────────────────────────┐
│ ⚠️ PERMANENT DELETE              [X]│
├─────────────────────────────────────┤
│ PERMANENTLY delete media item?      │
│                                     │
│ Name: My Important CD               │
│ Type: CD-ROM                        │
│                                     │
│ ⚠️ WARNING: This action CANNOT be  │
│ undone! The item will be            │
│ permanently removed from the        │
│ database.                           │
│                                     │
│ Are you absolutely sure?            │
│                                     │
│                [No]  [Yes]          │
└─────────────────────────────────────┘
```

## Testing Strategy

### Unit Tests
- Test repository methods (soft_delete, restore, permanent_delete)
- Test service methods
- Test filtering logic
- Test statistics calculations

### Integration Tests
- Test UI interactions
- Test dialog flows
- Test data consistency
- Test edge cases

### Manual Testing Checklist
- [ ] Delete media item (soft delete)
- [ ] Verify item disappears from main list
- [ ] Click "Show Deleted" button
- [ ] Verify deleted item appears with visual indicators
- [ ] Right-click deleted item
- [ ] Select "Restore" from context menu
- [ ] Verify item restored and visible
- [ ] Delete item again
- [ ] Right-click and select "Permanent Delete"
- [ ] Confirm both warnings
- [ ] Verify item completely removed
- [ ] Check statistics exclude deleted items
- [ ] Check search excludes deleted items
- [ ] Test with multiple items
- [ ] Test sorting with deleted items
- [ ] Test import/export with deleted items

## Migration Considerations

### Database Migration
- Migration already implemented in [`src/data/migrations.py`](src/data/migrations.py:291)
- Existing databases will have `is_deleted` column added automatically
- All existing records will have `is_deleted=0` (not deleted)
- Index created for performance

### Backward Compatibility
- Existing code continues to work (deleted items hidden by default)
- No breaking changes to API
- Optional `include_deleted` parameter added to methods

## Performance Considerations

1. **Index on is_deleted**
   - Already created in migration
   - Improves query performance for filtering

2. **Query Optimization**
   - Use `WHERE is_deleted = 0` in all default queries
   - Avoid loading deleted items unless explicitly requested

3. **UI Performance**
   - Deleted items only loaded when "Show Deleted" is active
   - Visual indicators use tags (efficient in Tkinter)

## Security Considerations

1. **Permanent Delete**
   - Requires double confirmation
   - Strong warning messages
   - Logged for audit trail

2. **Access Control**
   - Consider adding permission levels in future
   - Permanent delete could be admin-only

## Future Enhancements

1. **Bulk Operations**
   - Restore multiple items at once
   - Permanently delete multiple items

2. **Auto-Cleanup**
   - Automatically permanently delete items after X days
   - Configurable retention period

3. **Recycle Bin View**
   - Dedicated tab for deleted items
   - Show deletion date/time
   - Show who deleted (if user tracking added)

4. **Undo/Redo**
   - Implement undo stack for delete operations
   - Quick undo button after delete

## Success Criteria

- ✅ Soft delete implemented and working
- ✅ Toggle button shows/hides deleted items
- ✅ Deleted items visually distinguished
- ✅ Restore functionality working
- ✅ Permanent delete with strong warnings
- ✅ Statistics exclude deleted items
- ✅ Search excludes deleted items
- ✅ All tests passing
- ✅ Documentation complete
- ✅ No regressions in existing features

## Implementation Timeline

1. **Day 1**: UI updates (toggle button, visual indicators)
2. **Day 2**: Context menu and restore functionality
3. **Day 3**: Permanent delete and dialogs
4. **Day 4**: Statistics and search updates
5. **Day 5**: Testing and bug fixes
6. **Day 6**: Documentation and polish

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Accidental permanent delete | High | Double confirmation, strong warnings |
| Performance with many deleted items | Medium | Index on is_deleted, lazy loading |
| User confusion about soft delete | Medium | Clear UI messages, documentation |
| Data loss during migration | High | Backup before migration, thorough testing |

## Conclusion

Phase 9B implementation is straightforward since the backend is already complete. The focus is on creating an intuitive UI that makes soft delete functionality accessible while preventing accidental permanent deletions. The implementation follows best practices for data safety and user experience.

---

**Document Version**: 1.0  
**Created**: 2026-03-09  
**Status**: Ready for Implementation  
**Next Step**: Begin Task 1 (Update Main Window Toolbar)
