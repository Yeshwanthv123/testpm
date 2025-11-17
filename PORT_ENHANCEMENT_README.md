# PMBOT Port & AI Model Enhancement Guide

## Overview

This document describes the complete port detection and AI model auto-pull system implemented for PMBOT. These enhancements ensure the system works seamlessly across different devices with automatic port conflict resolution and AI model management.

## Key Features

### 1. **Automatic Port Detection** (`scripts/detect_ports.py`)
- ✅ Scans for port conflicts before Docker starts
- ✅ Automatically finds alternative ports if defaults are busy
- ✅ Updates `.env` files with detected ports
- ✅ Saves configuration to `.ports.json` for reference
- ✅ Validates port ranges (1024-65535)
- ✅ Handles edge cases: invalid YAML, missing files, permission errors

**What it does:**
```
1. Reads current port mappings from docker-compose.yml
2. Checks availability of ports 3000 (frontend), 5432 (database), 8000 (backend)
3. Finds alternatives if any port is in use
4. Updates backend/.env with new VITE_API_BASE and DATABASE_URL
5. Updates Frontend/.env with new VITE_API_BASE
6. Saves results to .ports.json
```

**Example output:**
```
🔍 Detecting and configuring ports...

✅ pmbot-backend: Port 8000 available
✅ pmbot-frontend: Port 3000 available
✅ pmbot-db: Port 5432 available

✅ Updated backend/.env
✅ Updated Frontend/.env
✅ Saved port configuration to .ports.json
```

