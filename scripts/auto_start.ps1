# Auto-Start PMBOT with Automatic Port Liberation
# Run: ./scripts/auto_start.ps1

$ErrorActionPreference = "Stop"

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

function Get-ProcessOnPort {
    param([int]$Port)
    try {
        $netstat = netstat -ano | Select-String ":$Port\s+LISTENING"
        if ($netstat) {
            $pid = ([string]$netstat).Split()[-1]
            return $pid
        }
    } catch {}
    return $null
}

function Kill-Port {
    param(
        [int]$Port,
        [switch]$Force
    )
    
    $pid = Get-ProcessOnPort -Port $Port
    if (-not $pid) {
        Write-Host "✅ Port $Port is free" -ForegroundColor Green
        return $true
    }
    
    try {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            $procName = $process.ProcessName
            Write-Host "🔴 Port $Port is in use by: $procName (PID: $pid)" -ForegroundColor Red
            
            if ($Force) {
                Write-Host "🔨 Force-killing $procName..." -ForegroundColor Yellow
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Start-Sleep -Milliseconds 500
                Write-Host "✅ Killed $procName" -ForegroundColor Green
                return $true
            } else {
                $response = Read-Host "Kill this process? (y/n)"
                if ($response -eq 'y') {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Milliseconds 500
                    Write-Host "✅ Killed $procName" -ForegroundColor Green
                    return $true
                }
            }
        }
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
    
    return $false
}

# Main Script
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "🚀 PMBOT Auto-Start with Port Liberation" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Define ports
$Ports = @{
    8000  = "Backend API"
    3000  = "Frontend"
    5432  = "Database"
    5000  = "LLM Wrapper"
}

# Free ports
Write-Host "🔍 Scanning ports..." -ForegroundColor Yellow
Write-Host ""

$allFree = $true
foreach ($port in $Ports.Keys) {
    $free = -not (Test-PortInUse -Port $port)
    if ($free) {
        Write-Host "✅ Port $port ($($Ports[$port])) - FREE" -ForegroundColor Green
    } else {
        Write-Host "🔴 Port $port ($($Ports[$port])) - IN USE" -ForegroundColor Red
        $allFree = $false
        Kill-Port -Port $port -Force
    }
}

Write-Host ""

# Verify all ports are free
Start-Sleep -Seconds 1
$stillNotFree = @()
foreach ($port in $Ports.Keys) {
    if (Test-PortInUse -Port $port) {
        $stillNotFree += $port
    }
}

if ($stillNotFree.Count -gt 0) {
    Write-Host "❌ These ports are still in use: $($stillNotFree -join ', ')" -ForegroundColor Red
    Write-Host "Cannot proceed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All ports are FREE and ready!" -ForegroundColor Green
Write-Host ""

# Check Docker
Write-Host "🐳 Checking Docker..." -ForegroundColor Yellow
$docker = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green
Write-Host ""

# Check Ollama
Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow
try {
    $ollama = curl.exe -s http://localhost:11434 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ollama is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Ollama may not be running" -ForegroundColor Yellow
        Write-Host "   Make sure to run: ollama serve" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Ollama status unknown" -ForegroundColor Yellow
}
Write-Host ""

# Start Docker
Write-Host "🚀 Starting Docker services..." -ForegroundColor Cyan
Write-Host "   Command: docker-compose up --build" -ForegroundColor Gray
Write-Host ""

try {
    & docker-compose up --build
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
