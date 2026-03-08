# Migration Guide: From Microsoft Access to Media Archive Manager

## Overview

This guide explains how to export data from your existing Microsoft Access database and import it into the Media Archive Manager application.

**Important Note for German/European Users:** If you use comma as decimal separator in your region, use semicolon-delimited files instead of comma-delimited files. See the detailed instructions below.

## Prerequisites

- Microsoft Access installed (any version)
- Media Archive Manager application installed
- Your existing Access database file

## Migration Process

### Step 1: Export Data from Microsoft Access

#### Option A: Export to Semicolon-Delimited CSV (Recommended for German/European Locales)

**Why Semicolon?** In German and many European locales, the comma is used as a decimal separator (e.g., 3,14). Using semicolon as the field delimiter avoids conflicts.

1. **Open your Access database**
   - Launch Microsoft Access
   - Open your existing media database

2. **Export Media Table**
   - Select the media table in the navigation pane
   - Click "External Data" tab
   - Click "Text File" in the Export group
   - Choose a save location (e.g., `media_export.csv`)
   - Click "OK"
   - In the Export Text Wizard:
     - Select "Delimited" format
     - Click "Next"
     - Choose "Other" and enter semicolon (;) as delimiter
     - Check "Include Field Names on First Row"
     - Set "Text Qualifier" to double quote (")
     - Click "Next"
     - Click "Finish"
   - Close the wizard

3. **Export Locations Table** (if you have one)
   - Repeat the same process for your locations table
   - Save as `locations_export.csv`

#### Option B: Export via Excel (Alternative Method)

If the Access export wizard doesn't work well:

1. **Export to Excel First**
   - In Access, select your table
   - Click "External Data" → "Excel"
   - Export to Excel file

2. **Save as CSV from Excel**
   - Open the Excel file
   - Click "File" → "Save As"
   - Choose "CSV UTF-8 (Comma delimited) (*.csv)" format
   - **Important:** If using German locale, Excel will automatically use semicolon
   - Save the file

3. **Verify Delimiter**
   - Open the CSV file in Notepad
   - Check if fields are separated by semicolon (;) or comma (,)
   - Note which delimiter is used for the import step

#### Option B: Export via Query

If your data needs transformation:

1. **Create an Export Query**
   ```sql
   SELECT 
       MediaName AS Name,
       MediaType AS [Media Type],
       Company,
       LicenseCode AS [License Code],
       Format(CreationDate, "yyyy-mm-dd") AS [Creation Date],
       Format(ValidUntilDate, "yyyy-mm-dd") AS [Valid Until Date],
       ContentDescription AS [Content Description],
       Remarks,
       LocationID AS [Location ID]
   FROM MediaTable
   ORDER BY MediaName;
   ```

2. **Run and Export Query**
   - Run the query to verify results
   - Right-click the query → Export → Text File
   - Follow the same CSV export steps as above

### Step 2: Prepare CSV Files

#### Media CSV Format

Your CSV file should have these columns (in this order):

**With Semicolon Delimiter (German/European Locale):**
```
Name;Media Type;Company;License Code;Creation Date;Valid Until Date;Content Description;Remarks;Location ID
```

**Example (Semicolon-delimited):**
```csv
Name;Media Type;Company;License Code;Creation Date;Valid Until Date;Content Description;Remarks;Location ID
Windows 10 Pro;DVD;Microsoft;XXXXX-XXXXX-XXXXX;2020-01-15;2025-01-15;Operating System Installation;Original retail version;1
Adobe Photoshop CS6;DVD;Adobe;1234-5678-9012;2019-06-20;2024-06-20;Photo editing software;Extended version;2
```

**With Comma Delimiter (US/International Locale):**
```
Name,Media Type,Company,License Code,Creation Date,Valid Until Date,Content Description,Remarks,Location ID
```

**Example (Comma-delimited):**
```csv
Name,Media Type,Company,License Code,Creation Date,Valid Until Date,Content Description,Remarks,Location ID
Windows 10 Pro,DVD,Microsoft,XXXXX-XXXXX-XXXXX,2020-01-15,2025-01-15,Operating System Installation,Original retail version,1
Adobe Photoshop CS6,DVD,Adobe,1234-5678-9012,2019-06-20,2024-06-20,Photo editing software,Extended version,2
```

**Field Requirements:**
- **Name** (required): Media item name
- **Media Type** (required): One of: DVD, Blu-ray, CD, USB-Stick, External-HDD, SD-Card, Other
- **Company** (optional): Publisher/manufacturer name
- **License Code** (optional): Product key or license code
- **Creation Date** (optional): Format YYYY-MM-DD
- **Valid Until Date** (optional): Format YYYY-MM-DD
- **Content Description** (optional): Description of contents
- **Remarks** (optional): Additional notes
- **Location ID** (optional): Reference to storage location

#### Locations CSV Format

Your CSV file should have these columns:

**With Semicolon Delimiter (German/European Locale):**
```
Box;Place;Detail
```

**Example (Semicolon-delimited):**
```csv
Box;Place;Detail
Box 1;Shelf A;Top shelf in office
Box 2;Shelf B;Middle shelf in office
Drawer 1;Desk;Top drawer
```

**With Comma Delimiter (US/International Locale):**
```
Box,Place,Detail
```

**Example (Comma-delimited):**
```csv
Box,Place,Detail
Box 1,Shelf A,Top shelf in office
Box 2,Shelf B,Middle shelf in office
Drawer 1,Desk,Top drawer
```

**Field Requirements:**
- **Box** (required): Container or box identifier
- **Place** (required): Physical location
- **Detail** (optional): Additional location details

### Step 3: Clean and Validate Data

Before importing, review your CSV files:

1. **Check Media Types**
   - Ensure all media types match the allowed values:
     - DVD
     - Blu-ray
     - CD
     - USB-Stick
     - External-HDD
     - SD-Card
     - Other

2. **Check Date Formats**
   - All dates must be in YYYY-MM-DD format
   - Example: 2024-03-07 (not 03/07/2024 or 7.3.2024)

3. **Check Location IDs**
   - If using location IDs, ensure they match your locations
   - Or leave empty and assign locations later in the application

4. **Remove Invalid Characters**
   - Check for special characters that might cause issues
   - Ensure proper UTF-8 encoding for international characters

## Step 4: Import into Media Archive Manager

### Phase 6a/6b: Custom Access CSV Import

The Media Archive Manager now includes specialized support for importing data from Microsoft Access databases with automatic field mapping, type conversion, and location management.

#### Import Locations First

1. **Launch Media Archive Manager**
   - Start the application

2. **Open Import Dialog**
   - Click File → Import
   - Or press Ctrl+I

3. **Select Locations File**
   - Click "Browse" button
   - Select your `location_export.csv` file (from Access export)

4. **Configure Import Options**
   - Select "Storage Locations" as import type
   - **Select Delimiter**: Choose "Semicolon (;)" for German/European CSV
   - Check "Skip header row" (if your CSV has headers)
   - Check "Validate data" (recommended)

5. **Location CSV Format**
   - The system expects: `Box;Ort;Typ` (or `Box;Place;Detail`)
   - **Box**: Visible box number for physical reference (e.g., "1", "2", "Box 1")
   - **Ort/Place**: Storage location (e.g., "Regal A", "Shelf A")
   - **Typ/Detail**: Optional type or detail (e.g., "Oben", "Top shelf")

6. **Preview and Import**
   - Review the preview to ensure data looks correct
   - Click "Import" button
   - Confirm the import when prompted
   - Note the number of successfully imported locations
   - Internal reference IDs are automatically generated

#### Import Media Items

1. **Open Import Dialog**
   - Click File → Import
   - Or press Ctrl+I

2. **Select Media File**
   - Click "Browse" button
   - Select your `media_export.csv` file (from Access export)

3. **Configure Import Options**
   - Select "Media Items" as import type
   - **Select Delimiter**: Choose "Semicolon (;)" for German/European CSV
   - Check "Skip header row" (if your CSV has headers)
   - Check "Validate data" (recommended)

4. **Media CSV Format**
   - The system expects: `ID;Name;Firma;Box;Position;Code;Art;Bemerkung;Datum;Verfällt am`
   - **ID**: Unique identifier (imported but not used as primary key)
   - **Name**: Media name (required)
   - **Firma**: Company/Publisher
   - **Box**: Storage box number (must match location Box)
   - **Position**: Storage position (must match location Ort/Place)
   - **Code**: License code or product key
   - **Art**: Media type (Archive, Image, Lexica, Program, Backup, Game, Other)
   - **Bemerkung**: Content description
   - **Datum**: Creation date (DD.MM.YYYY format)
   - **Verfällt am**: Expiration date (DD.MM.YYYY format)

5. **Automatic Field Mapping**
   - Media types are automatically mapped:
     - Archive → DVD
     - Image → DVD
     - Lexica → DVD
     - Program → DVD
     - Backup → External-HDD
     - Game → DVD
     - Other → Other
   - Dates are automatically converted from DD.MM.YYYY to ISO format
   - Locations are automatically looked up by Box + Position match

6. **Preview and Import**
   - Review the preview to ensure data looks correct
   - Click "Import" button
   - Confirm the import when prompted
   - Note any errors or warnings
   - Successfully imported items will be added to the database
   - Media items are automatically linked to locations

### Step 5: Verify Import

1. **Check Media Tab**
   - Switch to the "Media" tab
   - Verify all media items are listed
   - Check that data appears correctly

2. **Check Locations Tab**
   - Switch to the "Locations" tab
   - Verify all locations are listed
   - Check media count for each location

3. **Test Search**
   - Switch to "Search" tab
   - Try searching for specific media items
   - Test filtering by type and location

4. **Review Expired Media**
   - Click View → Show Expired Media
   - Or press Ctrl+X
   - Verify expired items are highlighted correctly

### Step 6: Backup Your Data

After successful import:

1. **Create Backup**
   - Click File → Backup Database
   - Choose a backup location
   - Backup file will be created with timestamp

2. **Verify Backup**
   - Check that backup file exists
   - Note the backup location for future reference

## Best Practices

### Data Preparation

1. **Clean Data in Access First**
   - Remove duplicate entries
   - Standardize media type names
   - Fix date formats
   - Remove invalid characters

2. **Export in Batches**
   - For large databases, export in smaller batches
   - Test with a small sample first
   - Import in stages to identify issues early

3. **Use Consistent Naming**
   - Standardize company names (e.g., "Microsoft" not "MS" or "MSFT")
   - Use consistent media type names
   - Standardize location names

### Import Strategy

1. **Import Locations First**
   - Always import locations before media
   - This ensures location IDs are available for media items

2. **Test Import**
   - Start with a small test file (5-10 records)
   - Verify import works correctly
   - Then import full dataset

3. **Handle Errors**
   - Review error messages carefully
   - Fix issues in CSV file
   - Re-import corrected data

4. **Incremental Import**
   - Import in stages if you have a large dataset
   - Verify each batch before continuing

## Common Issues and Solutions

### Issue: "Invalid media type"

**Solution:** Media types are automatically mapped from Access types:
- Archive → DVD
- Image → DVD
- Lexica → DVD
- Program → DVD
- Backup → External-HDD
- Game → DVD
- Other → Other (for unknown types)

If you see an error, check that your Art column contains one of these values.

### Issue: "Invalid date format"

**Solution:** Ensure dates are in DD.MM.YYYY format (German format):
- Correct: 07.03.2024 or 07.03.2024 14:30
- Incorrect: 2024-03-07, 03/07/2024, 7.3.2024

The system automatically converts DD.MM.YYYY to ISO format (YYYY-MM-DD).

### Issue: "Location not found" or "Media not linked to location"

**Solution:**
- Ensure locations were imported first
- Check that Box and Position values in media CSV exactly match Box and Ort values in locations CSV
- Box values must match exactly (e.g., "1" must match "1", not "Box 1")
- Position/Ort values must match exactly (e.g., "Regal A" must match "Regal A")
- If locations don't match, media will be imported but not linked to a location

### Issue: "Name is required"

**Solution:**
- Ensure every media item has a name in the Name column
- Check for empty rows in CSV
- Remove blank lines from CSV file

### Issue: Special characters display incorrectly

**Solution:**
- Save CSV file with UTF-8 encoding
- In Excel: Save As → CSV UTF-8 (Semicolon delimited)
- In Access: Ensure Unicode compression is off

### Issue: "Fields not recognized correctly" or "Data appears in wrong columns"

**Solution:** You selected the wrong delimiter
- If your CSV uses semicolon (;) as separator, select "Semicolon (;)" in the import dialog
- If your CSV uses comma (,) as separator, select "Comma (,)" in the import dialog
- **For German/European users:** Most CSV exports from Access or Excel will use semicolon (;) as delimiter
- **For US/International users:** Most CSV exports will use comma (,) as delimiter
- Check your CSV file in Notepad to see which delimiter is used

### Issue: "Comma appears in data fields"

**Solution:** This is why semicolon delimiter is recommended for German/European locales
- If you have data like "3,14" (three point fourteen), using comma as delimiter will split this incorrectly
- Use semicolon (;) as delimiter instead
- Re-export your CSV with semicolon delimiter from Access or Excel

### Issue: "Box number not visible" or "Can't find physical box"

**Solution:** The system maintains visible box numbers for physical reference
- Box numbers from your CSV are preserved and displayed
- You can use these numbers to locate physical boxes
- Internal reference IDs are generated automatically but not shown to users
- This design allows clean database relationships while maintaining user-friendly box references

### Issue: Media imported but not linked to locations

**Solution:** Location matching failed
- Check that Box values in media CSV match Box values in locations CSV exactly
- Check that Position values in media CSV match Ort values in locations CSV exactly
- Example:
  - Media CSV: Box="1", Position="Regal A"
  - Locations CSV: Box="1", Ort="Regal A" ✓ (will match)
  - Locations CSV: Box="Box 1", Ort="Regal A" ✗ (won't match)
- If no match is found, media is still imported but without location reference
- You can manually assign locations later in the application

## Alternative Migration Methods

### Method 1: Manual Entry

For small databases (< 50 items):
- Use the application's Add Media dialog
- Manually enter each item
- Ensures data quality
- Time-consuming but thorough

### Method 2: Direct Database Migration

For advanced users:
- Export Access database to SQLite format
- Use database tools to transform schema
- Import directly into Media Archive database
- Requires technical knowledge

### Method 3: Custom Script

For complex migrations:
- Write a Python script to read Access database
- Transform data to match Media Archive schema
- Use the application's import functionality
- Requires programming knowledge

## Post-Migration Tasks

1. **Verify Data Integrity**
   - Check all media items imported correctly
   - Verify locations are assigned properly
   - Test search and filter functionality

2. **Update Expired Dates**
   - Review expired media
   - Update expiration dates if needed
   - Remove obsolete items

3. **Organize Locations**
   - Review location assignments
   - Update location details if needed
   - Consolidate duplicate locations

4. **Create Regular Backups**
   - Set up a backup schedule
   - Store backups in a safe location
   - Test backup restoration

## Support

If you encounter issues during migration:

1. Check the error messages in the import dialog
2. Review this guide for common solutions
3. Verify your CSV file format matches the specifications
4. Test with a small sample file first
5. Check the application logs for detailed error information

## Summary

**Recommended Migration Path:**

1. Export locations from Access to CSV
2. Export media from Access to CSV
3. Clean and validate CSV files
4. Import locations into Media Archive Manager
5. Import media into Media Archive Manager
6. Verify import success
7. Create backup

This approach ensures a smooth migration with minimal data loss and provides a clear audit trail of the migration process.
