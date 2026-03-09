# Phase 6c: Import Dialog Improvements

## Overview
Enhance the import dialog with better field naming, improved defaults for Access format, and better preview visibility.

## Requirements

### 1. Add "Number" Field for Physical Media Identifier
- **Current**: Access CSV "ID" column is not stored
- **New**: Store Access "ID" column as "Number" field in media
- **Purpose**: Track physical media number/identifier
- **Display**: Show in media list and dialogs

### 2. Rename "type" Field to "category"
- **Current**: Field named "type" (confusing with "media_type")
- **New**: Rename to "category" for clarity
- **Reason**: Avoid confusion between content category and storage media type
- **Examples**: Archive, Program, Backup, Game, Image, Lexica

### 3. Set Access Format as Default
- **Current**: Standard format is default
- **New**: Access format should be default
- **Reason**: Primary use case is importing from Access database

### 4. Set Semicolon as Default Delimiter
- **Current**: Comma is default
- **New**: Semicolon should be default
- **Reason**: Access exports use semicolon delimiter

### 5. Improve Preview Visibility
- **Option A**: Make dialog resizable by user
- **Option B**: Increase preview height while keeping buttons visible
- **Recommendation**: Make dialog resizable (more flexible)

---

## Implementation Plan

### Step 1: Database Schema Changes

#### Add "number" field to media table
- **File**: [`src/data/schema.py`](../src/data/schema.py)
- **Action**: Add `number TEXT` column to media table
- **Index**: Add index on number field for quick lookup
- **Migration**: Existing records will have NULL number

```sql
ALTER TABLE media ADD COLUMN number TEXT;
CREATE INDEX IF NOT EXISTS idx_media_number ON media(number);
```

### Step 2: Model Changes

#### Update Media model
- **File**: [`src/models/media.py`](../src/models/media.py)
- **Changes**:
  - Add `number: Optional[str] = None` field
  - Rename `type` to `category`
  - Update docstrings
  - Update `__str__` and `__repr__` methods

#### Update all references to Media.type
- Search for all uses of `media.type` in codebase
- Replace with `media.category`
- Files likely affected:
  - [`src/business/media_service.py`](../src/business/media_service.py)
  - [`src/data/media_repository.py`](../src/data/media_repository.py)
  - [`src/gui/dialogs.py`](../src/gui/dialogs.py)
  - [`src/gui/main_window.py`](../src/gui/main_window.py)
  - All test files

### Step 3: Access CSV Mapper Changes

#### Update AccessCSVMapper
- **File**: [`src/business/access_csv_mapper.py`](../src/business/access_csv_mapper.py)
- **Changes**:
  - Store Access "ID" column in `number` field
  - Rename `type_value` to `category_value`
  - Update `AccessContentTypeMapper` to `AccessCategoryMapper`
  - Update method name: `map_content_type()` → `map_category()`
  - Update all references to `type` → `category`

#### Update column mapping
```python
COLUMN_MAPPING = {
    "id": 0,           # Now stored as "number"
    "name": 1,
    "company": 2,
    "box": 3,
    "place": 4,
    "license_code": 5,
    "category": 6,     # Was "media_type", now "category"
    "content_description": 7,
    "creation_date": 8,
    "valid_until_date": 9,
}
```

### Step 4: Import Dialog Changes

#### Update ImportDialog defaults
- **File**: [`src/gui/import_dialog.py`](../src/gui/import_dialog.py)
- **Changes**:
  - Set `csv_format` default to "access"
  - Set `delimiter_var` default to ";"
  - Make dialog resizable: `self.resizable(True, True)`
  - Increase preview tree height from 8 to 15 rows
  - Set minimum size to ensure buttons remain visible
  - Update preview to show more columns if needed

#### Dialog sizing
```python
# Current
self.geometry("650x550")
self.minsize(650, 550)
self.resizable(False, False)

# New
self.geometry("750x700")
self.minsize(750, 600)
self.resizable(True, True)
```

#### Preview tree
```python
# Current
self.preview_tree = ttk.Treeview(preview_frame, columns=columns, height=8)

# New
self.preview_tree = ttk.Treeview(preview_frame, columns=columns, height=15)
```

