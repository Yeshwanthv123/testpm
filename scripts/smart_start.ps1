# PMBOT Smart Startup for Windows
# This script handles port conflicts and starts Docker safely

param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000,
    [switch]$Force
)

function Test-PortInUse {
    param([int]$Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("127.0.0.1", $Port)
        return $true
    } catch {
        return $false
    } finally {
        $connection.Dispose()
    }
}

function Find-FreePort {
    param(
        [int]$StartPort,
        [int]$MaxAttempts = 20
    )
    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        $port = $StartPort + $i
        if (-not (Test-PortInUse -Port $port)) {
            return $port
        }
    }
    return $null
}

function Get-ProcessOnPort {
    param([int]$Port)
    try {
        $output = netstat -ano | Select-String ":$Port\s+LISTENING"
        if ($output) {
            $pid = ([string]$output).Split()[-1]
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                return "$($process.ProcessName) (PID: $pid)"
            }
        }
    } catch {}
    return $null
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 PMBOT Smart Startup (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "📦 Checking Docker..." -ForegroundColor Yellow
$docker = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is NOT running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Docker is running" -ForegroundColor Green
}

# Check ports
Write-Host ""
Write-Host "🔗 Checking Ports..." -ForegroundColor Yellow
Write-Host ""

$backendInUse = Test-PortInUse -Port $BackendPort
$frontendInUse = Test-PortInUse -Port $FrontendPort

if ($backendInUse -or $frontendInUse) {
    Write-Host "⚠️  Port Conflict Detected!" -ForegroundColor Red
    Write-Host ""
    
    if ($backendInUse) {
        Write-Host "   ❌ Port $BackendPort (Backend) is IN USE" -ForegroundColor Red
        $process = Get-ProcessOnPort -Port $BackendPort
        if ($process) {
            Write-Host "      Process: $process" -ForegroundColor Gray
        }
        
        $freePort = Find-FreePort -StartPort ($BackendPort + 1)
        if ($freePort) {
            Write-Host "      Suggestion: Use port $freePort" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ✅ Port $BackendPort (Backend) is FREE" -ForegroundColor Green
    }
    
    if ($frontendInUse) {
        Write-Host "   ❌ Port $FrontendPort (Frontend) is IN USE" -ForegroundColor Red
        $process = Get-ProcessOnPort -Port $FrontendPort
        if ($process) {
            Write-Host "      Process: $process" -ForegroundColor Gray
        }
        
        $freePort = Find-FreePort -StartPort ($FrontendPort + 1)
        if ($freePort) {
            Write-Host "      Suggestion: Use port $freePort" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ✅ Port $FrontendPort (Frontend) is FREE" -ForegroundColor Green
    }
    
    if (-not $Force) {
        Write-Host ""
        Write-Host "📝 Steps to fix:" -ForegroundColor Cyan
        Write-Host "   1. Update docker-compose.yml"
        Write-Host "      Change: ports:"
        Write-Host "              - \"8000:8000\""
        Write-Host "      To:      - \"<NEW_PORT>:8000\""
        Write-Host ""
        Write-Host "   2. Update Frontend in docker-compose.yml"
        Write-Host "      VITE_API_BASE: http://localhost:<NEW_PORT>"
        Write-Host ""
        Write-Host "   3. Run again: ./scripts/smart_start.ps1 --Force"
        exit 1
    }
} else {
    Write-Host "   ✅ Port $BackendPort (Backend) is FREE" -ForegroundColor Green
    Write-Host "   ✅ Port $FrontendPort (Frontend) is FREE" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Ready to start!" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:$BackendPort" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:$FrontendPort" -ForegroundColor Cyan
Write-Host ""

# Show startup info
Write-Host "📋 Starting docker-compose..." -ForegroundColor Yellow
Write-Host "   Command: docker-compose up --build" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start Docker
try {
    & docker-compose up --build
} catch {
    Write-Host "Error starting docker-compose: $_" -ForegroundColor Red
    exit 1
}
