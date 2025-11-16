# 🔧 Port & Configuration Fixes - Complete Guide

## What Was Fixed

### 1. **Path Mismatch Issue** ✅
**Problem:** Config.py was looking for `/app/.env` but docker-compose mounts to `/backend`
- **File Changed:** `backend/app/config.py` 
- **Fix:** Updated env_file path from `/app/.env` to `/backend/.env`
- **Impact:** Backend can now properly read environment variables in Docker

### 2. **Port Conflict Prevention** ✅
**Problem:** No mechanism to detect or handle port conflicts on different machines
- **Files Created:**
  - `scripts/diagnose_ports.py` - Python script to check port availability
  - `scripts/smart_start.ps1` - PowerShell script with port conflict detection
  - `scripts/smart_start.py` - Python universal startup script
- **Impact:** Automatic detection of port conflicts before starting Docker

### 3. **Documentation & Guides** ✅
**Problem:** No clear guidance on how to handle port changes
- **Files Created:**
  - `PORT_MANAGEMENT_GUIDE.md` - Complete port management strategy
  - `AI_MODEL_ZERO_SCORE_FIX.md` - Troubleshooting guide for zero scores
  - This file - Implementation and next steps
- **Impact:** Step-by-step instructions for every scenario

### 4. **Integration Testing** ✅
**Problem:** No way to verify all services are connected properly
- **File Created:** `scripts/integration_test.py` - Comprehensive service verification
- **Impact:** Can verify the entire service chain works before testing

---

## How to Use These Fixes

### Step 1: Check Port Availability (BEFORE starting Docker)

**On Windows:**
```powershell
python scripts/diagnose_ports.py
```

**On Mac/Linux:**
```bash
python3 scripts/diagnose_ports.py
```

This will show:
```
🔍 PMBOT Port & Service Diagnostic
============================================================

📦 Docker Status:
✅ Docker is running

🔗 Port Status:
────────────────────────────────────────────────────────
   8000 - Backend API                      ✅ FREE
   3000 - Frontend (Vite)                  ✅ FREE
   5432 - PostgreSQL                       ✅ FREE
   5000 - LLM Wrapper                      ✅ FREE
  11434 - Ollama (host)                    ✅ FREE
────────────────────────────────────────────────────────

✅ All ports are available! Safe to start Docker.
```

### Step 2: Start Docker with Smart Port Detection

**Option A: Using PowerShell (Windows)**
```powershell
./scripts/smart_start.ps1
```

**Option B: Using Python (All platforms)**
```bash
python3 scripts/smart_start.py
```

**Option C: Manual Docker (if you know ports are free)**
```bash
docker-compose up --build
```

### Step 3: Verify All Services Are Connected

**After Docker successfully starts:**
```bash
python3 scripts/integration_test.py
```

Expected output:
```
🔍 PMBOT Integration Test
============================================================

✅ PASS - Backend Health
✅ PASS - Frontend Accessibility
✅ PASS - Environment Variables
✅ PASS - Backend → LLM Connection
✅ PASS - LLM → Ollama Connection
✅ PASS - Database Connection
✅ PASS - API Endpoint

🎉 All tests passed! System is ready.
```

---

## If Ports Are In Use (What to Do)

### Scenario 1: Port 8000 is Already in Use

The diagnostic script will show:
```
❌ Port 8000 (Backend) is IN USE
   Process: chrome.exe (PID: 12345)
   Suggestion: Use port 8001
```

**Fix:**

1. **Edit `docker-compose.yml`:**
   ```yaml
   pmbot-backend:
     ports:
       - "8001:8000"  # Changed from 8000:8000
   ```

2. **Edit `docker-compose.yml` frontend section:**
   ```yaml
   pmbot-frontend:
     environment:
       VITE_API_BASE: http://localhost:8001  # Must match host port
   ```

3. **Restart:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Scenario 2: Multiple Ports Are In Use

The diagnostic will suggest free ports. Use the same process for each:
- Change port in docker-compose.yml
- Update corresponding environment variable
- Restart Docker

---

