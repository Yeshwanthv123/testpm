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

REM ============================================
REM AGGRESSIVE PORT CONFLICT RESOLUTION
REM ============================================
echo.
echo [STEP 1] Cleaning up existing Docker resources...
docker compose down -v >nul 2>nul
docker stop $(docker ps -q) >nul 2>nul
docker system prune -f >nul 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Docker cleanup complete

REM Check and fix port conflicts
echo.
echo [STEP 2] Checking for port conflicts...

setlocal enabledelayedexpansion
set "ports_to_check=3000 5000 5432 8000"
set "ports_freed=0"

for %%P in (!ports_to_check!) do (
    netstat -ano | findstr ":%%P " >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo [WARN] Port %%P is already in use - attempting to free it...
        for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P "') do (
            taskkill /PID %%A /F >nul 2>nul
            if !ERRORLEVEL! EQU 0 (
                set /a ports_freed+=1
            )
        )
    )
)

if !ports_freed! gtr 0 (
    echo [OK] Freed !ports_freed! port(s)
    echo      Waiting for ports to be released...
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] All required ports are available
)

REM ============================================
REM ENVIRONMENT FILES SETUP
REM ============================================
echo.
echo [STEP 3] Setting up environment files...

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo Creating backend\.env from template...
        copy "backend\.env.example" "backend\.env" >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            echo [OK] backend\.env created
        ) else (
            echo [ERROR] Failed to create backend\.env
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] backend\.env.example not found
        pause
        exit /b 1
    )
) else (
    echo [OK] backend\.env already exists
)

if not exist "Frontend\.env" (
    if exist "Frontend\.env.example" (
        echo Creating Frontend\.env from template...
        copy "Frontend\.env.example" "Frontend\.env" >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            echo [OK] Frontend\.env created
        ) else (
            echo [ERROR] Failed to create Frontend\.env
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] Frontend\.env.example not found
        pause
        exit /b 1
    )
) else (
    echo [OK] Frontend\.env already exists
)

REM ============================================
REM BUILD & START SERVICES
REM ============================================
echo.
echo [STEP 4] Building Docker images...
docker compose build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)
echo [OK] Docker images built successfully

REM Start services
echo.
echo [STEP 5] Starting services...
docker compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start services
    echo Try running: docker compose logs
    pause
    exit /b 1
)
echo [OK] Services started

REM ============================================
REM WAIT FOR SERVICES TO BE HEALTHY
REM ============================================
echo.
echo [STEP 6] Waiting for services to be ready...
echo.

setlocal enabledelayedexpansion
set "max_attempts=40"
set "backend_ready=0"
set "frontend_ready=0"

echo Waiting for Database...
set "db_attempts=0"
:wait_db
if !db_attempts! geq 30 (
    echo [WARN] Database startup timeout - continuing anyway...
    goto wait_backend
)
docker compose exec -T db pg_isready -U user -d mydatabase >nul 2>nul
if !ERRORLEVEL! EQU 0 (
    echo [OK] Database is ready
    goto wait_backend
)
timeout /t 1 /nobreak >nul
set /a db_attempts+=1
goto wait_db

:wait_backend
echo Waiting for Backend...
set "count=0"
:wait_backend_loop
if !count! geq !max_attempts! (
    echo [WARN] Backend startup timeout - it may still be initializing...
    goto wait_frontend
)
curl -s http://localhost:8000/docs >nul 2>nul
if !ERRORLEVEL! EQU 0 (
    echo [OK] Backend is ready
    set "backend_ready=1"
    goto wait_frontend
)
timeout /t 1 /nobreak >nul
set /a count+=1
goto wait_backend_loop

:wait_frontend
echo Waiting for Frontend...
set "count=0"
:wait_frontend_loop
if !count! geq !max_attempts! (
    echo [WARN] Frontend startup timeout - it may still be initializing...
    goto print_summary
)
curl -s http://localhost:3000 >nul 2>nul
if !ERRORLEVEL! EQU 0 (
    echo [OK] Frontend is ready
    set "frontend_ready=1"
    goto print_summary
)
timeout /t 1 /nobreak >nul
set /a count+=1
goto wait_frontend_loop

REM ============================================
REM PRINT SETUP SUMMARY
REM ============================================
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
echo Services Status:
if !backend_ready! EQU 1 (
    echo   ✓ Backend is ready
) else (
    echo   ? Backend is starting (check with: docker compose logs backend)
)
if !frontend_ready! EQU 1 (
    echo   ✓ Frontend is ready
) else (
    echo   ? Frontend is starting (check with: docker compose logs frontend)
)
echo.
echo Next steps:
echo   1. Open http://localhost:3000 in your browser
echo   2. Create an account or sign in
echo   3. Select your region and start practicing!
echo.
echo Useful commands:
echo   View logs:        docker compose logs -f
echo   Stop services:    docker compose down
echo   View status:      docker compose ps
echo.
echo For help, see: COMPLETE_SETUP_GUIDE.md
echo ==================================
echo.
pause
