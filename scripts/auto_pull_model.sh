#!/bin/bash
# Ollama Model Auto-Puller - Pure Bash (No Python Required)
# Ensures required AI models are available before starting PMBOT

# Primary and fallback models
PRIMARY_MODEL="qwen2:7b-instruct"
FALLBACK_MODELS=("llama2" "neural-chat" "mistral")
OLLAMA_URL="${LLM_API_URL:-http://localhost:11434}"
MAX_WAIT=120

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check if Ollama is running
check_ollama_running() {
    if command -v curl &> /dev/null; then
        curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1
        return $?
    else
        # Fallback: try with bash TCP
        ( exec 3<>/dev/tcp/localhost/11434 ) 2>/dev/null
        return $?
    fi
}

# Function to wait for Ollama
wait_for_ollama() {
    local elapsed=0
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        if check_ollama_running; then
            echo -e "${GREEN}✅${NC} Ollama is running and accessible"
            return 0
        fi
        
        remaining=$((MAX_WAIT - elapsed))
        echo -e "${YELLOW}⏳${NC} Waiting for Ollama... (${remaining}s remaining)"
        sleep 3
        elapsed=$((elapsed + 3))
    done
    
    echo -e "${RED}❌${NC} Ollama did not respond within timeout"
    return 1
}

# Function to check if model exists
model_exists() {
    local model=$1
    
    if command -v curl &> /dev/null; then
        # Try to get model info
        response=$(curl -s "$OLLAMA_URL/api/show" -d "{\"name\": \"$model\"}" 2>/dev/null)
        if echo "$response" | grep -q "\"name\""; then
            return 0
        fi
    fi
    
    return 1
}

# Function to pull model
pull_model() {
    local model=$1
    
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}❌${NC} ollama command not found"
        echo "   Please install Ollama from https://ollama.ai"
        return 1
    fi
    
    echo -e "${BLUE}📥${NC} Pulling model: $model"
    echo "   This may take 5-15 minutes on first run..."
    echo "   Model size: 4-7GB"
    echo ""
    
    ollama pull "$model" 2>&1 | grep -E "^(pulling|verifying|writing|removing|^$)" || true
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} Successfully pulled $model"
        return 0
    else
        echo -e "${RED}❌${NC} Failed to pull $model"
        return 1
    fi
}

main() {
    echo ""
    echo "============================================================"
    echo -e "${BLUE}🤖 Ollama Model Auto-Setup${NC}"
    echo "============================================================"
    echo "Primary model: $PRIMARY_MODEL"
    echo "Fallback models: ${FALLBACK_MODELS[*]}"
    echo ""
    
    # Check if Ollama is running
    echo -e "${BLUE}🔍${NC} Checking if Ollama is running..."
    if ! wait_for_ollama; then
        echo ""
        echo -e "${RED}❌${NC} Ollama is not running!"
        echo ""
        echo "📋 Setup Instructions:"
        echo "   1. Install Ollama from https://ollama.ai"
        echo "   2. Start Ollama with: ollama serve"
        echo "   3. Keep that terminal open while using PMBOT"
        echo ""
        echo "Or download the model manually:"
        echo "   ollama pull $PRIMARY_MODEL"
        echo ""
        return 1
    fi
    
    echo ""
    
    # Check if primary model exists
    echo -e "${BLUE}🔍${NC} Checking for primary model: $PRIMARY_MODEL..."
    if model_exists "$PRIMARY_MODEL"; then
        echo -e "${GREEN}✅${NC} Model $PRIMARY_MODEL is already available"
        echo ""
        return 0
    fi
    
    # Try to pull primary model
    echo ""
    if pull_model "$PRIMARY_MODEL"; then
        echo ""
        echo -e "${GREEN}✅${NC} $PRIMARY_MODEL is ready!"
        return 0
    fi
    
    # Fallback: try alternative models
    echo ""
    echo -e "${YELLOW}⚠️${NC}  Primary model pull failed. Trying fallback models..."
    
    for fallback in "${FALLBACK_MODELS[@]}"; do
        echo ""
        echo -e "${BLUE}🔄${NC} Checking fallback: $fallback..."
        
        if model_exists "$fallback"; then
            echo -e "${GREEN}✅${NC} Found fallback model: $fallback"
            echo "   (Performance may be reduced, but PMBOT will work)"
            return 0
        fi
        
        echo -e "${BLUE}📥${NC} Pulling fallback model: $fallback..."
        if pull_model "$fallback"; then
            echo ""
            echo -e "${GREEN}✅${NC} $fallback is ready!"
            echo "   (Performance may be reduced, but PMBOT will work)"
            return 0
        fi
    done
    
    # No models available
    echo ""
    echo -e "${RED}❌${NC} No suitable Ollama model found!"
    echo ""
    echo "📋 Quick Fix:"
    echo "   Run in a terminal: ollama pull $PRIMARY_MODEL"
    echo "   Or try: ollama pull llama2"
    echo ""
    return 1
}

main "$@"
exit $?
