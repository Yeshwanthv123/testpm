#!/bin/bash
# Port Detection and Configuration - Pure Bash (No Python Required)
# Auto-detects available ports and updates .env files

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Default ports
DEFAULT_BACKEND_PORT=8000
DEFAULT_FRONTEND_PORT=3000
DEFAULT_DB_PORT=5432

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is available
is_port_available() {
    local port=$1
    if command -v nc &> /dev/null; then
        # Use nc if available
        ! nc -z 127.0.0.1 "$port" 2>/dev/null
    elif command -v timeout &> /dev/null; then
        # Fallback: try with bash TCP redirection
        ( exec 3<>/dev/tcp/127.0.0.1/"$port" ) 2>/dev/null && return 1 || return 0
    else
        # If no tools available, assume port is available
        return 0
    fi
}

# Function to find available port
find_available_port() {
    local preferred=$1
    local start=$((preferred - 100))
    local end=$((preferred + 100))
    
    # Validate ranges
    [[ $start -lt 1024 ]] && start=1024
    [[ $end -gt 65535 ]] && end=65535
    
    # Try preferred port first
    if is_port_available "$preferred"; then
        echo "$preferred"
        return 0
    fi
    
    # Try ports around preferred
    for offset in {1..50}; do
        local port=$((preferred + offset))
        if [[ $port -le $end ]] && is_port_available "$port"; then
            echo "$port"
            return 0
        fi
        
        port=$((preferred - offset))
        if [[ $port -ge $start ]] && is_port_available "$port"; then
            echo "$port"
            return 0
        fi
    done
    
    # Fallback to preferred if can't detect
    echo "$preferred"
}

# Function to update .env file
update_env_var() {
    local file=$1
    local var=$2
    local value=$3
    
    if [ ! -f "$file" ]; then
        # Create file if it doesn't exist
        mkdir -p "$(dirname "$file")"
        echo "$var=$value" >> "$file"
    else
        # Update existing var or add new one
        if grep -q "^$var=" "$file"; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s|^$var=.*|$var=$value|" "$file"
            else
                sed -i "s|^$var=.*|$var=$value|" "$file"
            fi
        else
            echo "$var=$value" >> "$file"
        fi
    fi
}

main() {
    echo ""
    echo "🔍 Detecting and configuring ports..."
    echo ""
    
    # Detect available ports
    BACKEND_PORT=$(find_available_port "$DEFAULT_BACKEND_PORT")
    FRONTEND_PORT=$(find_available_port "$DEFAULT_FRONTEND_PORT")
    DB_PORT=$(find_available_port "$DEFAULT_DB_PORT")
    
    # Display detected ports
    [[ "$BACKEND_PORT" == "$DEFAULT_BACKEND_PORT" ]] && echo -e "${GREEN}✅${NC} Backend: Port $BACKEND_PORT available" || echo -e "${YELLOW}⚠️${NC}  Backend: Port $DEFAULT_BACKEND_PORT → $BACKEND_PORT"
    [[ "$FRONTEND_PORT" == "$DEFAULT_FRONTEND_PORT" ]] && echo -e "${GREEN}✅${NC} Frontend: Port $FRONTEND_PORT available" || echo -e "${YELLOW}⚠️${NC}  Frontend: Port $DEFAULT_FRONTEND_PORT → $FRONTEND_PORT"
    [[ "$DB_PORT" == "$DEFAULT_DB_PORT" ]] && echo -e "${GREEN}✅${NC} Database: Port $DB_PORT available" || echo -e "${YELLOW}⚠️${NC}  Database: Port $DEFAULT_DB_PORT → $DB_PORT"
    
    # Update .env files
    echo ""
    echo "📝 Updating configuration files..."
    
    BACKEND_ENV="$PROJECT_ROOT/backend/.env"
    FRONTEND_ENV="$PROJECT_ROOT/Frontend/.env"
    
    update_env_var "$BACKEND_ENV" "VITE_API_BASE" "http://localhost:$BACKEND_PORT"
    update_env_var "$BACKEND_ENV" "DATABASE_URL" "postgresql://postgres:password@localhost:$DB_PORT/pmbot"
    update_env_var "$BACKEND_ENV" "LLM_API_URL" "http://localhost:11434"
    
    update_env_var "$FRONTEND_ENV" "VITE_API_BASE" "http://localhost:$BACKEND_PORT"
    
    echo -e "${GREEN}✅${NC} Updated $BACKEND_ENV"
    echo -e "${GREEN}✅${NC} Updated $FRONTEND_ENV"
    
    # Save port config
    PORTS_JSON="$PROJECT_ROOT/.ports.json"
    cat > "$PORTS_JSON" << EOF
{
  "backend": $BACKEND_PORT,
  "frontend": $FRONTEND_PORT,
  "database": $DB_PORT
}
EOF
    echo -e "${GREEN}✅${NC} Saved port configuration to .ports.json"
    echo ""
}

main "$@"
