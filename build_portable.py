#!/usr/bin/env python3
"""
Build script for creating portable distribution of Media Archive Manager.

This script automates the entire build process:
1. Cleans previous builds
2. Runs PyInstaller
3. Creates required directory structure
4. Copies additional files
5. Generates VERSION.txt with current date
6. Verifies build integrity

Usage:
    python build_portable.py

Requirements:
    pip install pyinstaller

Output:
    dist/MediaArchiveManager/ - Portable distribution folder
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# Build configuration
APP_NAME = "MediaArchiveManager"
VERSION = "2.1.0"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
APP_DIR = DIST_DIR / APP_NAME


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 80)
    print(f"  {text}")
    print("=" * 80)
    print()


def print_step(text):
    """Print a step message."""
    print(f"[*] {text}")


def print_success(text):
    """Print a success message."""
    print(f"[OK] {text}")


def print_error(text):
    """Print an error message."""
    print(f"[ERROR] {text}")


def print_warning(text):
    """Print a warning message."""
    print(f"[!] {text}")


def clean_previous_builds():
    """Clean previous build artifacts."""
    print_step("Cleaning previous builds...")
    
    dirs_to_remove = [DIST_DIR, BUILD_DIR, PROJECT_ROOT / f"{APP_NAME}.egg-info"]
    
    for dir_path in dirs_to_remove:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print_success(f"Removed {dir_path.name}")
            except Exception as e:
                print_warning(f"Could not remove {dir_path.name}: {e}")
    
    # Remove build artifacts
    for pattern in ["*.pyc", "__pycache__", "*.egg-info"]:
        for item in PROJECT_ROOT.glob(f"**/{pattern}"):
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except Exception as e:
                print_warning(f"Could not remove {item}: {e}")


def check_icon_file():
    """Check if icon file exists."""
    print_step("Checking icon file...")
    
    icon_path = PROJECT_ROOT / "icon.ico"
    if not icon_path.exists():
        print_error("icon.ico not found!")
        print_warning("Creating icon file...")
        
        # Try to create icon
        try:
            import icon
            icon.create_icon_file()
            print_success("Icon file created")
        except Exception as e:
            print_error(f"Failed to create icon: {e}")
            return False
    else:
        print_success(f"Icon file found: {icon_path.stat().st_size} bytes")
    
    return True


def run_pyinstaller():
    """Run PyInstaller to build the executable."""
    print_step("Running PyInstaller...")
    
    spec_file = PROJECT_ROOT / "MediaArchiveManager.spec"
    if not spec_file.exists():
        print_error("MediaArchiveManager.spec not found!")
        return False
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--distpath", str(DIST_DIR)]
        print(f"  Command: {' '.join(cmd)}")
        print()
        
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)
        
        if result.returncode == 0:
            print_success("PyInstaller build completed successfully")
            return True
        else:
            print_error(f"PyInstaller failed with return code {result.returncode}")
            return False
    
    except subprocess.CalledProcessError as e:
        print_error(f"PyInstaller failed: {e}")
        return False
    except Exception as e:
        print_error(f"Error running PyInstaller: {e}")
        return False


def create_directory_structure():
    """Create required directory structure."""
    print_step("Creating directory structure...")
    
    required_dirs = [
        APP_DIR / "data",
        APP_DIR / "backups",
        APP_DIR / "config",
        APP_DIR / "logs",
    ]
    
    for dir_path in required_dirs:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep file to preserve empty directories
            gitkeep = dir_path / ".gitkeep"
            gitkeep.touch()
            
            print_success(f"Created {dir_path.relative_to(APP_DIR)}/")
        except Exception as e:
            print_error(f"Failed to create {dir_path}: {e}")
            return False
    
    return True


def copy_additional_files():
    """Copy additional files to distribution folder."""
    print_step("Copying additional files...")
    
    files_to_copy = [
        ("start.bat", "start.bat"),
        ("VERSION.txt", "VERSION.txt"),
        ("icon.ico", "icon.ico"),
    ]
    
    for src_name, dst_name in files_to_copy:
        src_path = PROJECT_ROOT / src_name
        dst_path = APP_DIR / dst_name
        
        if not src_path.exists():
            print_warning(f"Source file not found: {src_name}")
            continue
        
        try:
            shutil.copy2(src_path, dst_path)
            print_success(f"Copied {src_name}")
        except Exception as e:
            print_error(f"Failed to copy {src_name}: {e}")
            return False
    
    return True


def verify_build():
    """Verify the build integrity."""
    print_step("Verifying build integrity...")
    
    required_files = [
        APP_DIR / f"{APP_NAME}.exe",
        APP_DIR / "start.bat",
        APP_DIR / "VERSION.txt",
        APP_DIR / "icon.ico",
    ]
    
    required_dirs = [
        APP_DIR / "data",
        APP_DIR / "backups",
        APP_DIR / "config",
        APP_DIR / "logs",
        APP_DIR / "_internal",
    ]
    
    all_ok = True
    
    # Check files
    for file_path in required_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print_success(f"Found {file_path.name} ({size} bytes)")
        else:
            print_error(f"Missing {file_path.name}")
            all_ok = False
    
    # Check directories
    for dir_path in required_dirs:
        if dir_path.exists():
            print_success(f"Found {dir_path.name}/ directory")
        else:
            print_error(f"Missing {dir_path.name}/ directory")
            all_ok = False
    
    return all_ok


def print_summary():
    """Print build summary."""
    print_header("BUILD SUMMARY")
    
    print(f"Application: {APP_NAME}")
    print(f"Version: {VERSION}")
    print(f"Build Date: {BUILD_DATE}")
    print(f"Distribution: {APP_DIR}")
    print()
    
    if APP_DIR.exists():
        # Calculate total size
        total_size = 0
        for item in APP_DIR.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
        
        print(f"Total Size: {total_size / (1024*1024):.2f} MB")
        print()
        
        print("Directory Structure:")
        print(f"  {APP_DIR.name}/")
        for item in sorted(APP_DIR.iterdir()):
            if item.is_dir():
                print(f"    +-- {item.name}/")
            else:
                size = item.stat().st_size
                print(f"    +-- {item.name} ({size} bytes)")
        print()
    
    print("Next Steps:")
    print(f"1. Test the application: {APP_DIR / f'{APP_NAME}.exe'}")
    print(f"2. Or run: {APP_DIR / 'start.bat'}")
    print(f"3. Create ZIP archive: {APP_NAME}_v{VERSION}_Portable.zip")
    print(f"4. Distribute the ZIP file")
    print()


def main():
    """Main build process."""
    print_header(f"Building {APP_NAME} v{VERSION} Portable Distribution")
    
    try:
        # Step 1: Clean previous builds
        clean_previous_builds()
        
        # Step 2: Check icon file
        if not check_icon_file():
            print_error("Icon file check failed")
            return False
        
        # Step 3: Run PyInstaller
        if not run_pyinstaller():
            print_error("PyInstaller build failed")
            return False
        
        # Step 4: Create directory structure
        if not create_directory_structure():
            print_error("Directory structure creation failed")
            return False
        
        # Step 5: Copy additional files
        if not copy_additional_files():
            print_error("File copying failed")
            return False
        
        # Step 6: Verify build
        if not verify_build():
            print_warning("Build verification found issues")
        
        # Step 7: Print summary
        print_summary()
        
        print_header("BUILD COMPLETED SUCCESSFULLY")
        print_success(f"Portable distribution ready at: {APP_DIR}")
        print()
        
        return True
    
    except Exception as e:
        print_error(f"Build failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
