# 🎯 AI Model Zero Score - Troubleshooting Guide

## The Problem
After testing, the AI model shows a score of **0** for all answers. This typically means:
- ❌ Backend is not receiving requests from Frontend
- ❌ Backend is not receiving responses from LLM service
- ❌ Port misconfiguration broke the service chain

## The Service Chain (and where it breaks)

```
Frontend (http://localhost:3000)
    ↓
    API Request to /api/interview/evaluate
    ↓
Backend (http://localhost:8000)
    ↓
    Forward to LLM service at http://pmbot-llm-stub:5000
    ↓
LLM Wrapper (http://pmbot-llm-stub:5000)
    ↓
    Connect to Ollama at http://host.docker.internal:11434
    ↓
Ollama (http://localhost:11434 on host)
    ↓
    Process answer with model (qwen2:7b-instruct)
    ↓
    Return score/feedback
```

**If ANY link breaks, score = 0**

---

## Quick Diagnosis

### Step 1: Check Docker Status
```bash
# List all running containers
docker ps

# You should see:
# - pmbot-backend
# - pmbot-frontend
# - pmbot-llm-stub
# - pmbot-db
```

### Step 2: Check Service Health
```bash
# Test backend health
curl http://localhost:8000

# Expected: {"message": "Welcome to the Interview App API"}

# Test LLM wrapper from backend container
docker exec pmbot-backend curl http://pmbot-llm-stub:5000

# Expected: Should return LLM wrapper response
```

### Step 3: Check Logs
```bash
# Backend logs
docker logs pmbot-backend

# LLM logs
docker logs pmbot-llm-stub

# Look for:
# - Connection errors
# - Port errors
# - "Connection refused"
```

---

## Common Issues & Fixes

### Issue 1: Backend Can't Reach LLM

**Symptom:**
```
Error: Connection refused to http://localhost:5000
Error: Failed to connect to pmbot-llm-stub:5000
```

**Cause:**
Backend is looking for LLM on wrong address or LLM service not running

**Fix:**
1. Verify LLM service is running:
   ```bash
   docker ps | grep pmbot-llm-stub
   ```

2. Check docker-compose.yml has correct service name:
   ```yaml
   pmbot-backend:
     environment:
       LLM_API_URL: http://pmbot-llm-stub:5000  # ✅ Use service name, not localhost
   ```

3. Verify network connection from backend:
   ```bash
   docker exec pmbot-backend ping pmbot-llm-stub
   docker exec pmbot-backend curl http://pmbot-llm-stub:5000
   ```

### Issue 2: Frontend Can't Reach Backend

**Symptom:**
```
CORS error in browser console
Network tab shows 500 errors
No response from backend
```

**Cause:**
Frontend API base URL doesn't match backend actual URL

**Fix:**
1. Check docker-compose.yml:
   ```yaml
   pmbot-frontend:
     environment:
       VITE_API_BASE: http://localhost:8000  # Must match host:port
   ```

2. If port changed (e.g., 8001 due to conflict):
   ```yaml
   pmbot-backend:
     ports:
       - "8001:8000"  # Changed from 8000:8000
   
   pmbot-frontend:
     environment:
       VITE_API_BASE: http://localhost:8001  # ✅ Update this too!
   ```

3. Restart:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Issue 3: Ollama Not Responding

**Symptom:**
```
LLM wrapper logs: "Failed to connect to Ollama"
"ConnectionError: Connection refused"
```

**Cause:**
- Ollama not running on host
- Wrong Ollama URL in LLM wrapper

**Fix:**
1. Check Ollama is running:
   ```bash
   curl http://localhost:11434
   # Should return Ollama response
   ```

2. Start Ollama if not running:
   ```bash
   ollama serve
   ```

3. Pull model if missing:
   ```bash
   ollama pull qwen2:7b-instruct
   ```

