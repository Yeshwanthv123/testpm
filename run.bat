@echo off
REM Simple startup wrapper for team leads/managers
REM Just tell them to run: run.bat

cls

echo.
echo ╔════════════════════════════════════════════╗
echo ║         PMBOT Startup Script               ║
echo ║                                            ║
echo ║  Starting services automatically...        ║
echo ║  (Handles port conflicts automatically)    ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check Docker
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found
    echo Please install Docker from https://www.docker.com
    pause
    exit /b 1
)
echo OK: Docker is installed
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)
echo OK: Python is installed
echo.

REM Check Docker running
echo Checking if Docker is running...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo OK: Docker is running
echo.

REM Start main script
echo Starting PMBOT...
echo.

call start_pmbot.bat
if errorlevel 1 exit /b 1

exit /b 0
