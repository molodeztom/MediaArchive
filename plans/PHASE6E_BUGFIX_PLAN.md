# Phase 6E: Bugfix and UI Enhancement Plan

## Overview

This phase addresses critical bugs and UI improvements discovered during Phase 6D testing and implementation. The focus is on fixing location assignment logic, improving UI usability, and adding table sorting functionality.

## Issues Identified

### 1. Media Tab Sorting
**Issue**: Media tab is not sorted by Number column  
**Current**: Media displayed in database insertion order  
**Expected**: Media sorted by Number column (1, 2, 3, ..., x)

### 2. Location Tab ID Column
**Issue**: Location tab shows internal database ID column  
**Current**: ID column visible (1, 2, 3, ...)  
**Expected**: ID column should be hidden (only Box, Place, Detail, Media Count visible)

### 3. Location Assignment Tool Issues
**Issue**: "Assign Locations to Media" tool creates duplicate entries with wrong box IDs  
**Current**: Tool may be creating duplicates or incorrectly mapping box numbers  
**Expected**: Tool should correctly map box numbers to location IDs without duplicates

### 4. Box Display in Media Tab
**Issue**: Box column may show incorrect values (off by ±1)  
**Current**: Box value might be showing location.id instead of location.box  
**Expected**: Box column must show location.box value (e.g., "1", "2", "30"), not database ID

### 5. Edit Media Dialog - Location Display
**Issue**: Edit Media dialog doesn't show Place from location table  
**Current**: Only shows Box dropdown and Position field  
**Expected**: Show both Box number AND Place from location table (read-only, 1:1 relationship)

### 6. Search Tab - Location Filter
**Issue**: Location filter uses single dropdown with full location string  
**Current**: One dropdown showing "ID: Box / Place / Detail"  
**Expected**: Two separate UI elements:
  - Box number dropdown (all box numbers from location table)
  - Place input field (text search)

### 7. Filter Menu - Location Filter
**Issue**: Filter > By Location menu is not useful with single dropdown  
**Current**: Menu shows all locations in dropdown  
**Expected**: Remove this menu item (replaced by Search tab filters)

### 8. Category Dropdown in Media Dialogs
**Issue**: Category field is plain text entry  
**Current**: User must type category manually  
**Expected**: Combobox with:
  - Dropdown showing all existing categories from database
  - Ability to type new category value
  - State="normal" (not "readonly")

### 9. Media Tab - Column Sorting
**Issue**: No sorting functionality on table headers  
**Current**: Clicking headers does nothing  
**Expected**: 
  - Click header: Sort by that column (ascending)
  - Click again: Toggle sort order (descending)
  - Visual indicator for current sort column and direction

## Data Analysis

From [`tests/CDROM_export.csv`](tests/CDROM_export.csv:1):
- Box values: 0-50 (integers, some gaps)
- Position values: 0-75 (integers)
- Box and Position are separate fields in CSV

From [`tests/Location_Export.csv`](tests/Location_Export.csv:1):
- Box values: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 30, 40, 50
- Ort (Place) values: Various German text descriptions
- Typ (Detail) values: Various German text descriptions

**Key Insight**: Box numbers in media CSV (column 4) must match Box numbers in location CSV (column 1). These are NOT database IDs but user-visible box identifiers.

## Implementation Plan

### Task 1: Fix Media Tab Sorting
**File**: [`src/gui/main_window.py`](src/gui/main_window.py:330)

**Changes**:
1. In `_refresh_media_list()` method, sort media_list by number before displaying
2. Handle None values and non-numeric numbers
3. Sort logic: numeric numbers first (1, 2, 3...), then non-numeric alphabetically

**Implementation**:
```python
# Sort media by number (numeric first, then alphabetic)
def sort_key(media):
    if media.number:
        try:
            return (0, int(media.number))  # Numeric numbers first
        except ValueError:
            return (1, media.number)  # Non-numeric alphabetically
    return (2, "")  # No number last

media_list.sort(key=sort_key)
```

### Task 2: Hide Location Tab ID Column
**File**: [`src/gui/main_window.py`](src/gui/main_window.py:237)

**Changes**:
1. Remove "ID" from columns tuple
2. Remove ID column configuration
3. Update `_refresh_locations_list()` to not include ID in values
4. Update `_edit_location()` and `_delete_location()` to get ID from item iid instead of values[0]

