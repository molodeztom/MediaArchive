@echo off
REM ============================================================================
REM Media Archive Manager - Startup Script
REM Version 2.0.0
REM ============================================================================
REM
REM This script launches the Media Archive Manager application.
REM It ensures all required directories exist before starting the application.
REM
REM Usage:
REM   Double-click this file to start the application
REM   Or run from command line: start.bat
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM Set window title
title Media Archive Manager v2.0.0

REM Display startup message
echo.
echo ============================================================================
echo Media Archive Manager v2.0.0
echo ============================================================================
echo.
echo Starting application...
echo.

REM Create required directories if they don't exist
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

if not exist "backups" (
    echo Creating backups directory...
    mkdir backups
)

if not exist "config" (
    echo Creating config directory...
    mkdir config
)

if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

echo.

REM Check if executable exists
if not exist "MediaArchiveManager.exe" (
    echo.
    echo ERROR: MediaArchiveManager.exe not found!
    echo.
    echo Please ensure you are running this script from the correct directory.
    echo The directory should contain:
    echo   - MediaArchiveManager.exe
    echo   - start.bat
    echo   - data/
    echo   - backups/
    echo   - config/
    echo   - logs/
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Launching MediaArchiveManager.exe...
echo.

start "" "MediaArchiveManager.exe"

REM Exit without waiting
exit /b 0
