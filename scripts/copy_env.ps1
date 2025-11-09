<#
Simple helper to copy the example env into the backend folder on Windows PowerShell.
Usage: .\scripts\copy_env.ps1
#>
$src = Join-Path -Path (Resolve-Path .) -ChildPath "backend\.env.example"
$dest = Join-Path -Path (Resolve-Path .) -ChildPath "backend\.env"

if (-Not (Test-Path $src)) {
    Write-Error "Source .env.example not found at $src"
    exit 1
}

Copy-Item -Path $src -Destination $dest -Force
Write-Host "Copied backend/.env.example -> backend/.env. Edit backend/.env with real values and do NOT commit it to git." -ForegroundColor Green
