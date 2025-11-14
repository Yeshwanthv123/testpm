# PM Bot Setup Script
# This script automates the setup for a fresh clone
# Usage: .\setup.ps1

Write-Host "🚀 PM Bot Setup Script" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found." -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version
    Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Environment Setup" -ForegroundColor Yellow

# Create .env from example if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    if (Test-Path "backend\.env.example") {
        Write-Host "📄 Creating backend/.env from .env.example..."
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "✅ Environment file created at backend/.env" -ForegroundColor Green
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ backend/.env already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "🐳 Starting Docker Services" -ForegroundColor Yellow
Write-Host "This may take 1-2 minutes on first run..." -ForegroundColor Cyan

# Start Docker services
docker-compose down --remove-orphans 2>&1 | Out-Null
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Compose failed to start" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow

# Wait for services to be ready
$maxAttempts = 30
$attempt = 0
$allHealthy = $false

while ($attempt -lt $maxAttempts) {
    $attempt++
    
    # Check if all containers are running
    $psOutput = docker-compose ps --services --filter "status=running"
    $runningServices = @($psOutput -split "`n" | Where-Object { $_ })
    $expectedServices = @("pmbot-backend", "pmbot-frontend", "pmbot-db", "pmbot-llm-stub")
    
    if ($runningServices.Count -ge 4) {
        Write-Host "✅ All services running" -ForegroundColor Green
        $allHealthy = $true
        break
    }
    
    Write-Host "  Attempt $attempt/$maxAttempts - Waiting for services..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if (-not $allHealthy) {
    Write-Host "⚠️  Services may still be starting. Checking logs..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Service Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Green
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:3000 in your browser"
Write-Host "  2. Sign up or log in"
Write-Host "  3. Select company and experience level"
Write-Host "  4. Start practicing interviews"
Write-Host ""
Write-Host "🆘 Troubleshooting:" -ForegroundColor Yellow
Write-Host "  • View logs:    docker-compose logs -f"
Write-Host "  • Stop service: docker-compose down"
Write-Host "  • Restart:      docker-compose up -d"
Write-Host ""

# Optionally open the frontend in browser
$response = Read-Host "Would you like to open the application in your browser? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Start-Process "http://localhost:3000"
}