4. Verify docker-compose.yml has correct Ollama URL:
   ```yaml
   pmbot-llm-stub:
     environment:
       OLLAMA_URL: http://host.docker.internal:11434  # ✅ For Docker Desktop
   ```

### Issue 4: Wrong CSV or Model Path

**Symptom:**
```
FileNotFoundError: CSV not found
ModelNotFoundError
```

**Cause:**
Path mismatch between docker-compose mount and config.py

**Fix:**
1. Check docker-compose.yml mount point:
   ```yaml
   pmbot-backend:
     volumes:
       - ./backend:/backend  # Must be /backend, not /app
     environment:
       PM_QUESTIONS_CSV: /backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv
   ```

2. Check config.py reads correct path:
   ```python
   # In config.py
   env_file = "/backend/.env" if os.path.exists("/backend/.env") else ".env"
   ```

3. Verify file exists:
   ```bash
   docker exec pmbot-backend ls -la /backend/*.csv
   ```

---

## Complete Restart Procedure

When nothing else works, do a full clean restart:

```bash
# 1. Stop all containers
docker-compose down

# 2. Remove volumes (cleans database)
docker-compose down -v

# 3. Remove images (forces rebuild)
docker image remove pmbot-backend pmbot-frontend pmbot-llm-stub

# 4. Prune Docker system
docker system prune -a --volumes

# 5. Check ports are free
netstat -ano | findstr :8000
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# 6. Rebuild and start
docker-compose up --build

# 7. Verify all services
docker ps
docker logs pmbot-backend
docker logs pmbot-llm-stub
```

---

## Testing the Full Chain

### 1. Test Frontend → Backend

Open browser and go to `http://localhost:3000`
- Should load without errors
- Check browser console for errors

### 2. Test Backend Health

```bash
curl http://localhost:8000
# Response: {"message": "Welcome to the Interview App API"}
```

### 3. Test Backend → LLM Connection

```bash
docker exec pmbot-backend python3 -c "
import requests
response = requests.get('http://pmbot-llm-stub:5000')
print('LLM Status:', response.status_code)
"
```

### 4. Test LLM → Ollama Connection

```bash
docker exec pmbot-llm-stub python3 -c "
import requests
response = requests.get('http://host.docker.internal:11434')
print('Ollama Status:', response.status_code)
"
```

### 5. Full Interview Flow Test

1. Go to http://localhost:3000
2. Start an interview
3. Submit an answer
4. Check browser Network tab for `/api/interview/evaluate` request
5. Should see response with score > 0 (not zero)
6. Check backend logs: `docker logs pmbot-backend`

---

## Debug Environment Variables

To see what environment variables each service is using:

```bash
# Backend environment
docker exec pmbot-backend printenv | grep -E "LLM|PORT|DATABASE|API"

# Frontend environment
docker exec pmbot-frontend env | grep -E "VITE|REACT|NEXT"

# LLM environment
docker exec pmbot-llm-stub printenv | grep -E "OLLAMA|MODEL"
```

---

## Prevention Checklist

Before testing on a new machine:

- [ ] Check all 4 ports are free (8000, 3000, 5000, 5432)
- [ ] Ollama is running with qwen2 model loaded
- [ ] docker-compose.yml has `/backend` mount (not `/app`)
- [ ] config.py looks for `/backend/.env` (not `/app/.env`)
- [ ] Frontend VITE_API_BASE matches actual backend port
- [ ] Backend LLM_API_URL points to `pmbot-llm-stub:5000`
- [ ] LLM wrapper OLLAMA_URL points to `host.docker.internal:11434`
- [ ] Database connection string is correct
- [ ] CORS_ORIGINS includes frontend URL

---

## Questions?

Check docker logs first:
```bash
docker logs pmbot-backend 2>&1 | tail -50
docker logs pmbot-llm-stub 2>&1 | tail -50
docker logs pmbot-frontend 2>&1 | tail -50
```

The errors in logs will guide you to the exact problem!