### Step 5: Dialog Changes

#### Update AddMediaDialog
- **File**: [`src/gui/dialogs.py`](../src/gui/dialogs.py)
- **Changes**:
  - Add "Number" field (optional text entry)
  - Rename "Type" label to "Category"
  - Update field references from `type` to `category`
  - Update validation and save logic

#### Update EditMediaDialog
- **File**: [`src/gui/dialogs.py`](../src/gui/dialogs.py)
- **Changes**:
  - Add "Number" field (optional text entry)
  - Rename "Type" label to "Category"
  - Update field references from `type` to `category`
  - Pre-populate number field if present

### Step 6: Service Layer Changes

#### Update MediaService
- **File**: [`src/business/media_service.py`](../src/business/media_service.py)
- **Changes**:
  - Add `number` parameter to `create_media()` method
  - Add `number` parameter to `update_media()` method
  - Update all method signatures

#### Update LocationService
- **File**: [`src/business/location_service.py`](../src/business/location_service.py)
- **Changes**: None needed (no type field in locations)

### Step 7: Repository Layer Changes

#### Update MediaRepository
- **File**: [`src/data/media_repository.py`](../src/data/media_repository.py)
- **Changes**:
  - Add `number` column to INSERT statements
  - Add `number` column to UPDATE statements
  - Add `number` column to SELECT statements
  - Update all SQL queries

### Step 8: Main Window Changes

#### Update MainWindow
- **File**: [`src/gui/main_window.py`](../src/gui/main_window.py)
- **Changes**:
  - Update media tree columns to include "Number"
  - Update `_on_media_added()` to pass `number` parameter
  - Update `_on_media_updated()` to pass `number` parameter
  - Update `_process_import()` to handle `number` field
  - Update all references from `type` to `category`

### Step 9: Test Updates

#### Update all test files
- **Files**:
  - [`tests/test_phase6a_access_mapper.py`](../tests/test_phase6a_access_mapper.py)
  - [`tests/test_phase6_real_csv_import.py`](../tests/test_phase6_real_csv_import.py)
  - [`tests/test_phase3_business.py`](../tests/test_phase3_business.py)
  - [`tests/test_phase4_dialogs.py`](../tests/test_phase4_dialogs.py)
  - All other test files using Media model
- **Changes**:
  - Rename `AccessContentTypeMapper` to `AccessCategoryMapper`
  - Update method calls: `map_content_type()` → `map_category()`
  - Update all references from `media.type` to `media.category`
  - Add tests for `number` field
  - Update assertions to check `number` field

### Step 10: Documentation Updates

#### Update CSV_TO_DB_MAPPING.md
- **File**: [`docs/CSV_TO_DB_MAPPING.md`](../docs/CSV_TO_DB_MAPPING.md)
- **Changes**:
  - Update Access CSV mapping to show ID → number
  - Rename "type" to "category" throughout
  - Update examples with number field
  - Update terminology section

#### Update other documentation
- **Files**:
  - [`docs/DATA_MODEL.md`](../docs/DATA_MODEL.md)
  - [`docs/MIGRATION_FROM_ACCESS.md`](../docs/MIGRATION_FROM_ACCESS.md)
- **Changes**:
  - Update field descriptions
  - Update examples
  - Update terminology

---

## Detailed Changes by File

### Database Schema ([`src/data/schema.py`](../src/data/schema.py))

```python
MEDIA_TABLE = """
CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number TEXT,                              # NEW: Physical media number
    content_description TEXT,
    remarks TEXT,
    creation_date DATE,
    valid_until_date DATE,
    media_type TEXT,
    category TEXT,                            # RENAMED: Was "type"
    company TEXT,
    license_code TEXT,
    location_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES storage_location(id) ON DELETE SET NULL
);
"""

MEDIA_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_media_name ON media(name);",
    "CREATE INDEX IF NOT EXISTS idx_media_number ON media(number);",  # NEW
    "CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type);",
    "CREATE INDEX IF NOT EXISTS idx_media_category ON media(category);",  # RENAMED
    "CREATE INDEX IF NOT EXISTS idx_media_location ON media(location_id);",
    "CREATE INDEX IF NOT EXISTS idx_media_valid_until ON media(valid_until_date);",
    "CREATE INDEX IF NOT EXISTS idx_media_creation_date ON media(creation_date);",
]
```

