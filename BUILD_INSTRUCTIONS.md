# Build Instructions for Media Archive Manager Portable Distribution

## Quick Start

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build the portable distribution
python build_portable.py

# 3. Test the build
cd dist/MediaArchiveManager
start.bat

# 4. Create ZIP archive
cd ..
powershell -Command "Compress-Archive -Path MediaArchiveManager -DestinationPath MediaArchiveManager_v2.0.0_Portable.zip"
```

## Detailed Instructions

### Prerequisites

1. **Python 3.10 or later**
   - Download from https://www.python.org/
   - Add to PATH during installation

2. **PyInstaller**
   ```bash
   pip install pyinstaller
   ```

3. **Project Files**
   - Clone or download the MediaArchive project
   - Navigate to project root directory

### Step 1: Verify Project Structure

Ensure these files exist in project root:

```
d:\Projects\MediaArchive\
├── main.py                          (entry point)
├── icon.ico                         (application icon)
├── MediaArchiveManager.spec         (PyInstaller config)
├── start.bat                        (startup script)
├── VERSION.txt                      (version info)
├── build_portable.py                (build script)
├── src/                             (source code)
├── data/                            (data directory)
├── requirements.txt                 (dependencies)
└── README.md                        (documentation)
```

### Step 2: Create Icon File (if missing)

If `icon.ico` doesn't exist:

```bash
python icon.py
```

This creates a simple 32x32 icon. For a custom icon:
1. Create or download a `.ico` file
2. Place it in project root as `icon.ico`

### Step 3: Run Build Script

```bash
python build_portable.py
```

The script will:
1. Clean previous builds
2. Check for icon file
3. Run PyInstaller
4. Create directory structure
5. Copy additional files
6. Verify build integrity
7. Display summary

**Expected Output:**
```
================================================================================
  Building MediaArchiveManager v2.0.0 Portable Distribution
================================================================================

[*] Cleaning previous builds...
[*] Checking icon file...
[OK] Icon file found: 3148 bytes
[*] Running PyInstaller...
[OK] PyInstaller build completed successfully
[*] Creating directory structure...
[OK] Created data/
[OK] Created backups/
[OK] Created config/
[OK] Created logs/
[*] Copying additional files...
[OK] Copied start.bat
[OK] Copied VERSION.txt
[OK] Copied icon.ico
[*] Verifying build integrity...
[OK] Found MediaArchiveManager.exe (1764292 bytes)
[OK] Found start.bat (1983 bytes)
[OK] Found VERSION.txt (4537 bytes)
[OK] Found icon.ico (3148 bytes)
[OK] Found data/ directory
[OK] Found backups/ directory
[OK] Found config/ directory
[OK] Found logs/ directory
[OK] Found _internal/ directory

================================================================================
  BUILD SUMMARY
================================================================================

Application: MediaArchiveManager
Version: 2.0.0
Build Date: 2026-03-09
Distribution: d:\Projects\MediaArchive\dist\MediaArchiveManager

Total Size: 22.91 MB

Directory Structure:
  MediaArchiveManager/
    +-- _internal/
    +-- backups/
    +-- config/
    +-- data/
    +-- icon.ico (3148 bytes)
    +-- logs/
    +-- MediaArchiveManager.exe (1764292 bytes)
    +-- start.bat (1983 bytes)
    +-- VERSION.txt (4537 bytes)

Next Steps:
1. Test the application: d:\Projects\MediaArchive\dist\MediaArchiveManager\MediaArchiveManager.exe
2. Or run: d:\Projects\MediaArchive\dist\MediaArchiveManager\start.bat
3. Create ZIP archive: MediaArchiveManager_v2.0.0_Portable.zip
4. Distribute the ZIP file

================================================================================
  BUILD COMPLETED SUCCESSFULLY
================================================================================

[OK] Portable distribution ready at: d:\Projects\MediaArchive\dist\MediaArchiveManager
```

### Step 4: Test the Build

Navigate to the build output:

```bash
cd dist/MediaArchiveManager
```

Test by running:

```bash
# Option 1: Direct executable
MediaArchiveManager.exe

# Option 2: Startup script
start.bat
```

**Verify:**
- [ ] Application window opens
- [ ] Window title shows "Media Archive Manager v2.0.0"
- [ ] Icon displays in taskbar
- [ ] No error messages
- [ ] Can add/edit/delete media
- [ ] Database created in `data/` folder
- [ ] Logs created in `logs/` folder

### Step 5: Create Distribution Archive

#### Using PowerShell (Windows 10+)

```powershell
cd dist
Compress-Archive -Path MediaArchiveManager -DestinationPath MediaArchiveManager_v2.0.0_Portable.zip
```

#### Using 7-Zip

```bash
cd dist
7z a MediaArchiveManager_v2.0.0_Portable.zip MediaArchiveManager
```

#### Using Windows Explorer

1. Right-click `MediaArchiveManager` folder
2. Select "Send to" > "Compressed (zipped) folder"
3. Rename to `MediaArchiveManager_v2.0.0_Portable.zip`

### Step 6: Verify Archive

```bash
# List contents
powershell -Command "Expand-Archive -Path MediaArchiveManager_v2.0.0_Portable.zip -DestinationPath test_extract"

