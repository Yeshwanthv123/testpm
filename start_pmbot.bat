@echo off
REM PMBOT One-Click Startup with Automatic Port Liberation
REM Pure batch script - no Python needed
REM Run this file directly: double-click or run from command prompt

setlocal enabledelayedexpansion

cls
echo.
echo ===============================================
echo  PMBOT Auto-Start with Automatic Port Fixing
echo ===============================================
echo.

REM Check if Docker is available
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo OK: Docker is running
echo.

REM Check if Ollama is available
echo Checking Ollama...
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; Write-Host 'OK: Ollama is running' } catch { Write-Host 'WARNING: Ollama is not responding' }" 2>nul
if errorlevel 1 (
    echo WARNING: Ollama may not be running
    echo Please run: ollama serve (in another terminal)
    echo.
)
echo.

REM Auto-pull the model
echo Auto-pulling Ollama model...
python "%~dp0scripts\auto_pull_model.py" 2>nul
if errorlevel 1 (
    echo WARNING: Could not auto-pull model. This is OK if already downloaded.
)
echo.

REM Start docker-compose
echo Starting services with Docker Compose...
echo.

cd /d "%~dp0"
docker-compose up --build

if errorlevel 1 (
    echo.
    echo ERROR: Docker Compose failed
    pause
    exit /b 1
)

exit /b 0