### Media Model ([`src/models/media.py`](../src/models/media.py))

```python
@dataclass
class Media:
    """Represents a physical media item.
    
    Attributes:
        name: Media name/title (required).
        number: Physical media number/identifier (optional).
        media_type: Physical storage medium (DVD, CD, USB-Stick, etc.).
        category: Content category (Archive, Program, Backup, Game, etc.).
        content_description: Description of contents.
        remarks: Additional notes.
        creation_date: When media was created.
        valid_until_date: Expiration date (if applicable).
        company: Company/publisher name.
        license_code: License key or activation code.
        location_id: Reference to storage location.
        id: Unique identifier (None for new records).
        created_at: ISO 8601 timestamp when record was created.
        updated_at: ISO 8601 timestamp when record was last updated.
    """

    name: str
    number: Optional[str] = None              # NEW
    media_type: Optional[str] = None
    category: Optional[str] = None            # RENAMED from "type"
    content_description: Optional[str] = None
    remarks: Optional[str] = None
    creation_date: Optional[date] = None
    valid_until_date: Optional[date] = None
    company: Optional[str] = None
    license_code: Optional[str] = None
    location_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

### Access CSV Mapper ([`src/business/access_csv_mapper.py`](../src/business/access_csv_mapper.py))

```python
class AccessCategoryMapper:  # RENAMED from AccessContentTypeMapper
    """Maps Access content categories (Art field) to Media Archive categories."""
    
    CATEGORY_MAPPING = {  # RENAMED from CONTENT_TYPE_MAPPING
        "Archive": "Archive",
        "Image": "Image",
        "Lexica": "Lexica",
        "Program": "Program",
        "Backup": "Backup",
        "Game": "Game",
    }
    
    @staticmethod
    def map_category(access_category: str) -> Optional[str]:  # RENAMED
        """Map Access category (Art field) to Media Archive category."""
        # Implementation...

class AccessCSVMapper:
    COLUMN_MAPPING = {
        "id": 0,           # Now stored as "number"
        "name": 1,
        "company": 2,
        "box": 3,
        "place": 4,
        "license_code": 5,
        "category": 6,     # RENAMED from "media_type"
        "content_description": 7,
        "creation_date": 8,
        "valid_until_date": 9,
    }
    
    @staticmethod
    def parse_media_row(row, locations, external_id_map=None):
        # Extract fields
        external_id_str = row[COLUMN_MAPPING["id"]].strip()
        number = external_id_str if external_id_str else None  # NEW: Store as number
        
        access_art = row[COLUMN_MAPPING["category"]].strip()
        category_value = access_art if access_art else None  # RENAMED
        
        # Create media object
        media = Media(
            name=name,
            number=number,                    # NEW
            media_type="Unknown",
            category=category_value,          # RENAMED from type
            # ... other fields
        )
```

### Import Dialog ([`src/gui/import_dialog.py`](../src/gui/import_dialog.py))

```python
class ImportDialog(tk.Toplevel):
    def __init__(self, parent, on_import=None, locations=None):
        super().__init__(parent)
        self.title("Import Data")
        self.resizable(True, True)  # CHANGED: Make resizable
        self.result = None
        self.on_import = on_import
        self.imported_data = []
        self.import_type = "media"
        self.csv_format = "access"  # CHANGED: Default to access
        self.locations = locations or []
        
        # ... rest of init
    
    def _create_ui(self):
        # ... existing code ...
        
        # CSV Format frame
        self.format_var = tk.StringVar(value="access")  # CHANGED: Default to access
        
        # Delimiter selection
        self.delimiter_var = tk.StringVar(value=";")  # CHANGED: Default to semicolon
        
        # Preview tree
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, height=15)  # CHANGED: Increased height
        
        # Set dialog size
        self.geometry("750x700")  # CHANGED: Larger size
        self.minsize(750, 600)    # CHANGED: Larger minimum
