@echo off
REM Auto-detect ports and start PMBOT on Windows

echo.
echo ========================================
echo  PMBOT - Auto-Port Detection & Launch
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python from https://www.python.org
    pause
    exit /b 1
)

REM Run port detection
echo 🔍 Detecting available ports...
python scripts\detect_ports.py
if errorlevel 1 (
    echo ❌ Port detection failed
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Docker services...
docker compose up --build

pause
