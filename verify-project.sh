#!/bin/bash
# PM Bot - Project Verification Script
# Ensures all required files and configurations exist

set -e

RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'

echo -e "${BLUE}=================================="
echo "PM Bot - Project Verification"
echo "==================================${RESET}"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}[ERROR] docker-compose.yml not found. Are you in the PMBOTNEW directory?${RESET}"
    exit 1
fi
echo -e "${GREEN}[OK] docker-compose.yml found${RESET}"

# Check required directories
DIRS=("backend" "Frontend" "backend/app" "Frontend/src")

echo ""
echo "Checking directories..."
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}[OK] Directory '$dir' exists${RESET}"
    else
        echo -e "${RED}[ERROR] Directory '$dir' is missing${RESET}"
        exit 1
    fi
done

# Check required files
REQUIRED_FILES=(
    "docker-compose.yml"
    "backend/requirements.txt"
    "backend/Dockerfile"
    "backend/app/main.py"
    "Frontend/package.json"
    "Frontend/Dockerfile"
    "Frontend/src/main.tsx"
)

echo ""
echo "Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}[OK] File '$file' exists${RESET}"
    else
        echo -e "${RED}[ERROR] File '$file' is missing${RESET}"
        exit 1
    fi
done

# Check environment templates
ENV_TEMPLATES=(
    "backend/.env.example"
    "Frontend/.env.example"
)

echo ""
echo "Checking environment templates..."
for file in "${ENV_TEMPLATES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}[OK] Template '$file' exists${RESET}"
    else
        echo -e "${RED}[ERROR] Template '$file' is missing${RESET}"
        exit 1
    fi
done

# Check setup scripts
SETUP_SCRIPTS=(
    "setup.sh"
    "docker-health-check.sh"
    "docker-compose.yml"
)

echo ""
echo "Checking setup scripts..."
for script in "${SETUP_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${GREEN}[OK] Script '$script' exists${RESET}"
    else
        echo -e "${YELLOW}[WARN] Script '$script' is missing${RESET}"
    fi
done

# Check documentation
DOCS=(
    "COMPLETE_SETUP_GUIDE.md"
    "QUICK_START.md"
    "TROUBLESHOOTING.md"
    "README.md"
)

echo ""
echo "Checking documentation..."
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}[OK] Doc '$doc' exists${RESET}"
    else
        echo -e "${YELLOW}[WARN] Doc '$doc' is missing${RESET}"
    fi
done

# Check .gitignore
echo ""
echo "Checking .gitignore..."
if [ -f ".gitignore" ]; then
    echo -e "${GREEN}[OK] .gitignore exists${RESET}"
    
    # Verify .env files are gitignored
    if grep -q "\.env$" .gitignore; then
        echo -e "${GREEN}[OK] .env files are gitignored${RESET}"
    else
        echo -e "${YELLOW}[WARN] .env files may not be gitignored${RESET}"
    fi
else
    echo -e "${YELLOW}[WARN] .gitignore not found${RESET}"
fi

# Check data files
echo ""
echo "Checking data files..."
QUESTION_FILES=(
    "backend/PM_Questions_8000_expanded_clean_final5.csv"
    "backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"
)

FOUND_QUESTIONS=0
for file in "${QUESTION_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}[OK] Questions file found: $(basename $file)${RESET}"
        FOUND_QUESTIONS=1
    fi
done

if [ $FOUND_QUESTIONS -eq 0 ]; then
    echo -e "${YELLOW}[WARN] No PM question files found${RESET}"
    echo "      Questions will be loaded from CSV on first run"
fi

# Check scripts directory
echo ""
echo "Checking scripts..."
if [ -d "scripts" ]; then
    echo -e "${GREEN}[OK] scripts directory exists${RESET}"
    ls scripts/*.sh 2>/dev/null | head -3 | while read script; do
        echo "      $(basename $script)"
    done
else
    echo -e "${YELLOW}[WARN] scripts directory not found${RESET}"
fi

# Summary
echo ""
echo -e "${BLUE}=================================="
echo "Verification Summary"
echo "==================================${RESET}"
echo ""
echo -e "${GREEN}✓ Project structure verified${RESET}"
echo -e "${GREEN}✓ All required files present${RESET}"
echo ""
echo "Project is ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. Review QUICK_START.md"
echo "  2. Run: ./setup.sh"
echo "  3. Open: http://localhost:3000"
echo ""
