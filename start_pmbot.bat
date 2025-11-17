@echo off
REM PMBOT Smart Startup with Auto-Port Detection
REM Run this file directly: double-click or run from command prompt
REM No Python required - uses pure Batch

setlocal enabledelayedexpansion

cls
echo.
echo ===============================================
echo  PMBOT Auto-Start with Port Detection
echo ===============================================
echo.

REM Check if Docker is available
echo 🔍 Step 0: Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker is not installed or not running
    echo Please start Docker Desktop from https://www.docker.com
    pause
    exit /b 1
)
echo ✅ Docker is running
echo.

REM Check if Ollama is available
echo 🔍 Checking Ollama...
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; Write-Host '✅ Ollama is running' } catch { Write-Host '⚠️  Ollama is not responding' }" 2>nul
echo.

REM Step 1: Run port detection
echo 🔍 Step 1: Running port detection and configuration...
if exist "%~dp0scripts\detect_ports.bat" (
    call "%~dp0scripts\detect_ports.bat"
) else (
    echo ⚠️  Port detection script not found
)
echo.

REM Step 2: Auto-pull the model
echo 📦 Step 2: Checking AI models...
if exist "%~dp0scripts\auto_pull_model.bat" (
    call "%~dp0scripts\auto_pull_model.bat"
)
echo.

REM Step 3: Start docker-compose
echo 🚀 Step 3: Starting PMBOT services...
echo.

cd /d "%~dp0"
docker-compose up --build

if errorlevel 1 (
    echo.
    echo ERROR: Docker Compose failed
    pause
    exit /b 1
)

)

exit /b 0
