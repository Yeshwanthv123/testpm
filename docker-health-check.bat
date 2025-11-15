@echo off
REM PM Bot - Docker Health Check Script for Windows

setlocal enabledelayedexpansion

cls
echo ==================================
echo PM Bot - Health Check
echo ==================================
echo.

REM Check Docker
echo Checking Docker...
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed
    exit /b 1
)
echo [OK] Docker is installed

REM Check Docker Compose
echo Checking Docker Compose...
docker compose version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose is not installed
    exit /b 1
)
echo [OK] Docker Compose is installed

REM Check services status
echo.
echo Checking services...

docker compose ps --format "table {{.Names}}\t{{.State}}" | findstr pmbot >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Docker Compose services are running
    docker compose ps
) else (
    echo [WARN] Some services may not be running
)

REM Check ports
echo.
echo Checking ports...

REM Check port 3000
netstat -ano | findstr ":3000 " >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port 3000 (Frontend) is listening
) else (
    echo [WARN] Port 3000 (Frontend) is not listening
)

REM Check port 8000
netstat -ano | findstr ":8000 " >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port 8000 (Backend) is listening
) else (
    echo [WARN] Port 8000 (Backend) is not listening
)

REM Check port 5432
netstat -ano | findstr ":5432 " >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port 5432 (Database) is listening
) else (
    echo [WARN] Port 5432 (Database) is not listening
)

REM Check port 5000
netstat -ano | findstr ":5000 " >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port 5000 (LLM Service) is listening
) else (
    echo [WARN] Port 5000 (LLM Service) is not listening
)

REM Check API endpoints
echo.
echo Checking API endpoints...

echo Testing backend health...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/docs | findstr "200" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend API is responding
) else (
    echo [WARN] Backend API is not responding
)

echo Testing frontend health...
curl -s -o nul -w "%%{http_code}" http://localhost:3000 | findstr "200" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend is responding
) else (
    echo [WARN] Frontend is not responding
)

REM Check environment files
echo.
echo Checking environment files...

if exist "backend\.env" (
    echo [OK] backend\.env exists
) else (
    echo [ERROR] backend\.env is missing
)

if exist "Frontend\.env" (
    echo [OK] Frontend\.env exists
) else (
    echo [ERROR] Frontend\.env is missing
)

REM Summary
echo.
echo ==================================
echo Health Check Summary
echo ==================================
echo.
echo Frontend:  http://localhost:3000
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo If services are not responding:
echo   1. Check logs: docker compose logs -f
echo   2. Restart services: docker compose restart
echo   3. See COMPLETE_SETUP_GUIDE.md for troubleshooting
echo.
pause
