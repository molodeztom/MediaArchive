# Portable Distribution Guide

## Overview

This guide explains how to build, test, and distribute the Media Archive Manager as a portable Windows application.

## What is a Portable Distribution?

A portable distribution is a self-contained folder that includes:
- Compiled executable (no Python installation required)
- All dependencies (Python runtime, Tkinter, SQLite)
- Required directories for data storage
- Startup scripts and documentation

**Advantages:**
- No installation required
- No admin rights needed
- Can run from USB drive or network share
- Easy to update (copy database to new version)
- No registry modifications
- Easy to uninstall (just delete folder)

## Build Requirements

### Prerequisites

1. **Python 3.10+** installed on your system
2. **PyInstaller** package

### Installation

```bash
# Install PyInstaller
pip install pyinstaller
```

## Building the Portable Distribution

### Automated Build (Recommended)

The easiest way to build is using the provided build script:

```bash
# Navigate to project root
cd d:\Projects\MediaArchive

# Run the build script
python build_portable.py
```

This script will:
1. Clean previous builds
2. Check for icon file
3. Run PyInstaller
4. Create directory structure
5. Copy additional files
6. Verify build integrity
7. Display summary

### Manual Build

If you prefer to build manually:

```bash
# Run PyInstaller with spec file
pyinstaller MediaArchiveManager.spec

# Create directories
mkdir dist\MediaArchiveManager\data
mkdir dist\MediaArchiveManager\backups
mkdir dist\MediaArchiveManager\config
mkdir dist\MediaArchiveManager\logs

# Copy additional files
copy start.bat dist\MediaArchiveManager\
copy VERSION.txt dist\MediaArchiveManager\
copy icon.ico dist\MediaArchiveManager\
```

## Build Output

After a successful build, you'll have:

```
dist/
  MediaArchiveManager/
    ├── MediaArchiveManager.exe      (1.7 MB)
    ├── start.bat                    (2 KB)
    ├── VERSION.txt                  (4 KB)
    ├── icon.ico                     (3 KB)
    ├── _internal/                   (20 MB - dependencies)
    ├── data/                        (empty - for database)
    ├── backups/                     (empty - for backups)
    ├── config/                      (empty - for config)
    └── logs/                        (empty - for logs)
```

**Total Size:** ~23 MB

## Testing the Build

### Quick Test

1. Navigate to `dist/MediaArchiveManager/`
2. Double-click `MediaArchiveManager.exe` or `start.bat`
3. Application should launch immediately

### Functional Testing

Test these features:
- [ ] Application window opens
- [ ] Window title shows "Media Archive Manager v2.0.0"
- [ ] About dialog shows "Version 2.0.0"
- [ ] Icon displays in taskbar
- [ ] Database is created in `data/` folder
- [ ] Logs are created in `logs/` folder
- [ ] Add/Edit/Delete media works
- [ ] Search functionality works
- [ ] Import/Export works
- [ ] Backup functionality works

### Portability Testing

- [ ] Copy folder to different location - still works
- [ ] Copy folder to different computer - still works
- [ ] Run from USB drive - works
- [ ] Run from network share - works

## Distribution

### Creating a ZIP Archive

```bash
# Navigate to dist folder
cd dist

# Create ZIP archive (using Windows built-in or 7-Zip)
# Using PowerShell:
Compress-Archive -Path MediaArchiveManager -DestinationPath MediaArchiveManager_v2.0.0_Portable.zip

# Or using 7-Zip:
7z a MediaArchiveManager_v2.0.0_Portable.zip MediaArchiveManager
```

### Distribution Package Contents

```
MediaArchiveManager_v2.0.0_Portable.zip
└── MediaArchiveManager/
    ├── MediaArchiveManager.exe
    ├── start.bat
    ├── VERSION.txt
    ├── icon.ico
    ├── _internal/
    ├── data/
    ├── backups/
    ├── config/
    └── logs/
```

### Sharing the Distribution

1. **Direct Download:** Host ZIP file on website
2. **Cloud Storage:** Upload to Google Drive, OneDrive, etc.
3. **GitHub Releases:** Attach to GitHub release
4. **USB Drive:** Copy folder to USB for physical distribution

## User Installation

### For End Users

