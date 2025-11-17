@echo off
REM Port Detection and Configuration - Pure Batch (No Python Required)
REM Auto-detects available ports and updates .env files

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
set "DEFAULT_BACKEND_PORT=8000"
set "DEFAULT_FRONTEND_PORT=3000"
set "DEFAULT_DB_PORT=5432"

setlocal enabledelayedexpansion

REM Try to detect netstat availability
where netstat >nul 2>&1
if errorlevel 1 (
    echo ⚠️  netstat not available, using default ports
    set "BACKEND_PORT=%DEFAULT_BACKEND_PORT%"
    set "FRONTEND_PORT=%DEFAULT_FRONTEND_PORT%"
    set "DB_PORT=%DEFAULT_DB_PORT%"
) else (
    REM Check backend port
    netstat -ano | findstr ":%DEFAULT_BACKEND_PORT% " >nul 2>&1
    if errorlevel 1 (
        set "BACKEND_PORT=%DEFAULT_BACKEND_PORT%"
    ) else (
        REM Port in use, find alternative
        for /l %%i in (1,1,50) do (
            set /a "alt_port=%DEFAULT_BACKEND_PORT% + %%i"
            netstat -ano | findstr ":!alt_port! " >nul 2>&1
            if errorlevel 1 (
                set "BACKEND_PORT=!alt_port!"
                goto backend_found
            )
        )
        set "BACKEND_PORT=%DEFAULT_BACKEND_PORT%"
        :backend_found
    )
    
    REM Check frontend port
    netstat -ano | findstr ":%DEFAULT_FRONTEND_PORT% " >nul 2>&1
    if errorlevel 1 (
        set "FRONTEND_PORT=%DEFAULT_FRONTEND_PORT%"
    ) else (
        for /l %%i in (1,1,50) do (
            set /a "alt_port=%DEFAULT_FRONTEND_PORT% + %%i"
            netstat -ano | findstr ":!alt_port! " >nul 2>&1
            if errorlevel 1 (
                set "FRONTEND_PORT=!alt_port!"
                goto frontend_found
            )
        )
        set "FRONTEND_PORT=%DEFAULT_FRONTEND_PORT%"
        :frontend_found
    )
    
    REM Check database port
    netstat -ano | findstr ":%DEFAULT_DB_PORT% " >nul 2>&1
    if errorlevel 1 (
        set "DB_PORT=%DEFAULT_DB_PORT%"
    ) else (
        for /l %%i in (1,1,50) do (
            set /a "alt_port=%DEFAULT_DB_PORT% + %%i"
            netstat -ano | findstr ":!alt_port! " >nul 2>&1
            if errorlevel 1 (
                set "DB_PORT=!alt_port!"
                goto db_found
            )
        )
        set "DB_PORT=%DEFAULT_DB_PORT%"
        :db_found
    )
)

echo.
echo 🔍 Detected port configuration:
echo.
if "!BACKEND_PORT!"=="%DEFAULT_BACKEND_PORT%" (
    echo ✅ Backend: Port !BACKEND_PORT! available
) else (
    echo ⚠️  Backend: Port %DEFAULT_BACKEND_PORT% ^-^> !BACKEND_PORT!
)

if "!FRONTEND_PORT!"=="%DEFAULT_FRONTEND_PORT%" (
    echo ✅ Frontend: Port !FRONTEND_PORT! available
) else (
    echo ⚠️  Frontend: Port %DEFAULT_FRONTEND_PORT% ^-^> !FRONTEND_PORT!
)

if "!DB_PORT!"=="%DEFAULT_DB_PORT%" (
    echo ✅ Database: Port !DB_PORT! available
) else (
    echo ⚠️  Database: Port %DEFAULT_DB_PORT% ^-^> !DB_PORT!
)

echo.
echo 📝 Updating configuration files...
echo.

REM Update backend/.env
set "BACKEND_ENV=%PROJECT_ROOT%\backend\.env"
if not exist "%PROJECT_ROOT%\backend" mkdir "%PROJECT_ROOT%\backend"

REM Helper function to update env vars
REM Called as: call :update_env_file filepath varname value
call :update_env_file "%BACKEND_ENV%" "VITE_API_BASE" "http://localhost:!BACKEND_PORT!"
call :update_env_file "%BACKEND_ENV%" "DATABASE_URL" "postgresql://postgres:password@localhost:!DB_PORT!/pmbot"
call :update_env_file "%BACKEND_ENV%" "LLM_API_URL" "http://localhost:11434"

echo ✅ Updated %BACKEND_ENV%

REM Update Frontend/.env
set "FRONTEND_ENV=%PROJECT_ROOT%\Frontend\.env"
if not exist "%PROJECT_ROOT%\Frontend" mkdir "%PROJECT_ROOT%\Frontend"

call :update_env_file "%FRONTEND_ENV%" "VITE_API_BASE" "http://localhost:!BACKEND_PORT!"

echo ✅ Updated %FRONTEND_ENV%

REM Save port config as JSON
set "PORTS_JSON=%PROJECT_ROOT%\.ports.json"
(
    echo {
    echo   "backend": !BACKEND_PORT!,
    echo   "frontend": !FRONTEND_PORT!,
    echo   "database": !DB_PORT!
    echo }
) > "%PORTS_JSON%"

echo ✅ Saved port configuration to .ports.json
echo.
exit /b 0

REM Subroutine to update env file
:update_env_file
setlocal enabledelayedexpansion
set "file=%~1"
set "var=%~2"
set "value=%~3"

if not exist "%file%" (
    mkdir "%~dp1" >nul 2>&1
    echo %var%=%value% >> "%file%"
) else (
    REM Check if var exists
    findstr /R "^%var%=" "%file%" >nul 2>&1
    if errorlevel 1 (
        REM Variable doesn't exist, add it
        echo %var%=%value% >> "%file%"
    ) else (
        REM Variable exists, replace it
        for /f "delims=" %%i in ('type "%file%"') do (
            set "line=%%i"
            if "!line:%var%=!"=="!line!" (
                echo !line! >> "%file%.tmp"
            ) else (
                echo %var%=%value% >> "%file%.tmp"
            )
        )
        move /y "%file%.tmp" "%file%" >nul 2>&1
    )
)
endlocal
exit /b 0
