#!/bin/bash
# Auto-Start PMBOT with Automatic Port Liberation
# Works on macOS and Linux
# Usage: ./scripts/auto_start.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}=======================================${NC}"
    echo -e "${BLUE}🚀 PMBOT Auto-Start with Port Liberation${NC}"
    echo -e "${BLUE}=======================================${NC}"
    echo ""
}

test_port() {
    local port=$1
    nc -zv 127.0.0.1 $port &>/dev/null && return 0 || return 1
}

get_process_on_port() {
    local port=$1
    local os=$(uname)
    
    if [[ "$os" == "Darwin" ]]; then
        # macOS
        lsof -i :$port -n -P 2>/dev/null | grep LISTEN | awk '{print $2, $1}' | head -1
    else
        # Linux
        lsof -i :$port -n -P 2>/dev/null | grep LISTEN | awk '{print $2, $1}' | head -1
    fi
}

kill_process_auto() {
    local port=$1
    local proc_info=$(get_process_on_port $port)
    
    if [ -z "$proc_info" ]; then
        echo -e "${GREEN}✅ Port $port is free${NC}"
        return 0
    fi
    
    local pid=$(echo $proc_info | awk '{print $1}')
    local proc=$(echo $proc_info | awk '{print $2}')
    
    echo -e "${RED}🔴 Port $port is in use by: $proc (PID: $pid)${NC}"
    
    # Auto-kill Docker, Python, Node, Java, Ollama, PostgreSQL processes
    if [[ "$proc" =~ ^(docker|python|node|java|ollama|postgres) ]]; then
        echo -e "${YELLOW}🔨 Auto-killing $proc...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 0.5
        echo -e "${GREEN}✅ Killed $proc${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Port $port is used by $proc (not auto-killable)${NC}"
        return 1
    fi
}

# Main Script
print_header

# Check if running as root for port operations
if [[ $EUID -ne 0 ]]; then
    echo -e "${YELLOW}ℹ️  Some operations may require sudo${NC}"
    echo ""
fi

# Define ports
declare -A PORTS
PORTS[8000]="Backend API"
PORTS[3000]="Frontend"
PORTS[5432]="Database"
PORTS[5000]="LLM Wrapper"

# Check and free ports
echo -e "${YELLOW}🔍 Scanning ports...${NC}"
echo ""

all_free=true
for port in "${!PORTS[@]}"; do
    service="${PORTS[$port]}"
    if test_port $port; then
        echo -e "${RED}🔴 Port $port ($service) - IN USE${NC}"
        all_free=false
        kill_process_auto $port || true
    else
        echo -e "${GREEN}✅ Port $port ($service) - FREE${NC}"
    fi
done

echo ""

# Verify all ports are free
sleep 1
not_free=()
for port in "${!PORTS[@]}"; do
    if test_port $port; then
        not_free+=($port)
    fi
done

if [ ${#not_free[@]} -gt 0 ]; then
    echo -e "${RED}❌ These ports are still in use: ${not_free[*]}${NC}"
    echo -e "${RED}Cannot proceed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All ports are FREE and ready!${NC}"
echo ""

# Check Docker
echo -e "${YELLOW}🐳 Checking Docker...${NC}"
if ! docker ps &>/dev/null; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo -e "${RED}   Please start Docker${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check Ollama
echo -e "${YELLOW}🤖 Checking Ollama...${NC}"
if curl -s http://localhost:11434 &>/dev/null; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama may not be running${NC}"
    echo -e "${YELLOW}   Make sure to run: ollama serve${NC}"
fi
echo ""

# Start Docker
echo -e "${BLUE}🚀 Starting Docker services...${NC}"
echo -e "${BLUE}   Command: docker-compose up --build${NC}"
echo ""

docker-compose up --build