# Check structure
dir test_extract\MediaArchiveManager

# Clean up
rmdir /s /q test_extract
```

## Troubleshooting

### Build Fails: "icon.ico not found"

**Solution:**
```bash
python icon.py
```

### Build Fails: "PyInstaller not installed"

**Solution:**
```bash
pip install pyinstaller
```

### Build Fails: "main.py not found"

**Solution:**
- Ensure you're in project root directory
- Check that `main.py` exists

### Build Fails: "Permission denied"

**Solution:**
- Close any open files in the project
- Ensure you have write permissions
- Try running as administrator

### Executable Won't Start

**Solution:**
1. Check `logs/media_archive.log` for errors
2. Verify all files were copied correctly
3. Try running `start.bat` instead
4. Check Windows Event Viewer

### "Windows protected your PC" Warning

**Solution:**
- Click "More info" then "Run anyway"
- This is normal for unsigned executables

## Manual Build (Alternative)

If the build script fails, build manually:

```bash
# Run PyInstaller
pyinstaller MediaArchiveManager.spec

# Create directories
mkdir dist\MediaArchiveManager\data
mkdir dist\MediaArchiveManager\backups
mkdir dist\MediaArchiveManager\config
mkdir dist\MediaArchiveManager\logs

# Create .gitkeep files
type nul > dist\MediaArchiveManager\data\.gitkeep
type nul > dist\MediaArchiveManager\backups\.gitkeep
type nul > dist\MediaArchiveManager\config\.gitkeep
type nul > dist\MediaArchiveManager\logs\.gitkeep

# Copy files
copy start.bat dist\MediaArchiveManager\
copy VERSION.txt dist\MediaArchiveManager\
copy icon.ico dist\MediaArchiveManager\
```

## Customizing the Build

### Change Application Name

Edit `MediaArchiveManager.spec`:

```python
exe = EXE(
    ...
    name='YourAppName',  # Change this
    ...
)

coll = COLLECT(
    ...
    name='YourAppName',  # And this
)
```

### Change Icon

Replace `icon.ico` with your custom icon, or edit spec:

```python
exe = EXE(
    ...
    icon='path/to/your/icon.ico',
    ...
)
```

### Add Hidden Imports

If the build is missing modules, add to spec:

```python
a = Analysis(
    ...
    hiddenimports=['module1', 'module2'],
    ...
)
```

### Exclude Modules

To reduce size, exclude unused modules:

```python
a = Analysis(
    ...
    excludes=['matplotlib', 'numpy', 'pandas'],
    ...
)
```

## Performance Tips

### Reduce Build Time

- Use `--onedir` mode (faster than `--onefile`)
- Disable UPX compression: `upx=False`
- Use `--noupx` flag

### Reduce File Size

- Exclude unused modules
- Use `--strip` flag
- Remove debug symbols

### Improve Startup Time

- Use `--onedir` mode (faster loading)
- Avoid large imports at module level
- Use lazy imports for heavy modules

## Version Updates

To build a new version:

1. Update version in `src/utils/config.py`:
   ```python
   APP_VERSION = "2.1.0"
   ```

2. Update `VERSION.txt` with new date

3. Rebuild:
   ```bash
   python build_portable.py
   ```

4. Create new archive:
   ```bash
   cd dist
   Compress-Archive -Path MediaArchiveManager -DestinationPath MediaArchiveManager_v2.1.0_Portable.zip
   ```

## Distribution

### Upload to GitHub

```bash
# Create release on GitHub
# Upload MediaArchiveManager_v2.0.0_Portable.zip as release asset
```

### Upload to Website

1. Upload ZIP to web server
2. Create download page
3. Add version information
4. Include release notes

### Create Installer (Optional)

For a more professional distribution:

1. Download **Inno Setup** or **NSIS**
2. Create installer script
3. Build installer executable
4. Distribute installer

## Cleanup

After successful build:

```bash
# Remove build artifacts
rmdir /s /q build
del /q *.egg-info

# Keep only dist folder for distribution
```

## Next Steps

1. **Test** the portable distribution on different systems
2. **Document** any issues or improvements
3. **Distribute** the ZIP archive
4. **Collect** user feedback
5. **Plan** next version improvements

## Support

For issues or questions:
1. Check `logs/media_archive.log`
2. Review `docs/PORTABLE_DISTRIBUTION_GUIDE.md`
3. Check PyInstaller documentation
4. Contact developer

## References

- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Python Packaging](https://packaging.python.org/)
- [Windows Batch Scripting](https://ss64.com/nt/)

---

**Last Updated:** 2026-03-09  
**Version:** 2.0.0  
**Status:** Ready for Distribution
