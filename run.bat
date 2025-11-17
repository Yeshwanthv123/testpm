@echo off
REM Simple startup wrapper for team leads/managers
REM Run from cmd.exe or PowerShell with: run.bat or .\run.bat

setlocal enabledelayedexpansion

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

call "%~dp0start_pmbot.bat"
exit /b %errorlevel%
