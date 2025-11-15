#!/bin/bash
# PM Bot - Docker Health Check Script
# Verifies all services are running and responsive

set -e

RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'

echo -e "${BLUE}=================================="
echo "PM Bot - Health Check"
echo "==================================${RESET}"
echo ""

# Check Docker
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed${RESET}"
    exit 1
fi
echo -e "${GREEN}[OK] Docker is installed${RESET}"

# Check Docker Compose
echo "Checking Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo -e "${RED}[ERROR] Docker Compose is not installed${RESET}"
    exit 1
fi
echo -e "${GREEN}[OK] Docker Compose is installed${RESET}"

# Check services status
echo ""
echo -e "${BLUE}Checking services...${RESET}"

SERVICES=("pmbot-db" "pmbot-backend" "pmbot-frontend" "pmbot-llm-stub")

for service in "${SERVICES[@]}"; do
    STATUS=$(docker compose ps -q "$service" 2>/dev/null || echo "")
    if [ -z "$STATUS" ]; then
        echo -e "${YELLOW}[WARN] Service '$service' is not running${RESET}"
    else
        echo -e "${GREEN}[OK] Service '$service' is running${RESET}"
    fi
done

# Check ports
echo ""
echo -e "${BLUE}Checking ports...${RESET}"

# Function to check port
check_port() {
    local port=$1
    local service=$2
    
    if nc -z -w1 localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}[OK] Port $port ($service) is open${RESET}"
    else
        echo -e "${YELLOW}[WARN] Port $port ($service) is not responding${RESET}"
    fi
}

check_port 3000 "Frontend"
check_port 8000 "Backend"
check_port 5432 "Database"
check_port 5000 "LLM Service"

# Check API endpoints
echo ""
echo -e "${BLUE}Checking API endpoints...${RESET}"

# Check backend health
echo "Testing backend health..."
if curl -s http://localhost:8000/docs &> /dev/null; then
    echo -e "${GREEN}[OK] Backend API is responding${RESET}"
else
    echo -e "${YELLOW}[WARN] Backend API is not responding on port 8000${RESET}"
fi

# Check frontend health
echo "Testing frontend health..."
if curl -s http://localhost:3000 &> /dev/null; then
    echo -e "${GREEN}[OK] Frontend is responding${RESET}"
else
    echo -e "${YELLOW}[WARN] Frontend is not responding on port 3000${RESET}"
fi

# Database connection test
echo "Testing database connection..."
if docker compose exec -T pmbot-backend psql -h pmbot-db -U postgres -d mydatabase -c "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}[OK] Database is accessible${RESET}"
else
    echo -e "${YELLOW}[WARN] Database is not accessible${RESET}"
fi

# Check environment files
echo ""
echo -e "${BLUE}Checking environment files...${RESET}"

if [ -f "backend/.env" ]; then
    echo -e "${GREEN}[OK] backend/.env exists${RESET}"
else
    echo -e "${RED}[ERROR] backend/.env is missing${RESET}"
fi

if [ -f "Frontend/.env" ]; then
    echo -e "${GREEN}[OK] Frontend/.env exists${RESET}"
else
    echo -e "${RED}[ERROR] Frontend/.env is missing${RESET}"
fi

# Summary
echo ""
echo -e "${BLUE}=================================="
echo "Health Check Summary"
echo "==================================${RESET}"
echo ""
echo -e "${GREEN}Frontend:  http://localhost:3000${RESET}"
echo -e "${GREEN}Backend:   http://localhost:8000${RESET}"
echo -e "${GREEN}API Docs:  http://localhost:8000/docs${RESET}"
echo ""
echo "If services are not responding:"
echo "  1. Check logs: docker compose logs -f"
echo "  2. Restart services: docker compose restart"
echo "  3. See COMPLETE_SETUP_GUIDE.md for troubleshooting"
echo ""
