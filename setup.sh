#!/bin/bash

# PM Bot - Automated Setup Script
# This script prepares the project for running after a fresh clone

set -e

echo "=================================="
echo "PM Bot - Setup Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed${NC}"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed${NC}"
}

# Check if Docker Compose is installed
check_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
}

# Aggressive cleanup of Docker resources
cleanup_docker() {
    echo ""
    echo -e "${BLUE}[STEP 1] Cleaning up existing Docker resources...${NC}"
    
    # Stop and remove containers
    docker compose down -v 2>/dev/null || true
    docker stop $(docker ps -q) 2>/dev/null || true
    
    # Prune dangling resources
    docker system prune -f 2>/dev/null || true
    
    sleep 2
    echo -e "${GREEN}✓ Docker cleanup complete${NC}"
}

# Check and fix port conflicts
check_ports() {
    echo ""
    echo -e "${BLUE}[STEP 2] Checking for port conflicts...${NC}"
    
    PORTS=(3000 8000 5432 5000)
    PORTS_FREED=0
    
    for PORT in "${PORTS[@]}"; do
        if command -v lsof &> /dev/null; then
            # Using lsof if available (macOS/Linux)
            if lsof -i :$PORT &> /dev/null; then
                echo -e "${YELLOW}⚠ Port $PORT is in use - attempting to free it...${NC}"
                PID=$(lsof -i :$PORT -t 2>/dev/null | head -1)
                if [ ! -z "$PID" ]; then
                    kill -9 $PID 2>/dev/null || true
                    PORTS_FREED=$((PORTS_FREED + 1))
                fi
            fi
        else
            # Fallback for systems without lsof
            if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
                echo -e "${YELLOW}⚠ Port $PORT appears to be in use${NC}"
            fi
        fi
    done
    
    if [ $PORTS_FREED -gt 0 ]; then
        echo -e "${GREEN}✓ Freed $PORTS_FREED port(s)${NC}"
        echo "Waiting for ports to be released..."
        sleep 3
    else
        echo -e "${GREEN}✓ All required ports are available${NC}"
    fi
}

# Create .env files if they don't exist
setup_env_files() {
    echo ""
    echo -e "${BLUE}[STEP 3] Setting up environment files...${NC}"
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            echo "Creating backend/.env from template..."
            cp backend/.env.example backend/.env
            echo -e "${GREEN}✓ backend/.env created${NC}"
        else
            echo -e "${RED}✗ backend/.env.example not found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ backend/.env already exists${NC}"
    fi
    
    # Frontend .env
    if [ ! -f "Frontend/.env" ]; then
        if [ -f "Frontend/.env.example" ]; then
            echo "Creating Frontend/.env from template..."
            cp Frontend/.env.example Frontend/.env
            echo -e "${GREEN}✓ Frontend/.env created${NC}"
        else
            echo -e "${RED}✗ Frontend/.env.example not found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Frontend/.env already exists${NC}"
    fi
}

# Build images
build_images() {
    echo ""
    echo -e "${BLUE}[STEP 4] Building Docker images...${NC}"
    docker compose build
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
}

# Start services
start_services() {
    echo ""
    echo -e "${BLUE}[STEP 5] Starting services...${NC}"
    docker compose up -d
    echo -e "${GREEN}✓ Services started${NC}"
}

# Wait for services to be ready
wait_for_services() {
    echo ""
    echo -e "${BLUE}[STEP 6] Waiting for services to be ready...${NC}"
    
    # Wait for database
    echo "Waiting for Database..."
    for i in {1..30}; do
        if docker compose exec -T db pg_isready -U user -d mydatabase &> /dev/null; then
            echo -e "${GREEN}✓ Database is ready${NC}"
            break
        fi
        sleep 1
    done
    
    # Wait for backend
    echo "Waiting for Backend..."
    for i in {1..40}; do
        if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    
    # Wait for frontend
    echo ""
    echo "Waiting for Frontend..."
    for i in {1..40}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend is ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
}

# Print summary
print_summary() {
    echo ""
    echo "=================================="
    echo "Setup Complete! 🎉"
    echo "=================================="
    echo ""
    echo "Your PM Bot is now running!"
    echo ""
    echo "Access the application:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Create an account or sign in"
    echo "  3. Select your region and start practicing!"
    echo ""
    echo "Useful commands:"
    echo "  View logs:        docker compose logs -f"
    echo "  Stop services:    docker compose down"
    echo "  View status:      docker compose ps"
    echo ""
    echo "For help, see: COMPLETE_SETUP_GUIDE.md"
    echo "=================================="
}

# Main execution
main() {
    check_docker
    check_compose
    cleanup_docker
    check_ports
    setup_env_files
    build_images
    start_services
    wait_for_services
    print_summary
}

# Run main
main