1. **Download** the ZIP file
2. **Extract** to desired location (e.g., `C:\Programs\MediaArchiveManager\`)
3. **Run** by double-clicking:
   - `MediaArchiveManager.exe` (direct launch)
   - `start.bat` (with directory creation)
4. **Done!** No installation wizard, no admin rights needed

### First Run

On first run, the application will:
1. Create `data/media_archive.db` (empty database)
2. Create `logs/media_archive.log` (log file)
3. Display main window

## Updating to a New Version

### For Users

1. **Backup** current database:
   - File > Backup Database
   - Save backup to safe location

2. **Extract** new version to different folder

3. **Copy** database:
   - Copy `data/media_archive.db` from old folder
   - Paste into new folder's `data/` directory

4. **Run** new version:
   - Double-click `start.bat` or `.exe`
   - Verify data is intact

5. **Delete** old version folder (optional)

### Important Notes

- **Database is NOT overwritten** during updates
- Always backup before updating
- New version uses same database format
- Preferences are stored in database (preserved)

## Troubleshooting

### Application Won't Start

**Symptom:** Nothing happens when clicking `.exe` or `start.bat`

**Solutions:**
1. Check `logs/media_archive.log` for errors
2. Verify all files were extracted correctly
3. Try running `start.bat` instead of `.exe`
4. Check Windows Event Viewer for system errors

### "Windows protected your PC" Warning

**Symptom:** SmartScreen warning appears

**Solutions:**
1. Click "More info" then "Run anyway"
2. This is normal for unsigned executables
3. Consider code signing for production release

### Antivirus Blocks Application

**Symptom:** Antivirus software blocks the executable

**Solutions:**
1. Add exception for `MediaArchiveManager.exe`
2. This is a false positive (common with PyInstaller)
3. Submit to antivirus vendor for whitelisting

### Database Errors

**Symptom:** "Database locked" or "Cannot create database"

**Solutions:**
1. Ensure `data/` directory exists and is writable
2. Check available disk space
3. Verify no other instance is running
4. Try restoring from backup

### Missing Dependencies

**Symptom:** "Module not found" or similar errors

**Solutions:**
1. Verify `_internal/` folder exists
2. Check that all files were extracted
3. Rebuild using `build_portable.py`

## Advanced Topics

### Customizing the Build

Edit `MediaArchiveManager.spec` to customize:

```python
# Change console output
console=False,  # Set to True for debug output

# Add hidden imports
hiddenimports=['module_name'],

# Exclude modules
excludes=['matplotlib', 'numpy'],

# Change icon
icon='path/to/icon.ico',
```

### Code Signing

To sign the executable (requires certificate):

```bash
# Using signtool (Windows SDK)
signtool sign /f certificate.pfx /p password /t http://timestamp.server.com MediaArchiveManager.exe
```

### Creating an Installer

For a more professional distribution, consider:
- **NSIS** (Nullsoft Scriptable Install System)
- **Inno Setup**
- **WiX Toolset**

These create traditional Windows installers with:
- Installation wizard
- Start menu shortcuts
- Uninstall support
- Registry entries

### Multi-Platform Support

To build for other platforms:

```bash
# Linux
pyinstaller MediaArchiveManager.spec --onedir

# macOS
pyinstaller MediaArchiveManager.spec --onedir
```

## Performance Optimization

### Startup Time

- First run: ~2-5 seconds (normal for PyInstaller)
- Subsequent runs: ~1-2 seconds (cached)

### Memory Usage

- Typical: 50-100 MB
- With large database: 100-200 MB

### Database Performance

- SQLite handles thousands of records efficiently
- For very large databases (>100k records), consider:
  - Archiving old data
  - Using pagination
  - Optimizing queries

## Security Considerations

### Data Security

- Database stored locally (no cloud sync)
- No network access required
- All data stays on user's computer
- Backups are standard SQLite files

### Code Security

- No external dependencies (except Python stdlib)
- No telemetry or tracking
- No automatic updates (manual update process)
- Source code available for review

### Antivirus Considerations

- PyInstaller executables may trigger false positives
- This is normal and expected
- Submit to antivirus vendors for whitelisting
- Consider code signing for production

## Version Management

### Version Numbering

Current version: **2.0.0**

Format: `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features
- **PATCH:** Bug fixes

### Updating Version

To update version for new release:

1. Edit `src/utils/config.py`:
   ```python
   APP_VERSION = "2.1.0"  # Update version
   ```

2. Update `VERSION.txt` with new date

3. Rebuild using `build_portable.py`

4. Create new ZIP archive with version in filename:
   ```
   MediaArchiveManager_v2.1.0_Portable.zip
   ```

## Release Checklist

Before releasing a new version:

- [ ] Update version number
- [ ] Test all features
- [ ] Test portability
- [ ] Update VERSION.txt
- [ ] Update documentation
- [ ] Create clean build
- [ ] Test build on clean system
- [ ] Create ZIP archive
- [ ] Test ZIP extraction
- [ ] Verify file sizes
- [ ] Create release notes
- [ ] Upload to distribution channel
- [ ] Announce release

## Support & Documentation

### User Documentation

- `VERSION.txt` - Version and quick start info
- `README.md` - Project overview
- `docs/` - Detailed documentation

### Developer Documentation

- `plans/PORTABLE_DISTRIBUTION_PLAN.md` - Detailed plan
- `MediaArchiveManager.spec` - PyInstaller configuration
- `build_portable.py` - Build automation script

### Getting Help

For issues or questions:
1. Check `logs/media_archive.log` for errors
2. Review documentation
3. Check GitHub issues
4. Contact developer

## References

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Python Tkinter](https://docs.python.org/3/library/tkinter.html)
- [SQLite](https://www.sqlite.org/)
- [Windows Batch Scripting](https://ss64.com/nt/)

## Changelog

### Version 2.0.0 (2026-03-09)

**Initial Portable Distribution Release**

- Created PyInstaller spec file
- Implemented build automation script
- Created startup batch script
- Added VERSION.txt with build information
- Generated application icon
- Created portable directory structure
- Documented build and distribution process
- Tested on Windows 11

**Features:**
- Standalone executable (no Python required)
- Portable folder structure
- Database protection (not overwritten on update)
- Easy installation (extract and run)
- Easy uninstallation (delete folder)

**Known Issues:**
- None

**Future Enhancements:**
- Code signing for Windows SmartScreen
- Auto-updater functionality
- Traditional Windows installer
- Multi-platform support (Linux, macOS)

---

**Last Updated:** 2026-03-09  
**Version:** 2.0.0  
**Status:** Ready for Distribution
