#!/bin/bash
# PMBOT One-Click Startup with Automatic Port Liberation
# Usage: ./start_pmbot.sh

set -e

echo ""
echo "==============================================="
echo " PMBOT Auto-Start with Automatic Port Fixing"
echo "==============================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker from https://www.docker.com"
    exit 1
fi

# Check if Ollama is running
echo "Checking Ollama..."
if curl -s http://localhost:11434 &>/dev/null; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama is NOT running"
    echo "   Run in another terminal: ollama serve"
    echo ""
fi
echo ""

# Auto-pull the model
echo "Auto-pulling Ollama model..."
if command -v python3 &> /dev/null; then
    python3 scripts/auto_pull_model.py || true
fi
echo ""

# Start services
echo "Starting PMBOT services..."
echo ""

cd "$(dirname "$0")"
docker-compose up --build

exit $?
