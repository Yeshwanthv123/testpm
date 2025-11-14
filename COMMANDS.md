#!/bin/bash
# PMBOT Quick Reference - Common Commands

# ============================================
# 🚀 INITIAL SETUP (First Time Only)
# ============================================

# 1. Clone repository
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW

# 2. Generate .env files from templates
bash scripts/setup.sh         # Mac/Linux
# OR
.\scripts\setup.ps1           # Windows PowerShell

# 3. Prepare Ollama on host
ollama serve                  # Terminal 1: Start Ollama server
ollama pull llama3            # Terminal 2: Download models
ollama pull qwen2:7b-instruct

# 4. Build and start Docker services
docker compose up --build


# ============================================
# 🔄 DAILY OPERATIONS
# ============================================

# Start services (Ollama must be running on host)
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose stop

# Stop and remove containers
docker compose down

# Rebuild after code changes
docker compose build

# Rebuild specific service
docker compose build pmbot-backend
docker compose build pmbot-frontend

# Full restart
docker compose restart


# ============================================
# 📊 MONITORING & LOGS
# ============================================

# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f pmbot-backend
docker compose logs -f pmbot-frontend
docker compose logs -f pmbot-llm-stub
docker compose logs -f pmbot-db

# Last 50 lines of logs
docker compose logs --tail 50 pmbot-backend

# Show running containers
docker compose ps

# View container details
docker compose exec pmbot-backend sh
docker compose exec pmbot-frontend sh


# ============================================
# ✅ TESTING & VERIFICATION
# ============================================

# Check backend is running
curl http://localhost:8000/health

# List Ollama models
ollama list

# Check Ollama is accessible
curl http://localhost:11434/api/tags

# Test API endpoint
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'


# ============================================
# 🗑️ CLEANUP & RESET
# ============================================

# Remove all containers (keeps images)
docker compose down

# Remove containers AND volumes (deletes database!)
docker compose down -v

# Remove all PMBOT images
docker image rm pmbotnew-pmbot-backend
docker image rm pmbotnew-pmbot-frontend
docker image rm pmbotnew-pmbot-llm-stub

# Clean up ALL Docker resources (use with caution!)
docker system prune -a

# Rebuild everything from scratch
docker compose down -v
docker compose build --no-cache
docker compose up


# ============================================
# 📝 DEVELOPMENT
# ============================================

# View file in container
docker compose exec pmbot-backend cat /backend/app/main.py

# Run Python command in backend
docker compose exec pmbot-backend python -c "import sys; print(sys.version)"

# Install additional Python package
docker compose exec pmbot-backend pip install requests

# Run backend tests
docker compose exec pmbot-backend pytest

# Run frontend dev server
docker compose exec pmbot-frontend npm run dev


# ============================================
# 🔍 TROUBLESHOOTING
# ============================================

# Check network connectivity
docker network ls
docker network inspect pmbot-net

# Inspect container
docker inspect pmbot-backend

# Check resource usage
docker stats

# View container environment
docker compose exec pmbot-backend env

# Check if port is in use
netstat -ano | findstr :8000
netstat -ano | findstr :3000
netstat -ano | findstr :5432

# See what's using Ollama port
netstat -ano | findstr :11434


# ============================================
# 🐛 DEBUG REQUESTS
# ============================================

# Test LLM wrapper directly
curl http://localhost:5000/health

# Test database connection
docker compose exec pmbot-db psql -U user -d mydatabase -c "SELECT 1"

# Check environment variables
docker compose exec pmbot-backend env | grep -i ollama
docker compose exec pmbot-backend env | grep -i database


# ============================================
# 📦 DATABASE OPERATIONS
# ============================================

# Access PostgreSQL shell
docker compose exec pmbot-db psql -U user -d mydatabase

# Backup database
docker compose exec pmbot-db pg_dump -U user mydatabase > backup.sql

# Restore database
docker compose exec -T pmbot-db psql -U user mydatabase < backup.sql

# Drop and recreate database
docker compose exec pmbot-db psql -U user -c "DROP DATABASE IF EXISTS mydatabase;"
docker compose exec pmbot-db psql -U user -c "CREATE DATABASE mydatabase;"


# ============================================
# 🚀 PRODUCTION CHECKS
# ============================================

# Verify all services are healthy
docker compose ps

# Check response times
time curl http://localhost:8000/health

# Load test (simple)
for i in {1..10}; do curl http://localhost:8000/health; done

# Check logs for errors
docker compose logs | grep -i error
docker compose logs | grep -i exception
docker compose logs | grep -i warning