```

### Media Dialogs ([`src/gui/dialogs.py`](../src/gui/dialogs.py))

```python
class AddMediaDialog(BaseDialog):
    def _create_form(self):
        # ... existing fields ...
        
        # Number field (NEW)
        ttk.Label(form_frame, text="Number:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.number_var, width=30).grid(
            row=row, column=1, sticky=tk.W, pady=5
        )
        row += 1
        
        # Category field (RENAMED from Type)
        ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()  # RENAMED from type_var
        ttk.Entry(form_frame, textvariable=self.category_var, width=30).grid(
            row=row, column=1, sticky=tk.W, pady=5
        )
        row += 1
        
        # ... rest of fields ...
    
    def _save(self):
        # ... validation ...
        
        media = Media(
            name=name,
            number=self.number_var.get() or None,  # NEW
            media_type=media_type,
            category=self.category_var.get() or None,  # RENAMED
            # ... other fields ...
        )
```

### Main Window ([`src/gui/main_window.py`](../src/gui/main_window.py))

```python
class MainWindow:
    def _create_media_tab(self):
        # Update columns to include Number
        columns = ("ID", "Number", "Name", "Type", "Category", "Location", "Expires")  # NEW: Number, Category
        self.media_tree = ttk.Treeview(frame, columns=columns, height=20)
        
        # Configure columns
        self.media_tree.column("Number", anchor=tk.W, width=80)  # NEW
        self.media_tree.column("Category", anchor=tk.W, width=100)  # NEW
        
        # ... rest of configuration ...
    
    def _refresh_media_list(self):
        for media in media_list:
            self.media_tree.insert("", tk.END, values=(
                media.id,
                media.number or "",  # NEW
                media.name,
                media.media_type,
                media.category or "",  # RENAMED
                media.location_id or "N/A",
                expires
            ))
    
    def _on_media_added(self, media):
        created = self.media_service.create_media(
            name=media.name,
            number=media.number,  # NEW
            media_type=media.media_type,
            category=media.category,  # RENAMED
            # ... other fields ...
        )