## Understanding the Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Vite)                       │
│               http://localhost:3000                      │
│              Container Port: 3000                        │
└────────────────────────────┬────────────────────────────┘
                             │
                    API Request (HTTP)
                    /api/interview/*
                             │
                             ↓
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│               http://localhost:8000                      │
│              Container Port: 8000                        │
│                                                          │
│  Environment Variables (from docker-compose):           │
│  - LLM_API_URL=http://pmbot-llm-stub:5000  ✅ Service name │
│  - LLM_MODEL=qwen2:7b-instruct                          │
│  - LLM_FORCE=1                                          │
└────────────────────────────┬────────────────────────────┘
                             │
                    Internal Docker Network
                  (uses service names, not localhost)
                             │
                             ↓
┌─────────────────────────────────────────────────────────┐
│              LLM WRAPPER (Flask)                         │
│          http://pmbot-llm-stub:5000                     │
│          Container Port: 5000                           │
│                                                          │
│  Environment Variables:                                 │
│  - OLLAMA_URL=http://host.docker.internal:11434  ✅ Host│
└────────────────────────────┬────────────────────────────┘
                             │
                    Escape Docker to Host
                 (host.docker.internal)
                             │
                             ↓
┌─────────────────────────────────────────────────────────┐
│                 OLLAMA (Host Machine)                    │
│               http://localhost:11434                    │
│  Must be running on host before Docker starts           │
│                    (NOT in Docker)                       │
└─────────────────────────────────────────────────────────┘
```

**Critical Points:**
- ✅ Within Docker: Use service names (pmbot-llm-stub)
- ✅ From Host: Use localhost (http://localhost:8000)
- ✅ Escaping Docker: Use host.docker.internal

---

## Troubleshooting Checklist

Before assuming something is broken, verify:

### Before Starting Docker
- [ ] Run `python3 scripts/diagnose_ports.py`
- [ ] All 4 ports are FREE (8000, 3000, 5000, 5432)
- [ ] Ollama is running: `ollama serve`
- [ ] Qwen2 model is pulled: `ollama pull qwen2:7b-instruct`

### After Docker Starts
- [ ] Run `python3 scripts/integration_test.py`
- [ ] All tests should pass (green ✅)
- [ ] Check backend logs: `docker logs pmbot-backend`
- [ ] Check LLM logs: `docker logs pmbot-llm-stub`

### If Tests Fail
1. Check which test failed
2. Read the error message carefully
3. Follow the suggested fix
4. Consult `AI_MODEL_ZERO_SCORE_FIX.md` for detailed troubleshooting

---

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Address already in use" | Run diagnose_ports.py, change port in docker-compose.yml |
| "Connection refused" | Make sure Docker container is running: `docker ps` |
| "AI model score is 0" | Run integration_test.py to find which connection failed |
| "Frontend blank page" | Check browser console errors, verify VITE_API_BASE |
| "CORS error" | Verify CORS_ORIGINS in docker-compose.yml includes frontend URL |
| "Cannot connect to Ollama" | Ensure Ollama is running on host: `ollama serve` |

---

## Files Changed/Created

### Modified Files
1. **`backend/app/config.py`**
   - Changed: `/app/.env` → `/backend/.env`
   - Reason: Match docker-compose mount point

### New Files Created
1. **`PORT_MANAGEMENT_GUIDE.md`** - Strategic guide for port management
2. **`AI_MODEL_ZERO_SCORE_FIX.md`** - Comprehensive troubleshooting guide
3. **`IMPLEMENTATION_GUIDE.md`** - This file
4. **`scripts/diagnose_ports.py`** - Port availability checker
5. **`scripts/smart_start.ps1`** - Windows PowerShell startup script
6. **`scripts/smart_start.py`** - Python startup script (all platforms)
7. **`scripts/integration_test.py`** - Service connectivity verifier

---

## Next Steps

### For Your Next Test Session

1. **Before starting:**
   ```bash
   python3 scripts/diagnose_ports.py
   ```

2. **Start Docker:**
   ```bash
   ./scripts/smart_start.ps1  # Windows
   # OR
   python3 scripts/smart_start.py  # All platforms
   ```

3. **Verify all services:**
   ```bash
   python3 scripts/integration_test.py
   ```

4. **Run interview test:**
   - Open http://localhost:3000
   - Go through interview flow
   - Verify scores are NOT zero

### If Something Goes Wrong

1. **Stop everything:**
   ```bash
   docker-compose down
   ```

2. **Diagnose:**
   ```bash
   python3 scripts/integration_test.py
   ```

3. **Check logs:**
   ```bash
   docker logs pmbot-backend 2>&1 | tail -50
   docker logs pmbot-llm-stub 2>&1 | tail -50
   ```

4. **Refer to troubleshooting guides:**
   - `AI_MODEL_ZERO_SCORE_FIX.md` for connection issues
   - `PORT_MANAGEMENT_GUIDE.md` for port-related issues

---

## Key Takeaways

### Root Causes of Your Previous Issues
1. **Port conflicts not detected** → Fixed with diagnose_ports.py
2. **Path mismatches** → Fixed in config.py
3. **No verification of service connectivity** → Fixed with integration_test.py
4. **Manual port changes broke everything** → Fixed with proper docs and scripts

### How These Fixes Prevent Future Issues
- ✅ Automatic port conflict detection
- ✅ Clear instructions for port changes
- ✅ Automated verification that everything works
- ✅ Comprehensive troubleshooting guides
- ✅ Environment variables properly configured

### Remember
- **Change ONE port** → Update BOTH docker-compose AND frontend env
- **Test BEFORE debugging** → Run integration_test.py first
- **Check logs FIRST** → Errors in logs explain 90% of problems
- **Use service names in Docker** → pmbot-llm-stub, not localhost

---

## Questions?

1. Check `PORT_MANAGEMENT_GUIDE.md` for port strategy
2. Check `AI_MODEL_ZERO_SCORE_FIX.md` for connection issues
3. Run `scripts/integration_test.py` to identify problems
4. Check docker logs: `docker logs pmbot-backend`

Good luck with your next test! 🚀
