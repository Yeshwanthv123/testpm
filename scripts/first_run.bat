@echo off
REM PMBOT First-Run Setup for Windows
REM This script handles:
REM 1. Environment file setup
REM 2. Port conflict detection
REM 3. Port liberation
REM 4. Ollama auto-pull
REM 5. Docker compose startup

setlocal enabledelayedexpansion

cls
echo.
echo ==========================================
echo   PMBOT First-Run Setup (Windows)
echo ==========================================
echo.

REM Get project root
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%

echo Project root: %PROJECT_ROOT%
echo.

REM Step 1: Setup environment files
echo Step 1 - Setting up environment files...
python "%PROJECT_ROOT%\scripts\setup_environment.py"
if errorlevel 1 (
    echo ERROR: Failed to setup environment files
    pause
    exit /b 1
)
echo.

REM Step 2: Check prerequisites
echo Step 2 - Checking prerequisites...
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found!
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo OK: %DOCKER_VERSION%

REM Check Docker running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo OK: Docker is running
echo.

REM Step 3: Port detection
echo Step 3 - Detecting available ports...
python "%PROJECT_ROOT%\scripts\find_available_ports.py"
echo.

REM Step 4: Free up ports if needed
echo Step 4 - Freeing up ports if necessary...
python "%PROJECT_ROOT%\scripts\free_ports.py"
echo.

REM Step 5: Check Ollama
echo Step 5 - Checking Ollama...
echo.
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; Write-Host 'OK: Ollama is running at localhost:11434' } catch { Write-Host 'WARNING: Ollama is NOT running' ; Write-Host '' ; Write-Host 'IMPORTANT: Start Ollama in a separate terminal:' ; Write-Host '  > ollama serve' ; Write-Host '' ; Write-Host 'Keep that terminal open while using PMBOT' }" 2>nul
echo.

REM Step 6: Auto-pull model
echo Step 6 - Auto-pulling Ollama model (if needed)...
python "%PROJECT_ROOT%\scripts\auto_pull_model.py" 2>nul
echo.

REM Step 7: Start services
echo Step 7 - Starting PMBOT services...
echo.
cd /d "%PROJECT_ROOT%"
docker-compose down --remove-orphans 2>nul
docker-compose up --build

echo.
echo ==========================================
echo OK: PMBOT is ready!
echo ==========================================
echo.
echo Access the application at:
echo   Frontend: http://localhost:3000
echo.
pause
