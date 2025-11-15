@echo off
REM PM Bot - Automated Setup Script for Windows
REM This script prepares the project for running after a fresh clone

setlocal enabledelayedexpansion

echo ==================================
echo PM Bot - Windows Setup Script
echo ==================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed
    echo Please install Docker from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)
echo [OK] Docker is installed

REM Check if Docker Compose is installed
docker compose version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose is not installed
    echo Please install Docker Compose: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed

REM Create .env files if they don't exist
echo.
echo Setting up environment files...

if not exist "backend\.env" (
    echo Creating backend\.env from .env.example...
    copy backend\.env.example backend\.env >nul
    echo [OK] backend\.env created
) else (
    echo [WARN] backend\.env already exists
)

if not exist "Frontend\.env" (
    echo Creating Frontend\.env from .env.example...
    copy Frontend\.env.example Frontend\.env >nul
    echo [OK] Frontend\.env created
) else (
    echo [WARN] Frontend\.env already exists
)

REM Build images
echo.
echo Building Docker images...
docker compose build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)
echo [OK] Docker images built

REM Start services
echo.
echo Starting services...
docker compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [OK] Services started

REM Wait for services
echo.
echo Waiting for services to be ready...
echo Waiting for backend...

setlocal
set "count=0"
:wait_backend
if %count% geq 30 (
    echo [WARN] Backend startup timeout
    goto wait_frontend
)
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/docs >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend is ready
    goto wait_frontend
)
set /a count+=1
goto wait_backend

:wait_frontend
echo Waiting for frontend...
set "count=0"
:wait_frontend_loop
if %count% geq 30 (
    echo [WARN] Frontend startup timeout
    goto print_summary
)
timeout /t 2 /nobreak >nul
curl -s http://localhost:3000 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend is ready
    goto print_summary
)
set /a count+=1
goto wait_frontend_loop

REM Print summary
:print_summary
echo.
echo ==================================
echo Setup Complete! 
echo ==================================
echo.
echo Your PM Bot is now running!
echo.
echo Access the application:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Next steps:
echo   1. Open http://localhost:3000 in your browser
echo   2. Sign up or login with Google
echo   3. Select your region
echo   4. Complete onboarding
echo   5. Start practicing!
echo.
echo To view logs:
echo   docker compose logs -f
echo.
echo To stop the application:
echo   docker compose down
echo.
echo For help, see COMPLETE_SETUP_GUIDE.md
echo ==================================
echo.
pause
