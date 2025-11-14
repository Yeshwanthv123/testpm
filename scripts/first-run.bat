@echo off
REM PMBOT First-Run Setup Script (Windows)
REM This script handles everything needed to get PMBOT running from a fresh clone

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║    PMBOT - First-Run Setup Script          ║
echo ╚════════════════════════════════════════════╝
echo.

REM Function-like procedures using goto
:check_prerequisites
echo 📌 Step 1: Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    exit /b 1
)
echo ✅ Docker is installed

where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ollama is not installed. Please install from https://ollama.ai
    exit /b 1
)
echo ✅ Ollama is installed

docker compose version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not available
    exit /b 1
)
echo ✅ Docker Compose is available
echo.

REM Generate .env files
echo 📌 Step 2: Generating .env files from templates...

if exist backend\.env (
    echo ⏭️  backend\.env already exists, skipping
) else (
    copy backend\.env.example backend\.env >nul
    echo ✅ Created backend\.env
)

if exist Frontend\.env (
    echo ⏭️  Frontend\.env already exists, skipping
) else (
    copy Frontend\.env.example Frontend\.env >nul
    echo ✅ Created Frontend\.env
)
echo.

REM Check Ollama models
echo 📌 Step 3: Checking Ollama models...

ollama list 2>nul | find /I "llama3" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ℹ️  llama3 not found, downloading...
    call ollama pull llama3
    echo ✅ llama3 downloaded
) else (
    echo ✅ llama3 is already downloaded
)

ollama list 2>nul | find /I "qwen2:7b-instruct" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ℹ️  qwen2:7b-instruct not found, downloading...
    call ollama pull qwen2:7b-instruct
    echo ✅ qwen2:7b-instruct downloaded
) else (
    echo ✅ qwen2:7b-instruct is already downloaded
)
echo.

REM Build Docker images
echo 📌 Step 4: Building Docker images...
docker compose build
echo ✅ Docker images built
echo.

REM Start services
echo 📌 Step 5: Starting Docker services...
docker compose up -d
echo ✅ Docker services started

REM Wait for services
echo ℹ️  Waiting for services to start (this may take 30 seconds)...
timeout /t 10 /nobreak

REM Check backend health
echo 📌 Step 6: Verifying services are running...

setlocal EnableDelayedExpansion
set "max_attempts=30"
set "attempt=0"

:health_check_loop
set /a attempt+=1

for /f %%i in ('curl -s http://localhost:8000/health 2^>nul ^| find /c "status"') do (
    if "%%i" GTR "0" (
        echo ✅ Backend is responding
        goto health_check_success
    )
)

if !attempt! LSS !max_attempts! (
    echo -n "."
    timeout /t 1 /nobreak >nul
    goto health_check_loop
)

echo ❌ Backend failed to start. Run 'docker compose logs pmbot-backend' to see errors
exit /b 1

:health_check_success
echo.
echo.
echo ╔════════════════════════════════════════════╗
echo ✨ Setup Complete!
echo ╚════════════════════════════════════════════╝
echo.

echo 📍 Next Steps:
echo.
echo   1. Start Ollama server in a separate terminal:
echo      ollama serve
echo.
echo   2. Access the application:
echo      Frontend: http://localhost:3000
echo      Backend:  http://localhost:8000
echo.
echo   3. View logs (if needed):
echo      docker compose logs -f
echo.
echo ℹ️  For detailed information, see SETUP.md
echo ℹ️  For common commands, see COMMANDS.md
echo.

endlocal