### 2. **Port Configuration Validation** (`scripts/validate_ports.py`)
- ✅ Validates docker-compose.yml port mappings
- ✅ Checks .env files for required variables
- ✅ Verifies port ranges are valid
- ✅ Provides comprehensive error reporting
- ✅ Non-blocking validation (warnings don't stop startup)

**What it validates:**
- Port values are in valid range (1024-65535)
- docker-compose.yml syntax is valid YAML
- Required .env variables exist (VITE_API_BASE, DATABASE_URL, LLM_API_URL)
- .ports.json configuration is consistent

**Run manually:**
```bash
python scripts/validate_ports.py
```

### 3. **AI Model Auto-Pull** (`scripts/auto_pull_model.py`)

**Enhanced features:**
- ✅ Primary model: `qwen2:7b-instruct` (optimized for PM questions)
- ✅ Fallback models: `llama2`, `neural-chat`, `mistral`
- ✅ Waits up to 2 minutes for Ollama to start
- ✅ Tests model capability after download
- ✅ Better error messages and network handling
- ✅ Timeout handling for slow networks

**What it does:**
```
1. Checks if Ollama is running at localhost:11434
2. Waits up to 120 seconds for Ollama to start
3. Checks if qwen2:7b-instruct is already downloaded
4. If not found, pulls from Ollama repository
5. Tests model can generate text responses
6. Falls back to alternative models if needed
```

**Example output:**
```
============================================================
🤖 Ollama Model Auto-Setup
============================================================
Primary model: qwen2:7b-instruct
Fallback models: llama2, neural-chat, mistral

🔍 Checking if Ollama is running...
✅ Ollama is running and accessible

🔍 Checking for primary model: qwen2:7b-instruct...
⏳ Pulling primary model: qwen2:7b-instruct...
   This may take 5-15 minutes on first run...
   Model size: 4-7GB

✅ Model qwen2:7b-instruct is ready!
```

## Quick Start

### Option 1: Automatic (Recommended)

**Windows:**
```batch
start_pmbot.bat
```

**Mac/Linux:**
```bash
./start_pmbot.sh
```

This single command will:
1. ✅ Check Docker is running
2. ✅ Detect available ports
3. ✅ Validate port configuration
4. ✅ Auto-pull AI models
5. ✅ Start all PMBOT services

### Option 2: Manual Steps

```bash
# 1. Detect and configure ports
python scripts/detect_ports.py

# 2. Validate configuration
python scripts/validate_ports.py

# 3. Auto-pull models
python scripts/auto_pull_model.py

# 4. Start Docker Compose
docker-compose up --build
```

## Port Configuration Files

### `.env` Files (Auto-Updated)

**`backend/.env`**
```
VITE_API_BASE=http://localhost:8000
DATABASE_URL=postgresql://postgres:password@localhost:5432/pmbot
LLM_API_URL=http://localhost:11434
```

**`Frontend/.env`**
```
VITE_API_BASE=http://localhost:8000
```

### `.ports.json` (Reference)
Created after first run, documents actual ports being used:
```json
{
  "pmbot-backend": 8000,
  "pmbot-frontend": 3000,
  "pmbot-db": 5432
}
```

## Troubleshooting

### Port Conflicts

**Problem:** "Address already in use"

**Solution:**
```bash
# Detect and fix automatically
python scripts/detect_ports.py

# Or manually find what's using a port (Mac/Linux)
lsof -i :8000

# Kill process on Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Ollama Not Responding

**Problem:** "Ollama did not respond within the timeout period"

**Solution:**
```bash
# Start Ollama in a new terminal
ollama serve

# Then try again
python scripts/auto_pull_model.py
```

### Model Download Failed

**Problem:** "Failed to pull qwen2:7b-instruct"

**Solution:**
```bash
# Download manually
ollama pull qwen2:7b-instruct

# Or try a smaller fallback model
ollama pull llama2

# Then restart PMBOT
./start_pmbot.sh  # or start_pmbot.bat
```

### Docker Compose Error

**Problem:** "docker-compose: command not found"

**Solution:**
- Update Docker Desktop to latest version (includes Docker Compose)
- Or use: `docker compose` instead of `docker-compose`

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Startup Flow                       │
├─────────────────────────────────────────────────────┤
│  1. start_pmbot.sh / start_pmbot.bat               │
│     ↓                                               │
│  2. detect_ports.py                                │
│     ├─ Read docker-compose.yml                    │
│     ├─ Test port availability                     │
│     ├─ Update .env files                          │
│     └─ Save .ports.json                           │
│     ↓                                               │
│  3. validate_ports.py                             │
│     ├─ Validate docker-compose.yml                │
│     ├─ Check .env files                           │
│     └─ Report any issues                          │
│     ↓                                               │
│  4. auto_pull_model.py                            │
│     ├─ Wait for Ollama                            │
│     ├─ Check/pull primary model                   │
│     ├─ Try fallback models if needed              │
│     └─ Test model capability                      │
│     ↓                                               │
│  5. docker-compose up --build                     │
│     ├─ Backend (FastAPI)                          │
│     ├─ Frontend (React)                           │
│     ├─ Database (PostgreSQL)                      │
│     └─ LLM Stub (Ollama wrapper)                  │
└─────────────────────────────────────────────────────┘
```

## Configuration Reference

### Default Ports
| Service | Port | Container Port | Purpose |
|---------|------|----------------|---------|
| Frontend | 3000 | 3000 | React web interface |
| Backend | 8000 | 8000 | FastAPI server |
| Database | 5432 | 5432 | PostgreSQL |

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE` | Backend API URL | `http://localhost:8000` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://postgres:password@localhost:5432/pmbot` |
| `LLM_API_URL` | Ollama server URL | `http://localhost:11434` |

### AI Models
| Model | Size | Quality | Fallback |
|-------|------|---------|----------|
| qwen2:7b-instruct | 4-5GB | Excellent | Primary |
| llama2 | 3.8GB | Good | 1st |
| neural-chat | 4GB | Good | 2nd |
| mistral | 4.1GB | Good | 3rd |

## Advanced Features

### Custom Ports

Edit `docker-compose.yml` to use custom ports:
```yaml
services:
  pmbot-backend:
    ports:
      - "9000:8000"  # Host port 9000 → Container port 8000
```

Then the auto-detection will use port 9000 if available.

### Disable Auto-Pull

If you want to manage models manually:
```bash
# Comment out the auto_pull_model.py line in start_pmbot.sh/.bat
# Then run your own: ollama pull llama2
```

### Multiple Installations

Run multiple instances on different ports:

**Installation 1 (default):**
```bash
# Uses ports 3000, 5432, 8000
./start_pmbot.sh
```

**Installation 2 (alternate):**
```bash
# Edit docker-compose.yml to use ports 3001, 5433, 8001
# Then run
./start_pmbot.sh
```

## Performance Tips

1. **First Run:** Model download takes 5-15 minutes (~4-7GB). Be patient!
2. **Network:** Use stable internet connection for model download
3. **Disk Space:** Ensure 10GB+ free space for Ollama models
4. **Memory:** 8GB+ RAM recommended for model inference
5. **Docker:** Close unused containers to free resources

## Monitoring

Check system status:
```bash
# View active containers
docker ps

# View service logs
docker logs pmbot-backend
docker logs pmbot-frontend
docker logs pmbot-db

# Check port configuration
cat .ports.json

# Test API connectivity
curl http://localhost:8000/health
```

## Support

If issues persist:
1. Check `SOLUTION_SUMMARY.md` for common solutions
2. Review logs: `docker logs <service_name>`
3. Verify Ollama: `curl http://localhost:11434/api/tags`
4. Check ports: `.ports.json` and `docker ps -a`

## Summary

The enhanced PMBOT system now includes:
- ✅ **Automatic port conflict detection and resolution**
- ✅ **Port configuration validation**
- ✅ **Automatic AI model downloading and fallback support**
- ✅ **Comprehensive error handling for edge cases**
- ✅ **Non-blocking validation (system continues on warnings)**
- ✅ **Cross-platform support (Windows, Mac, Linux)**
- ✅ **Single-command startup with full automation**

This makes PMBOT truly portable and easy to deploy on any machine! 🚀
