#!/bin/bash
# PM Bot - Fix Port Conflicts Script for Unix/Linux/macOS
# Automatically finds and kills processes using required ports

RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'

echo -e "${BLUE}=================================="
echo "PM Bot - Port Conflict Fixer"
echo "==================================${RESET}"
echo ""

# Define ports
PORTS=(3000 8000 5432 5000)

echo "Checking for processes using required ports..."
echo ""

# Check each port
for PORT in "${PORTS[@]}"; do
    echo "Checking port $PORT..."
    
    # Find process using the port
    if command -v lsof &> /dev/null; then
        # Using lsof (preferred method)
        PID=$(lsof -i :$PORT -t 2>/dev/null)
        if [ -n "$PID" ]; then
            echo -e "${YELLOW}  Found process using port $PORT (PID: $PID)${RESET}"
            echo "  Killing process $PID..."
            kill -9 $PID 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  [OK] Process killed${RESET}"
            else
                echo -e "${RED}  [WARN] Could not kill process (may need sudo)${RESET}"
            fi
        else
            echo -e "${GREEN}  [OK] Port $PORT is free${RESET}"
        fi
    else
        # Fallback to netstat
        PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $NF}' | cut -d'/' -f1)
        if [ -n "$PID" ] && [ "$PID" != "-" ]; then
            echo -e "${YELLOW}  Found process using port $PORT (PID: $PID)${RESET}"
            echo "  Killing process $PID..."
            kill -9 $PID 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  [OK] Process killed${RESET}"
            else
                echo -e "${RED}  [WARN] Could not kill process (may need sudo)${RESET}"
            fi
        else
            echo -e "${GREEN}  [OK] Port $PORT is free${RESET}"
        fi
    fi
done

echo ""
echo -e "${BLUE}=================================="
echo "Port Check Complete"
echo "==================================${RESET}"
echo ""
echo "All PM Bot ports should now be available:"
echo "  Port 3000  (Frontend)"
echo "  Port 8000  (Backend)"
echo "  Port 5432  (Database)"
echo "  Port 5000  (LLM Service)"
echo ""
echo "You can now run: ./setup.sh"
echo ""
