#!/bin/bash
# Auto-detect ports and start PMBOT on Mac/Linux

echo ""
echo "========================================"
echo "  PMBOT - Auto-Port Detection & Launch"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python from https://www.python.org"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Please install Docker from https://www.docker.com"
    exit 1
fi

# Run port detection
echo "🔍 Detecting available ports..."
python3 scripts/detect_ports.py
if [ $? -ne 0 ]; then
    echo "❌ Port detection failed"
    exit 1
fi

echo ""
echo "🚀 Starting Docker services..."
docker compose up --build

