#!/bin/bash
# Simple startup wrapper for team leads/managers
# Just tell them to run: bash run.sh

set -e

clear

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║         🚀 PMBOT Startup Script            ║"
echo "║                                            ║"
echo "║  Starting services automatically...        ║"
echo "║  (Handles port conflicts automatically)    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    echo "   Please install Docker from https://www.docker.com"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "   Please install Python 3 from https://www.python.org"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Check Ollama
echo "🤖 Checking Ollama..."
if curl -s http://localhost:11434 &>/dev/null; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama is NOT running"
    echo "   Run in another terminal: ollama serve"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Starting PMBOT..."
echo ""

# Run the startup script
exec bash start_pmbot.sh
