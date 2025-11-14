# Auto-generate .env files from .env.example templates
# Run this once after cloning the repository

$ErrorActionPreference = "Stop"

Write-Host "🔧 Setting up PMBOT environment files..." -ForegroundColor Cyan

# Backend .env
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating backend/.env from template..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env" -Force
    Write-Host "✅ backend/.env created. Update OAuth credentials if needed." -ForegroundColor Green
} else {
    Write-Host "⏭️  backend/.env already exists, skipping." -ForegroundColor Gray
}

# Frontend .env
if (-not (Test-Path "Frontend\.env")) {
    Write-Host "📝 Creating Frontend/.env from template..." -ForegroundColor Yellow
    Copy-Item "Frontend\.env.example" "Frontend\.env" -Force
    Write-Host "✅ Frontend/.env created." -ForegroundColor Green
} else {
    Write-Host "⏭️  Frontend/.env already exists, skipping." -ForegroundColor Gray
}

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure Ollama is running on your host machine:" -ForegroundColor White
Write-Host "     - Download: https://ollama.ai" -ForegroundColor Gray
Write-Host "     - Run: ollama serve" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Verify models are downloaded:" -ForegroundColor White
Write-Host "     - ollama pull llama3" -ForegroundColor Gray
Write-Host "     - ollama pull qwen2:7b-instruct" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Start the application:" -ForegroundColor White
Write-Host "     - docker compose up --build" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Access the application:" -ForegroundColor White
Write-Host "     - Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "     - Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 For troubleshooting, see SETUP.md" -ForegroundColor Cyan
