@echo off
REM PMBOT One-Click Startup with Automatic Port Liberation
REM Run this file directly: double-click or run from command prompt

cls
echo.
echo ===============================================
echo  PMBOT Auto-Start with Automatic Port Fixing
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

REM Run the main startup script
echo Starting PMBOT...
echo.

python scripts\auto_start.py
if errorlevel 1 (
    echo.
    echo ERROR: Startup failed. Check the messages above.
    pause
    exit /b 1
)

exit /b 0