```

---

## Testing Plan

### Unit Tests

#### Test number field
- Test creating media with number
- Test updating media number
- Test searching by number
- Test number field in import/export

#### Test category field
- Test all existing type tests with new category name
- Verify category mapping works correctly
- Test category filtering

#### Test import dialog
- Test Access format as default
- Test semicolon as default delimiter
- Test resizable dialog
- Test preview with 15 rows

### Integration Tests

#### Test full import workflow
- Import locations with empty Ort/Typ
- Import media with number field
- Verify number is stored correctly
- Verify category is stored correctly
- Verify location mapping works

#### Test UI workflow
- Add media with number and category
- Edit media with number and category
- Display media with number and category
- Search/filter by category

---

## Migration Strategy

### Database Migration

Since this is a local desktop application with SQLite:

1. **Option A: Automatic Migration**
   - Add migration code to check if `number` column exists
   - If not, run ALTER TABLE to add it
   - Run on application startup

2. **Option B: Manual Migration**
   - Provide migration script
   - User runs script before upgrading
   - Document in release notes

**Recommendation**: Option A (automatic migration)

### Migration Code

```python
# In src/data/database.py
def migrate_schema(self):
    """Apply schema migrations."""
    cursor = self.conn.cursor()
    
    # Check if number column exists
    cursor.execute("PRAGMA table_info(media)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "number" not in columns:
        logger.info("Migrating schema: Adding number column to media table")
        cursor.execute("ALTER TABLE media ADD COLUMN number TEXT")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_number ON media(number)")
        self.conn.commit()
    
    # Check if category column exists (renamed from type)
    if "category" not in columns and "type" in columns:
        logger.info("Migrating schema: Renaming type column to category")
        # SQLite doesn't support RENAME COLUMN directly in older versions
        # Need to create new table and copy data
        # ... migration logic ...
```

---

## File Changes Summary

### Files to Modify

| File | Changes | Complexity |
|------|---------|------------|
| [`src/data/schema.py`](../src/data/schema.py) | Add number field, rename type to category | Low |
| [`src/models/media.py`](../src/models/media.py) | Add number field, rename type to category | Low |
| [`src/business/access_csv_mapper.py`](../src/business/access_csv_mapper.py) | Store ID as number, rename type to category | Medium |
| [`src/business/media_service.py`](../src/business/media_service.py) | Add number parameter, rename type to category | Medium |
| [`src/data/media_repository.py`](../src/data/media_repository.py) | Add number column, rename type to category | Medium |
| [`src/gui/import_dialog.py`](../src/gui/import_dialog.py) | Change defaults, make resizable, increase preview | Low |
| [`src/gui/dialogs.py`](../src/gui/dialogs.py) | Add number field, rename type to category | Medium |
| [`src/gui/main_window.py`](../src/gui/main_window.py) | Add number column, rename type to category | Medium |
| [`tests/test_phase6a_access_mapper.py`](../tests/test_phase6a_access_mapper.py) | Rename class, update tests | Low |
| [`tests/test_phase6_real_csv_import.py`](../tests/test_phase6_real_csv_import.py) | Update tests for new fields | Low |
| [`tests/test_phase3_business.py`](../tests/test_phase3_business.py) | Update tests for new fields | Low |
| [`tests/test_phase4_dialogs.py`](../tests/test_phase4_dialogs.py) | Update tests for new fields | Low |
| [`docs/CSV_TO_DB_MAPPING.md`](../docs/CSV_TO_DB_MAPPING.md) | Update mapping documentation | Low |
| [`docs/DATA_MODEL.md`](../docs/DATA_MODEL.md) | Update model documentation | Low |

### Files to Create

| File | Purpose |
|------|---------|
| [`src/data/migrations.py`](../src/data/migrations.py) | Database migration utilities |

---

## Implementation Order

### Phase 1: Database and Model Changes
1. Add migration utility
2. Update schema with number field
3. Rename type to category in schema
4. Update Media model
5. Run tests to identify all affected code

### Phase 2: Repository and Service Changes
6. Update MediaRepository with number and category
7. Update MediaService with number and category
8. Update all method signatures
9. Run business logic tests

### Phase 3: Mapper Changes
10. Rename AccessContentTypeMapper to AccessCategoryMapper
11. Update parse_media_row to store ID as number
12. Update all references to type → category
13. Run mapper tests

### Phase 4: GUI Changes
14. Update import dialog defaults and sizing
15. Update AddMediaDialog with number field
16. Update EditMediaDialog with number field
17. Update MainWindow media tree columns
18. Run dialog tests

### Phase 5: Testing and Documentation
19. Update all test files
20. Run full test suite
21. Update documentation
22. Manual testing of import workflow

---

## Risks and Considerations

### Breaking Changes
- **Database schema change**: Requires migration
- **API changes**: All code using Media.type must be updated
- **Test updates**: All tests using Media.type must be updated

### Backward Compatibility
- Existing databases will need migration
- Existing CSV exports may not have number field
- Consider adding version check

### User Impact
- Users will see new "Number" field in dialogs
- "Type" label changes to "Category"
- Import dialog looks different (larger, resizable)
- Access format is now default

---

## Success Criteria

### Functional Requirements
- ✅ Number field is stored and displayed
- ✅ Category field replaces type field
- ✅ Access format is default
- ✅ Semicolon is default delimiter
- ✅ Import dialog is resizable
- ✅ Preview shows 15 rows
- ✅ Buttons remain visible when resizing

### Technical Requirements
- ✅ All tests pass
- ✅ Database migration works
- ✅ No data loss during migration
- ✅ Import/export works with new fields
- ✅ Documentation is updated

### User Experience
- ✅ Dialog is easier to use
- ✅ Field names are clearer
- ✅ More data visible in preview
- ✅ Default settings match common use case

---

## Timeline

This is a medium-complexity change affecting multiple layers:

### Estimated Breakdown
- Database and model changes: 30 minutes
- Repository and service changes: 45 minutes
- Mapper changes: 30 minutes
- GUI changes: 60 minutes
- Test updates: 45 minutes
- Documentation: 30 minutes
- Testing and verification: 30 minutes

**Note**: Time estimates are provided for planning purposes only and may vary based on actual implementation complexity.

---

## Next Steps

1. Review this plan with stakeholders
2. Confirm field naming (number, category)
3. Confirm dialog sizing preferences
4. Begin implementation in Code mode
5. Test thoroughly with real Access CSV files
