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

# Create .env files if they don't exist
setup_env_files() {
    echo ""
    echo "Setting up environment files..."
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        echo "Creating backend/.env from .env.example..."
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✓ backend/.env created${NC}"
    else
        echo -e "${YELLOW}⚠ backend/.env already exists${NC}"
    fi
    
    # Frontend .env
    if [ ! -f "Frontend/.env" ]; then
        echo "Creating Frontend/.env from .env.example..."
        cp Frontend/.env.example Frontend/.env
        echo -e "${GREEN}✓ Frontend/.env created${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend/.env already exists${NC}"
    fi
}

# Build images
build_images() {
    echo ""
    echo "Building Docker images..."
    docker compose build
    echo -e "${GREEN}✓ Docker images built${NC}"
}

# Start services
start_services() {
    echo ""
    echo "Starting services..."
    docker compose up -d
    echo -e "${GREEN}✓ Services started${NC}"
}

# Wait for services to be ready
wait_for_services() {
    echo ""
    echo "Waiting for services to be ready..."
    
    # Wait for backend
    echo "Waiting for backend..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is ready${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    # Wait for frontend
    echo "Waiting for frontend..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend is ready${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done
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
    echo "  2. Sign up or login with Google"
    echo "  3. Select your region"
    echo "  4. Complete onboarding"
    echo "  5. Start practicing!"
    echo ""
    echo "To view logs:"
    echo "  docker compose logs -f"
    echo ""
    echo "To stop the application:"
    echo "  docker compose down"
    echo ""
    echo "For help, see COMPLETE_SETUP_GUIDE.md"
    echo "=================================="
}

# Main execution
main() {
    check_docker
    check_compose
    setup_env_files
    build_images
    start_services
    wait_for_services
    print_summary
}

# Run main
main
