#!/bin/bash
# PMBOT One-Click Startup with Automatic Port Liberation
# Usage: ./start_pmbot.sh

set -e

echo ""
echo "==============================================="
echo " PMBOT Auto-Start with Automatic Port Fixing"
echo "==============================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker from https://www.docker.com"
    exit 1
fi

# Make the startup script executable
chmod +x scripts/auto_start.py

# Run the main startup script
echo "Starting PMBOT..."
echo ""

python3 scripts/auto_start.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "ERROR: Startup failed. Check the messages above."
    exit 1
fi

exit 0
