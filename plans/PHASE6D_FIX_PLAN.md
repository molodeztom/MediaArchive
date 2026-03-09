# Phase 6d Fix Plan: Correct Location Assignment Logic

## Problem Analysis

The current implementation misunderstands the relationship between media and locations:

### Current (Wrong) Approach
- Stores box and place from media CSV as separate fields in media table
- Tries to match by box+place combination
- Doesn't properly link media to locations via foreign key

### Correct Approach Needed
1. **Media CSV Structure**: Box (integer ID reference), Position (string)
2. **Location CSV Structure**: Box (integer ID), Ort (place), Typ (detail)
3. **Relationship**: Media.Box → Location.Box (foreign key relationship)

## Solution

### Step 1: Update Access CSV Mapper
- When parsing media CSV, store Box integer as temporary location_id
- Store Position string in media.place field
- Don't store box as a separate field - it's just a reference

### Step 2: Update Location Assignment Logic
- After locations are imported, they get database IDs (1, 2, 3, ...)
- Need to map: Location.box (from CSV) → Location.id (database ID)
- Then update media: where media.location_id == box_number, set to actual location.id

### Step 3: Update UI Display
- In media tab, show:
  - Position from media.place
  - Box from location.box (via foreign key join)
- Add double-click handler to jump to location in locations tab

## Implementation Steps

1. **Modify AccessCSVMapper.parse_media_row()**:
   - Store Box integer directly as location_id (temporary reference)
   - Store Position as place field
   - Remove box field storage

2. **Update MediaService.assign_locations_by_box_place()**:
   - Get all media with location_id set (these are temporary box numbers)
   - Get all locations
   - Create mapping: location.box → location.id
   - Update media: set location_id = location_map[old_location_id]

3. **Update Main Window Media Display**:
   - Join with location table to show Box from location
   - Show Position from media.place
   - Add double-click handler

## Key Insight

The box number in media CSV is NOT a field to store - it's a REFERENCE to a location. The proper flow is:

1. Import media: store box number as temporary location_id
2. Import locations: locations get real database IDs
3. Assignment: map box numbers to real location IDs
4. Display: show location.box via foreign key join
