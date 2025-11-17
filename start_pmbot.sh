#!/bin/bash
# PMBOT Smart Startup with Auto-Port Detection
# Usage: ./start_pmbot.sh
# No Python required - uses pure Bash

set -e

echo ""
echo "==============================================="
echo " PMBOT Auto-Start with Port Detection"
echo "==============================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ ERROR: Docker is not installed"
    echo "Please install Docker from https://www.docker.com"
    exit 1
fi

# Check if Ollama is running
echo "🔍 Checking Ollama server..."
if curl -s http://localhost:11434 &>/dev/null; then
    echo "✅ Ollama is running at http://localhost:11434"
else
    echo "⚠️  Ollama is NOT running"
    echo "   Run in another terminal: ollama serve"
    echo ""
fi
echo ""

# Step 1: Run port detection and configuration
echo "🔍 Step 1: Detecting available ports and updating configuration..."
if [ -f "scripts/detect_ports.sh" ]; then
    bash scripts/detect_ports.sh || true
else
    echo "⚠️  Port detection script not found"
fi
echo ""

# Step 2: Auto-pull the model if available
echo "📦 Step 2: Checking AI models..."
if [ -f "scripts/auto_pull_model.sh" ]; then
    bash scripts/auto_pull_model.sh || true
fi
echo ""

# Step 3: Start services
echo "🚀 Step 3: Starting PMBOT services..."
echo ""

docker-compose up --build
cd "$(dirname "$0")"
docker compose up --build

exit $?
