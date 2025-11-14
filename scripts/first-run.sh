#!/bin/bash
# PMBOT First-Run Setup Script
# This script handles everything needed to get PMBOT running from a fresh clone

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    PMBOT - First-Run Setup Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "${YELLOW}📌 Step $1: $2${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ Error: $1${NC}"
    exit 1
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
print_step "1" "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
fi
print_success "Docker is installed"

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed or not accessible"
fi
print_success "Docker Compose is available"

if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed. Please install from https://ollama.ai"
fi
print_success "Ollama is installed"

echo ""

# Generate .env files
print_step "2" "Generating .env files from templates..."

if [ -f backend/.env ]; then
    print_info "backend/.env already exists, skipping"
else
    cp backend/.env.example backend/.env
    print_success "Created backend/.env"
fi

if [ -f Frontend/.env ]; then
    print_info "Frontend/.env already exists, skipping"
else
    cp Frontend/.env.example Frontend/.env
    print_success "Created Frontend/.env"
fi

echo ""

# Check Ollama
print_step "3" "Checking Ollama models..."

if ! ollama list | grep -q "llama3"; then
    print_info "llama3 not found, downloading..."
    ollama pull llama3
    print_success "llama3 downloaded"
else
    print_success "llama3 is already downloaded"
fi

if ! ollama list | grep -q "qwen2:7b-instruct"; then
    print_info "qwen2:7b-instruct not found, downloading..."
    ollama pull qwen2:7b-instruct
    print_success "qwen2:7b-instruct downloaded"
else
    print_success "qwen2:7b-instruct is already downloaded"
fi

echo ""

# Build Docker images
print_step "4" "Building Docker images..."
docker compose build
print_success "Docker images built"

echo ""

# Start services
print_step "5" "Starting Docker services..."
docker compose up -d
print_success "Docker services started"

# Wait for services to stabilize
print_info "Waiting for services to start (this may take 30 seconds)..."
sleep 10

# Check if backend is healthy
print_step "6" "Verifying services are running..."

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health | grep -q '"status"'; then
        print_success "Backend is responding"
        break
    fi
    
    attempt=$((attempt + 1))
    if [ $attempt -lt $max_attempts ]; then
        echo -n "."
        sleep 1
    fi
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Backend failed to start. Run 'docker compose logs pmbot-backend' to see errors"
fi

echo ""

# Final summary
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📍 Next Steps:${NC}"
echo -e "${NC}  1. Start Ollama server in a separate terminal:"
echo -e "     ${YELLOW}ollama serve${NC}"
echo ""
echo -e "${NC}  2. Access the application:"
echo -e "     ${YELLOW}Frontend:${NC} http://localhost:3000"
echo -e "     ${YELLOW}Backend:${NC}  http://localhost:8000"
echo ""
echo -e "${NC}  3. View logs (if needed):"
echo -e "     ${YELLOW}docker compose logs -f${NC}"
echo ""

print_info "For detailed information, see SETUP.md"
print_info "For common commands, see COMMANDS.md"
