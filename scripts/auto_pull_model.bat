@echo off
REM Ollama Model Auto-Puller - Pure Batch (No Python Required)
REM Ensures required AI models are available before starting PMBOT

setlocal enabledelayedexpansion

set "PRIMARY_MODEL=qwen2:7b-instruct"
set "FALLBACK_MODELS=llama2 neural-chat mistral"
set "OLLAMA_URL=http://localhost:11434"
set "MAX_WAIT=120"

REM Function to check if Ollama is running
set "OLLAMA_RUNNING=0"
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; Write-Output 'running' } catch { Write-Output 'stopped' }" 2^>nul') do (
    if "%%i"=="running" set "OLLAMA_RUNNING=1"
)

cls
echo.
echo ============================================================
echo 🤖 Ollama Model Auto-Setup
echo ============================================================
echo Primary model: %PRIMARY_MODEL%
echo Fallback models: %FALLBACK_MODELS%
echo.

REM Check if Ollama is running
echo 🔍 Checking if Ollama is running...

set "elapsed=0"
:wait_loop
if %OLLAMA_RUNNING% equ 1 goto ollama_ready

if %elapsed% gtr %MAX_WAIT% (
    echo ❌ Ollama is not running!
    echo.
    echo 📋 Setup Instructions:
    echo    1. Install Ollama from https://ollama.ai
    echo    2. Start Ollama with: ollama serve
    echo    3. Keep that terminal open while using PMBOT
    echo.
    echo Or download the model manually:
    echo    ollama pull %PRIMARY_MODEL%
    echo.
    exit /b 1
)

set /a "remaining=%MAX_WAIT% - %elapsed%"
echo ⏳ Waiting for Ollama... (%remaining%s remaining)
timeout /t 3 /nobreak >nul

set /a "elapsed=%elapsed% + 3"
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; Write-Output 'running' } catch { Write-Output 'stopped' }" 2^>nul') do (
    if "%%i"=="running" set "OLLAMA_RUNNING=1"
)
goto wait_loop

:ollama_ready
echo ✅ Ollama is running and accessible
echo.

REM Check if primary model exists
echo 🔍 Checking for primary model: %PRIMARY_MODEL%...

for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/show' -Body '{\"name\": \"%PRIMARY_MODEL%\"}' -ContentType 'application/json' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; if ($response.Content -match '\"name\"') { Write-Output 'found' } } catch { Write-Output 'not_found' }" 2^>nul') do (
    if "%%i"=="found" (
        echo ✅ Model %PRIMARY_MODEL% is already available
        echo.
        exit /b 0
    )
)

REM Try to pull primary model
echo.
echo 📥 Pulling model: %PRIMARY_MODEL%
echo    This may take 5-15 minutes on first run...
echo    Model size: 4-7GB
echo.

where ollama >nul 2>&1
if errorlevel 1 (
    echo ❌ ollama command not found
    echo    Please install Ollama from https://ollama.ai
    exit /b 1
)

ollama pull %PRIMARY_MODEL%
if errorlevel 1 (
    echo ❌ Failed to pull %PRIMARY_MODEL%
    echo.
    echo ⚠️ Trying fallback models...
) else (
    echo ✅ %PRIMARY_MODEL% is ready!
    echo.
    exit /b 0
)

REM Try fallback models
for %%model in (%FALLBACK_MODELS%) do (
    echo.
    echo 🔄 Checking fallback: %%model...
    
    for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/show' -Body '{\"name\": \"%%model\"}' -ContentType 'application/json' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; if ($response.Content -match '\"name\"') { Write-Output 'found' } } catch { Write-Output 'not_found' }" 2^>nul') do (
        if "%%i"=="found" (
            echo ✅ Found fallback model: %%model
            echo    (Performance may be reduced, but PMBOT will work)
            echo.
            exit /b 0
        )
    )
    
    echo 📥 Pulling fallback model: %%model...
    ollama pull %%model >nul 2>&1
    if errorlevel 0 (
        echo ✅ %%model is ready!
        echo    (Performance may be reduced, but PMBOT will work)
        echo.
        exit /b 0
    )
)

REM No models available
echo.
echo ❌ No suitable Ollama model found!
echo.
echo 📋 Quick Fix:
echo    Run in a terminal: ollama pull %PRIMARY_MODEL%
echo    Or try: ollama pull llama2
echo.
exit /b 1
