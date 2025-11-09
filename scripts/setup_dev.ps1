<#
Setup development environment on Windows (PowerShell).
Creates a Python virtual environment in `backend/.venv` and installs backend and llm-stub requirements.
This does not install Node dependencies for the Frontend.

Usage: .\scripts\setup_dev.ps1
#>
Set-StrictMode -Version Latest

$repoRoot = (Get-Location).Path
$backendDir = Join-Path $repoRoot "backend"
$llmStubDir = Join-Path $backendDir "llm_stub"

if (-Not (Test-Path $backendDir)) {
    Write-Error "backend folder not found. Run this script from the repository root."
    exit 1
}

Push-Location $backendDir

if (-Not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment at backend/.venv..."
    python -m venv .venv
} else {
    Write-Host "Using existing backend/.venv virtual environment"
}

Write-Host "Activating venv and installing Python packages..."
& .\.venv\Scripts\Activate.ps1

try {
    if (Test-Path "requirements.txt") {
        Write-Host "Installing backend/requirements.txt..."
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
    }
} catch {
    Write-Warning "Failed to install backend requirements. Try running the command manually with administrator privileges or check your Python/pip setup."
}

# Install llm_stub requirements (if present)
if (Test-Path $llmStubDir) {
    Push-Location $llmStubDir
    if (Test-Path "requirements.txt") {
        Write-Host "Installing llm_stub/requirements.txt..."
        try {
            python -m pip install -r requirements.txt
        } catch {
            Write-Warning "Failed to install llm_stub requirements. You may need to install heavy packages like sentence-transformers separately."
        }
    }
    Pop-Location
}

Pop-Location

Write-Host "Setup complete. Run the backend with: (cd backend; . ./.venv/Scripts/Activate.ps1; uvicorn app.main:app --reload)" -ForegroundColor Green
