# Phase 6d: Fix Automatic Location Assignment After Import

## Overview
Fix the automatic location assignment for media after importing locations. Currently, media items don't get their locations assigned properly because the location lookup happens during CSV parsing when locations may not exist yet in the database.

## Current Problem

### Issue 1: Location Lookup Timing
- **Current behavior**: AccessCSVMapper.parse_media_row() tries to find locations by Box+Place during CSV parsing
- **Problem**: If locations haven't been imported yet, lookup fails and media.location_id is set to NULL
- **Location**: [`src/business/access_csv_mapper.py`](../src/business/access_csv_mapper.py:204-213)

### Issue 2: Incomplete Location Assignment
- **Current behavior**: `_process_import()` only updates media that have temporary location IDs in the mapping
- **Problem**: Media without location IDs (because locations didn't exist during parsing) are never updated
- **Location**: [`src/gui/main_window.py`](../src/gui/main_window.py:919-943)

### Issue 3: No User Guidance
- **Current behavior**: No warning if locations are missing when importing media
- **Problem**: User doesn't know they need to import locations first
- **Location**: Import dialog doesn't check for existing locations

## Solution Strategy

### Approach 1: Post-Import Location Assignment (Recommended)
After both media and locations are imported, run a location assignment process that:
1. Finds all media without location_id
2. Matches them to locations by Box+Place
3. Updates media with correct location IDs
4. Reports results to user

### Approach 2: Import Order Enforcement
- Check if locations exist before allowing media import
- If no locations, prompt user to import locations first
- Show warning dialog with option to continue anyway

### Approach 3: Combined Approach (Best)
- Implement both approaches
- Always run post-import location assignment
- Warn user if importing media without locations

## Implementation Plan

### Step 1: Create Location Assignment Service Method

**File**: [`src/business/media_service.py`](../src/business/media_service.py)

Add new method:
```python
def assign_locations_by_box_place(self, locations: List[StorageLocation]) -> dict:
    """Assign locations to media based on Box+Place matching.
    
    Args:
        locations: List of available locations
    
    Returns:
        Dictionary with assignment statistics:
        - total_media: Total media items checked
        - assigned: Number of media assigned locations
        - already_assigned: Number already had locations
        - not_found: Number where location wasn't found
    """
```

### Step 2: Update Import Process

**File**: [`src/gui/main_window.py`](../src/gui/main_window.py)

Update `_process_import()` method:
1. After importing locations, run location assignment for all media
2. After importing media, run location assignment
3. Show results dialog with statistics

### Step 3: Add Import Validation

**File**: [`src/gui/import_dialog.py`](../src/gui/import_dialog.py)

Add validation before media import:
1. Check if any locations exist in database
2. If no locations, show warning dialog:
   - "No locations found in database"
   - "Media items may not be assigned to locations"
   - "Would you like to import locations first?"
   - Options: "Import Locations", "Continue Anyway", "Cancel"

### Step 4: Update Access CSV Mapper

**File**: [`src/business/access_csv_mapper.py`](../src/business/access_csv_mapper.py)

Simplify location lookup during parsing:
- Don't try to match locations during parsing
- Just store Box and Place values in media object
- Let post-import assignment handle the matching

**OR** keep current behavior but add fallback:
- Try to match during parsing (for when locations exist)
- If not found, store Box+Place for later matching
- Post-import assignment will handle unmatched media

### Step 5: Add Location Assignment Dialog

**File**: [`src/gui/dialogs.py`](../src/gui/dialogs.py)

Create new dialog:
```python
class LocationAssignmentDialog(BaseDialog):
    """Dialog showing location assignment results."""
    
    def __init__(self, parent, results: dict):
        """
        Args:
            parent: Parent window
            results: Assignment results dictionary
        """
```

### Step 6: Add Manual Location Assignment Feature

**File**: [`src/gui/main_window.py`](../src/gui/main_window.py)

Add menu item: "Tools" → "Assign Locations to Media"
- Runs location assignment for all media
- Shows results dialog
- Refreshes media list

---

## Detailed Implementation

### MediaService.assign_locations_by_box_place()

```python
def assign_locations_by_box_place(self, locations: List[StorageLocation]) -> dict:
    """Assign locations to media based on Box+Place matching.
    
    Finds all media items and attempts to assign them to locations by matching
    the Box and Place fields from the Access CSV import.
    
    Args:
        locations: List of available storage locations
    
    Returns:
        Dictionary with assignment statistics:
        - total_media: Total media items checked
        - assigned: Number of media newly assigned locations
        - already_assigned: Number that already had locations
        - not_found: Number where matching location wasn't found
        - updated_media: List of updated media IDs
    """
    stats = {
        "total_media": 0,
        "assigned": 0,
        "already_assigned": 0,
        "not_found": 0,
        "updated_media": []
    }
    
    # Get all media
    all_media = self.get_all_media()
    stats["total_media"] = len(all_media)
    
    # Create location lookup by Box+Place
    location_map = {}
    for loc in locations:
        key = f"{loc.box}|{loc.place}"
        location_map[key] = loc.id
    
    # Process each media item
    for media in all_media:
        # Skip if already has location
        if media.location_id is not None:
            stats["already_assigned"] += 1
            continue
        
        # Try to find location by Box+Place
        # Note: This requires storing Box+Place in media during import
        # For now, we can't do this without modifying the Media model
        # So this method will only work for media imported with temporary IDs
        
        # TODO: Need to store Box+Place in media for this to work
        stats["not_found"] += 1
    
    return stats
```

**Problem**: This approach requires storing Box+Place in the Media model, which we don't currently do.

### Alternative: Store Box+Place During Import

**Option A**: Add temporary fields to Media model
- Add `import_box: Optional[str]` and `import_place: Optional[str]`
- Store during import, use for matching, then clear

**Option B**: Use a separate mapping table
- Create temporary table: `media_location_mapping(media_id, box, place)`
- Populate during import
- Use for matching
- Drop after assignment

**Option C**: Store in remarks or content_description
- Append Box+Place to remarks during import
- Parse and match after import
- Remove from remarks after assignment

**Recommendation**: Option A is cleanest but requires model changes. Option B is most flexible.

### Simplified Approach (No Model Changes)

Since we already have the two-phase import working with temporary IDs, we can enhance it:

1. **During Location Import**:
   - Store mapping of Box+Place → database ID
   - Keep this mapping in memory or temporary storage

2. **During Media Import**:
   - For each media, store Box+Place from CSV
   - After all media imported, match against location mapping
   - Update media with correct location IDs

3. **Post-Import Assignment**:
   - Get all media without location_id
   - Get all locations
   - For each media, try to infer Box+Place from name or other fields
   - Match and update

**Problem**: We don't currently store Box+Place in media, so we can't match after the fact.

### Practical Solution (Phase 6d)

Given the constraints, the best approach is:

1. **Enhance Import Dialog**:
   - Check if locations exist before media import
   - Warn user if no locations found
   - Suggest importing locations first

2. **Improve Import Process**:
   - When importing media from Access CSV, store Box+Place temporarily
   - After import, immediately try to match with existing locations
   - Show results: "X media assigned, Y not found"

3. **Add Manual Assignment Tool**:
   - Menu item: "Tools" → "Assign Locations"
   - Scans all media without locations
   - Tries to match based on available data
   - Shows results

4. **Store Box+Place in Media**:
   - Add `box` and `place` fields to Media model (optional)
   - Store during Access import
   - Use for location matching
   - Can be cleared after assignment or kept for reference

---

## Implementation Steps

### Phase 6d.1: Add Box/Place Fields to Media Model

**Files to modify**:
- [`src/models/media.py`](../src/models/media.py): Add `box` and `place` fields
- [`src/data/schema.py`](../src/data/schema.py): Add columns to media table
- [`src/data/migrations.py`](../src/data/migrations.py): Add migration for new columns
- [`src/data/media_repository.py`](../src/data/media_repository.py): Update CRUD operations
- [`src/business/media_service.py`](../src/business/media_service.py): Update methods

### Phase 6d.2: Store Box/Place During Import

**Files to modify**:
- [`src/business/access_csv_mapper.py`](../src/business/access_csv_mapper.py): Store box/place in Media object
- [`src/gui/import_dialog.py`](../src/gui/import_dialog.py): Pass box/place through

### Phase 6d.3: Implement Location Assignment

**Files to modify**:
- [`src/business/media_service.py`](../src/business/media_service.py): Add `assign_locations_by_box_place()` method
- [`src/gui/main_window.py`](../src/gui/main_window.py): Call assignment after import

### Phase 6d.4: Add User Guidance

**Files to modify**:
- [`src/gui/import_dialog.py`](../src/gui/import_dialog.py): Add location check and warning
- [`src/gui/dialogs.py`](../src/gui/dialogs.py): Add LocationAssignmentResultsDialog

### Phase 6d.5: Add Manual Assignment Tool

**Files to modify**:
- [`src/gui/main_window.py`](../src/gui/main_window.py): Add "Tools" menu with "Assign Locations" item

---

## Testing Plan

### Test 1: Import Locations Then Media
1. Start with empty database
2. Import locations from Access CSV
3. Import media from Access CSV
4. Verify all media have correct location_id
5. Check that Box+Place fields are populated

### Test 2: Import Media Then Locations
1. Start with empty database
2. Import media from Access CSV
3. Verify media have no location_id but have Box+Place
4. Import locations from Access CSV
5. Verify automatic assignment runs
6. Check that media now have correct location_id

### Test 3: Manual Assignment
1. Create media without locations
2. Create locations
3. Use "Assign Locations" tool
4. Verify assignment works

### Test 4: Partial Matches
1. Import media with various Box+Place values
2. Import locations with only some matching Box+Place
3. Verify correct matches are made
4. Verify unmatched media are reported

---

## Success Criteria

✅ Media imported from Access CSV are automatically assigned to locations
✅ Assignment works regardless of import order (media first or locations first)
✅ User is warned if importing media without locations
✅ Manual assignment tool available for fixing unassigned media
✅ Assignment results are clearly reported to user
✅ Box and Place fields are stored in media for reference
✅ All existing tests still pass
✅ New tests cover assignment scenarios

---

## Migration Strategy

### Database Migration
- Add `box TEXT` and `place TEXT` columns to media table
- Existing media will have NULL values (acceptable)
- Future imports will populate these fields

### Backward Compatibility
- New fields are optional
- Existing functionality continues to work
- Location assignment is enhancement, not requirement

---

## Timeline

This is a medium-complexity change affecting multiple layers:

### Estimated Breakdown
- Add box/place fields to model and schema: 30 minutes
- Update repository and service: 30 minutes
- Implement location assignment logic: 45 minutes
- Update import process: 30 minutes
- Add user guidance and dialogs: 45 minutes
- Add manual assignment tool: 30 minutes
- Testing: 45 minutes
- Documentation: 30 minutes

**Note**: Time estimates are provided for planning purposes only.

---

## Alternative: Simpler Approach

If adding fields to Media model is too complex, we can use a simpler approach:

### Simplified Phase 6d

1. **Import Order Enforcement**:
   - Check if locations exist before allowing media import
   - Show warning: "Please import locations first"
   - Don't allow media import until locations exist

2. **Improved Matching**:
   - During media import, match against existing locations
   - Show results: "X matched, Y not found"
   - List unmatched media for user review

3. **No Model Changes**:
   - Don't add box/place fields
   - Rely on import-time matching only
   - Accept that post-import assignment isn't possible

This is simpler but less flexible. Users must import in correct order.

---

## Recommendation

**Implement Full Phase 6d** with box/place fields in Media model.

**Rationale**:
- Provides best user experience
- Allows flexible import order
- Enables post-import fixes
- Stores useful reference data
- Future-proof for other features

**Alternative**: If time is limited, implement Simplified Phase 6d first, then enhance later.