**Implementation**:
```python
# Use iid to store location ID instead of first column
self.location_tree.insert("", tk.END, iid=str(loc.id), values=(
    loc.box,
    loc.place,
    loc.detail or "",
    media_count
))

# Retrieve ID from iid
item = selection[0]
location_id = int(item)  # iid is the location ID
```

### Task 3: Fix Location Assignment Logic
**File**: [`src/business/media_service.py`](src/business/media_service.py:460)

**Investigation Needed**:
1. Review `assign_locations_by_box_place()` method
2. Check if method is creating duplicates
3. Verify box number to location ID mapping logic
4. Add logging to track assignment process

**Potential Issues**:
- Method might be called multiple times
- Box number matching might be incorrect
- Need to verify location.box values are strings matching media CSV box values

### Task 4: Verify Box Display Logic
**File**: [`src/gui/main_window.py`](src/gui/main_window.py:352)

**Current Implementation**:
```python
if media.location_id and media.location_id in location_map:
    box = location_map[media.location_id].box
else:
    box = "N/A"
```

**Verification**:
- This looks correct - it gets location.box via location_id
- Need to test with real data to confirm
- Check if location_map is built correctly

### Task 5: Enhance Edit Media Dialog
**File**: [`src/gui/dialogs.py`](src/gui/dialogs.py:351)

**Changes**:
1. Add read-only Place field below Box dropdown
2. Update Place field when Box selection changes
3. Show current Place value from location table

**Implementation**:
```python
# Box dropdown with change handler
box_combo.bind("<<ComboboxSelected>>", self._on_box_changed)

# Place field (read-only)
ttk.Label(main_frame, text="Place").grid(row=3, column=0, sticky=tk.W, pady=5)
self.place_display_var = tk.StringVar()
place_entry = ttk.Entry(main_frame, textvariable=self.place_display_var, state="readonly", width=40)
place_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)

# Position field moves to row 4
ttk.Label(main_frame, text="Position").grid(row=4, column=0, sticky=tk.W, pady=5)
```

### Task 6: Enhance Search Tab Location Filter
**File**: [`src/gui/search_panel.py`](src/gui/search_panel.py:1)

**Changes**:
1. Replace single location dropdown with two fields:
   - Box number dropdown (readonly combobox)
   - Place text entry field
2. Update `get_search_criteria()` to return box and place separately
3. Update `_perform_search()` in main_window.py to filter by box and/or place

**Implementation**:
```python
# Box filter
ttk.Label(filter_frame, text="Box:").grid(row=X, column=0, sticky=tk.W, pady=5)
self.box_filter_var = tk.StringVar(value="All")
box_values = ["All"] + sorted(set(loc.box for loc in locations))
box_combo = ttk.Combobox(filter_frame, textvariable=self.box_filter_var, 
                         values=box_values, state="readonly", width=15)

# Place filter
ttk.Label(filter_frame, text="Place:").grid(row=X+1, column=0, sticky=tk.W, pady=5)
self.place_filter_var = tk.StringVar()
place_entry = ttk.Entry(filter_frame, textvariable=self.place_filter_var, width=20)
```

### Task 7: Remove Filter Menu Location Item
**File**: [`src/gui/main_window.py`](src/gui/main_window.py:133)

**Changes**:
1. Remove "By Location" submenu from Filter menu
2. Remove `_update_location_menu()` method
3. Remove `_filter_by_location()` method
4. Keep "By Type" and "Clear Filters" menu items

### Task 8: Add Category Combobox to Media Dialogs
**Files**: 
- [`src/gui/dialogs.py`](src/gui/dialogs.py:80) - AddMediaDialog
- [`src/gui/dialogs.py`](src/gui/dialogs.py:319) - EditMediaDialog

**Changes**:
1. Replace Category Entry with Combobox
2. Populate with existing categories from database
3. Set state="normal" to allow typing new values
4. Add method to get unique categories from database

