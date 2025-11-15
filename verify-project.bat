@echo off
REM PM Bot - Project Verification Script for Windows
REM Ensures all required files and configurations exist

cls
echo ==================================
echo PM Bot - Project Verification
echo ==================================
echo.

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found
    echo Are you in the PMBOTNEW directory?
    pause
    exit /b 1
)
echo [OK] docker-compose.yml found

REM Check required directories
echo.
echo Checking directories...

setlocal enabledelayedexpansion
set "dirs[0]=backend"
set "dirs[1]=Frontend"
set "dirs[2]=backend\app"
set "dirs[3]=Frontend\src"

for /L %%i in (0,1,3) do (
    if exist "!dirs[%%i]!" (
        echo [OK] Directory '!dirs[%%i]!' exists
    ) else (
        echo [ERROR] Directory '!dirs[%%i]!' is missing
        pause
        exit /b 1
    )
)

REM Check required files
echo.
echo Checking required files...

set "files[0]=docker-compose.yml"
set "files[1]=backend\requirements.txt"
set "files[2]=backend\Dockerfile"
set "files[3]=backend\app\main.py"
set "files[4]=Frontend\package.json"
set "files[5]=Frontend\Dockerfile"
set "files[6]=Frontend\src\main.tsx"

for /L %%i in (0,1,6) do (
    if exist "!files[%%i]!" (
        echo [OK] File '!files[%%i]!' exists
    ) else (
        echo [ERROR] File '!files[%%i]!' is missing
        pause
        exit /b 1
    )
)

REM Check environment templates
echo.
echo Checking environment templates...

if exist "backend\.env.example" (
    echo [OK] Template 'backend\.env.example' exists
) else (
    echo [ERROR] Template 'backend\.env.example' is missing
    pause
    exit /b 1
)

if exist "Frontend\.env.example" (
    echo [OK] Template 'Frontend\.env.example' exists
) else (
    echo [ERROR] Template 'Frontend\.env.example' is missing
    pause
    exit /b 1
)

REM Check setup scripts
echo.
echo Checking setup scripts...

if exist "setup.bat" (
    echo [OK] Script 'setup.bat' exists
) else (
    echo [WARN] Script 'setup.bat' is missing
)

if exist "docker-health-check.bat" (
    echo [OK] Script 'docker-health-check.bat' exists
) else (
    echo [WARN] Script 'docker-health-check.bat' is missing
)

REM Check documentation
echo.
echo Checking documentation...

set "docs[0]=COMPLETE_SETUP_GUIDE.md"
set "docs[1]=QUICK_START.md"
set "docs[2]=TROUBLESHOOTING.md"
set "docs[3]=README.md"

for /L %%i in (0,1,3) do (
    if exist "!docs[%%i]!" (
        echo [OK] Doc '!docs[%%i]!' exists
    ) else (
        echo [WARN] Doc '!docs[%%i]!' is missing
    )
)

REM Check data files
echo.
echo Checking data files...

set "found_questions=0"
if exist "backend\PM_Questions_8000_expanded_clean_final5.csv" (
    echo [OK] Questions file found: PM_Questions_8000_expanded_clean_final5.csv
    set "found_questions=1"
)

if exist "backend\PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv" (
    echo [OK] Questions file found: PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv
    set "found_questions=1"
)

if %found_questions% equ 0 (
    echo [WARN] No PM question files found
    echo        Questions will be loaded from CSV on first run
)

REM Check scripts directory
echo.
echo Checking scripts...

if exist "scripts" (
    echo [OK] scripts directory exists
    for %%f in (scripts\*.ps1) do (
        echo       %%~nf
        exit /b 0
    )
) else (
    echo [WARN] scripts directory not found
)

REM Summary
echo.
echo ==================================
echo Verification Summary
echo ==================================
echo.
echo [OK] Project structure verified
echo [OK] All required files present
echo.
echo Project is ready to deploy!
echo.
echo Next steps:
echo   1. Review QUICK_START.md
echo   2. Run: setup.bat
echo   3. Open: http://localhost:3000
echo.
pause
