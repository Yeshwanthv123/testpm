#!/bin/bash
# PMBOT First-Run Setup for Mac/Linux
# This script handles:
# 1. Environment file setup
# 2. Port conflict detection
# 3. Port liberation
# 4. Ollama auto-pull
# 5. Docker compose startup

set -e

echo ""
echo "=========================================="
echo "  🚀 PMBOT First-Run Setup (Mac/Linux)"
echo "=========================================="
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Step 1: Setup environment files
echo "Step 1️⃣  Setting up environment files..."
python3 scripts/setup_environment.py
echo ""

# Step 2: Check prerequisites
echo "Step 2️⃣  Checking prerequisites..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "   Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "✅ Docker installed: $(docker --version)"

# Check Docker running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop"
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Step 3: Port detection
echo "Step 3️⃣  Detecting available ports..."
python3 scripts/find_available_ports.py
echo ""

# Step 4: Free up ports if needed
echo "Step 4️⃣  Freeing up ports if necessary..."
python3 scripts/free_ports.py
echo ""

# Step 5: Check Ollama
echo "Step 5️⃣  Checking Ollama..."
echo ""
if curl -s http://localhost:11434 &>/dev/null; then
    echo "✅ Ollama is running at localhost:11434"
else
    echo "⚠️  Ollama is NOT running"
    echo ""
    echo "   IMPORTANT: You need to start Ollama in a separate terminal:"
    echo "   $ ollama serve"
    echo ""
    echo "   Keep that terminal open while using PMBOT"
    echo ""
fi
echo ""

# Step 6: Auto-pull model
echo "Step 6️⃣  Auto-pulling Ollama model (if needed)..."
python3 scripts/auto_pull_model.py || true
echo ""

# Step 7: Start services
echo "Step 7️⃣  Starting PMBOT services..."
echo ""
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose up --build

echo ""
echo "=========================================="
echo "✅ PMBOT is ready!"
echo "=========================================="
echo ""
echo "Access the application at:"
echo "  🌐 Frontend: http://localhost:3000"
echo ""