**Implementation**:
```python
# In dialog __init__, get existing categories
existing_categories = self._get_existing_categories()

# Category combobox (editable)
ttk.Label(main_frame, text="Category").grid(row=5, column=0, sticky=tk.W, pady=5)
self.category_var = tk.StringVar()
category_combo = ttk.Combobox(
    main_frame,
    textvariable=self.category_var,
    values=existing_categories,
    state="normal",  # Allows typing new values
    width=37
)
category_combo.grid(row=5, column=1, sticky=tk.EW, pady=5)

def _get_existing_categories(self):
    """Get list of unique categories from database."""
    # Need to pass media_service or get categories from parent
    pass
```

### Task 9: Add Column Sorting to Media Tab
**File**: [`src/gui/main_window.py`](src/gui/main_window.py:192)

**Changes**:
1. Add click handlers to column headers
2. Track current sort column and direction
3. Implement sort logic for each column type
4. Add visual indicator (▲/▼) to sorted column header

**Implementation**:
```python
# Add instance variables
self.sort_column = "Number"  # Default sort column
self.sort_reverse = False  # Ascending by default

# Bind header clicks
for col in columns:
    self.media_tree.heading(col, text=col, anchor=tk.W, 
                           command=lambda c=col: self._sort_media_by_column(c))

def _sort_media_by_column(self, column):
    """Sort media list by clicked column."""
    # Toggle direction if same column
    if self.sort_column == column:
        self.sort_reverse = not self.sort_reverse
    else:
        self.sort_column = column
        self.sort_reverse = False
    
    # Refresh with new sort
    self._refresh_media_list()
    
    # Update header to show sort indicator
    for col in self.media_tree["columns"]:
        if col == column:
            indicator = " ▼" if self.sort_reverse else " ▲"
            self.media_tree.heading(col, text=col + indicator)
        else:
            self.media_tree.heading(col, text=col)
```

## Implementation Order

1. **Task 2**: Hide Location Tab ID Column (simple, no dependencies)
2. **Task 1**: Fix Media Tab Sorting (simple, improves usability immediately)
3. **Task 4**: Verify Box Display Logic (investigation/testing)
4. **Task 3**: Fix Location Assignment Logic (critical bug fix)
5. **Task 5**: Enhance Edit Media Dialog (add Place display)
6. **Task 8**: Add Category Combobox (requires database query method)
7. **Task 6**: Enhance Search Tab Location Filter (moderate complexity)
8. **Task 7**: Remove Filter Menu Location Item (cleanup)
9. **Task 9**: Add Column Sorting (enhancement, most complex)

## Testing Strategy

### Unit Tests
- Test sorting logic with various number formats
- Test location assignment with real CSV data
- Test category retrieval from database

### Integration Tests
- Import real CSV files (CDROM_export.csv, Location_Export.csv)
- Verify box numbers match between media and locations
- Test location assignment tool
- Verify UI displays correct values

### Manual Testing
- Test all dialog interactions
- Verify sorting works correctly
- Test search filters with box/place
- Verify category dropdown shows existing values

## Files to Modify

1. [`src/gui/main_window.py`](src/gui/main_window.py:1) - Media tab sorting, location tab ID hiding, filter menu, column sorting
2. [`src/gui/dialogs.py`](src/gui/dialogs.py:1) - Edit Media dialog Place display, Category combobox
3. [`src/gui/search_panel.py`](src/gui/search_panel.py:1) - Box/Place filter UI
4. [`src/business/media_service.py`](src/business/media_service.py:1) - Location assignment logic review
5. [`src/data/media_repository.py`](src/data/media_repository.py:1) - Add method to get unique categories

## Success Criteria

- ✅ Media tab sorted by Number column (numeric first, then alphabetic)
- ✅ Location tab ID column hidden
- ✅ Location assignment tool works correctly without duplicates
- ✅ Box column in media tab shows correct box numbers from location table
- ✅ Edit Media dialog shows Box number and Place from location table
- ✅ Search tab has separate Box dropdown and Place input filters
- ✅ Filter menu no longer has "By Location" submenu
- ✅ Category field in media dialogs is editable combobox with existing values
- ✅ Media tab columns sortable by clicking headers
- ✅ All tests pass

## Notes

- Box numbers in CSV are user-visible identifiers (0, 1, 2, 3, ..., 50)
- Database location.id is internal (1, 2, 3, ..., 24)
- Mapping: location.box → location.id (e.g., box "30" → id 22)
- Media.location_id stores database ID, not box number
- Display must show location.box, not location.id
