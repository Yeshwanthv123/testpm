@echo off
REM PM Bot - Fix Port Conflicts Script for Windows
REM Automatically finds and kills processes using required ports

setlocal enabledelayedexpansion

echo ==================================
echo PM Bot - Port Conflict Fixer
echo ==================================
echo.

REM Define ports
set "PORTS=3000 8000 5432 5000"

echo Checking for processes using required ports...
echo.

REM Check each port
for %%P in (%PORTS%) do (
    echo Checking port %%P...
    for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P "') do (
        if not "%%A"=="" (
            echo   Found process using port %%P (PID: %%A)
            tasklist | findstr "%%A" >nul
            if !ERRORLEVEL! EQU 0 (
                echo   Killing process %%A...
                taskkill /PID %%A /F >nul 2>nul
                if !ERRORLEVEL! EQU 0 (
                    echo   [OK] Process killed
                ) else (
                    echo   [WARN] Could not kill process (may need admin rights)
                )
            )
        )
    )
)

echo.
echo ==================================
echo Port Check Complete
echo ==================================
echo.
echo All PM Bot ports should now be available:
echo   Port 3000  (Frontend)
echo   Port 8000  (Backend)
echo   Port 5432  (Database)
echo   Port 5000  (LLM Service)
echo.
echo You can now run: setup.bat
echo.
pause
