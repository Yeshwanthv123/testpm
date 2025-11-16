# 🔧 Port Management & Configuration Guide

## Problem Summary
- ❌ Port conflicts when running on different machines (Mac/Linux/Windows)
- ❌ Hardcoded port references breaking after port changes
- ❌ Services unable to communicate with each other
- ❌ AI model scoring zero due to no request/response

## Solution: Centralized Port Configuration

### Standard Port Allocation
```
Backend API:        8000
Frontend (Vite):    3000
Database (PostgreSQL): 5432
LLM Wrapper:        5000
Ollama (Host):      11434
```

### Key Principle
**✅ All port configurations come from docker-compose.yml**
- Do NOT hardcode ports in code
- Use environment variables everywhere
- Frontend auto-discovers API base URL

---

## Configuration Files

### 1. docker-compose.yml
- Defines all port mappings
- Sets environment variables for services
- Backend env: `LLM_API_URL=http://pmbot-llm-stub:5000`
- Frontend env: `VITE_API_BASE=http://localhost:8000`

### 2. Backend Configuration
- `config.py`: Reads settings from docker-compose env vars
- `ai_services.py`: Uses `LLM_API_URL` env var to connect to LLM
- All services use env vars, NOT hardcoded ports

### 3. Frontend Configuration
- `utils/api.ts`: Auto-resolves `VITE_API_BASE` from environment
- Priority: Vite env > Window var > Fallback (localhost:8000)
- No hardcoded API URLs

---

## When Ports Need to Change

If port 8000 is already in use, follow this process:

### Step 1: Update docker-compose.yml
```yaml
ports:
  - "8001:8000"  # Changed from 8000:8000 to 8001:8000
```

### Step 2: Update Frontend Environment
```yaml
environment:
  VITE_API_BASE: http://localhost:8001  # Must match host port
```

### Step 3: Restart Services
```bash
docker-compose down
docker-compose up --build
```

**That's it!** Everything else auto-updates via environment variables.

---

## Checking Port Status

### On Mac/Linux
```bash
# Check if port is in use
lsof -i :8000
lsof -i :3000
lsof -i :5000
lsof -i :5432

# Kill process on port
kill -9 <PID>
```

### On Windows
```powershell
# Check if port is in use
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process on port
taskkill /PID <PID> /F
```

---

## Debugging Connection Issues

### 1. Backend Can't Reach LLM
```
Error: Connection refused to http://localhost:5000
Fix: Backend inside container must use service name: http://pmbot-llm-stub:5000
```

### 2. Frontend Can't Reach Backend
```
Error: CORS error or 500 response
Fix: Verify VITE_API_BASE matches actual backend URL
```

### 3. AI Model Returns Zero Score
```
Causes:
- Backend not connected to LLM (check LLM_API_URL)
- LLM service not running
- Request/response not received by AI service

Check:
1. docker exec pmbot-backend curl http://pmbot-llm-stub:5000/health
2. Check backend logs: docker logs pmbot-backend
3. Check LLM logs: docker logs pmbot-llm-stub
```

---

## Before Testing on New Machine

1. **Verify ports are free**
   ```bash
   # All these should be available
   lsof -i :8000
   lsof -i :3000
   lsof -i :5432
   lsof -i :5000
   ```

2. **Clean Docker environment**
   ```bash
   docker-compose down -v  # Remove volumes
   docker system prune -a   # Clean unused images
   ```

3. **Build fresh**
   ```bash
   docker-compose up --build
   ```

4. **Check service health**
   ```bash
   docker exec pmbot-backend curl http://localhost:8000
   docker logs pmbot-backend
   docker logs pmbot-llm-stub
   ```

---

## Environment Variables Reference

### Backend (set in docker-compose.yml)
- `LLM_API_URL`: URL to LLM wrapper (http://pmbot-llm-stub:5000)
- `LLM_MODEL`: Model name (qwen2:7b-instruct)
- `LLM_FORCE`: Force using LLM (1 = yes)
- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: Allowed frontend origins

### Frontend (set in docker-compose.yml)
- `VITE_API_BASE`: Backend API base URL (http://localhost:8000)
- `REACT_APP_API_BASE`: For React projects
- `NEXT_PUBLIC_API_BASE`: For Next.js projects

### LLM Wrapper
- `OLLAMA_URL`: Ollama endpoint (http://host.docker.internal:11434)
- `LLM_MODEL`: Model name

---

## Testing Checklist

- [ ] Port 8000 is free
- [ ] Port 3000 is free
- [ ] Port 5000 is free
- [ ] Port 5432 is free
- [ ] `docker-compose up --build` starts without errors
- [ ] Backend at http://localhost:8000 responds
- [ ] Frontend at http://localhost:3000 loads
- [ ] Backend can reach LLM: `docker exec pmbot-backend curl http://pmbot-llm-stub:5000`
- [ ] AI model shows proper scores (not zero)

