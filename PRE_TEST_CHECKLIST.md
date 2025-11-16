# ✅ Pre-Test Checklist - Never Waste Testing Time Again

Use this checklist **BEFORE** every testing session to ensure everything is properly configured.

## 🟢 Day Before Testing

### System Preparation
- [ ] Restart your machine (clears port locks, orphaned processes)
- [ ] Verify all tools are installed:
  - [ ] Docker Desktop installed and working
  - [ ] Ollama installed on host machine
  - [ ] Python 3.8+ installed (for diagnostic scripts)
- [ ] Pull latest code from repository
  ```bash
  git pull origin main
  ```

### Ollama Setup
- [ ] Start Ollama service
  ```bash
  ollama serve  # Keep running
  ```
- [ ] Verify Ollama is accessible
  ```bash
  curl http://localhost:11434
  ```
- [ ] Pull the model
  ```bash
  ollama pull qwen2:7b-instruct
  ```
- [ ] Verify model is pulled
  ```bash
  ollama list
  # Should show: qwen2:7b-instruct
  ```

### Docker Cleanup
```bash
# Clean up previous containers/images
docker-compose down -v
docker system prune -a
```

---

## 🟡 1 Hour Before Testing

### Port Verification
```bash
# Check ports are free
python3 scripts/diagnose_ports.py
```

Expected output:
```
🔗 Port Status:
   8000 - Backend API              ✅ FREE
   3000 - Frontend (Vite)          ✅ FREE
   5432 - PostgreSQL               ✅ FREE
   5000 - LLM Wrapper              ✅ FREE
  11434 - Ollama (host)            ✅ FREE
```

**If any port is IN USE:**
1. Follow "Port Conflict Resolution" section below
2. DO NOT SKIP THIS - it's why testing failed last time

### Configuration Verification
- [ ] Check `docker-compose.yml` has correct paths
  ```bash
  # Verify backend mount is /backend, not /app
  grep "- ./backend:" docker-compose.yml
  ```
  
- [ ] Verify frontend API base URL
  ```bash
  # Should show: VITE_API_BASE: http://localhost:8000
  grep "VITE_API_BASE:" docker-compose.yml
  ```

- [ ] Verify LLM configuration
  ```bash
  # Should show: LLM_API_URL: http://pmbot-llm-stub:5000
  grep "LLM_API_URL:" docker-compose.yml
  ```

---

## 🟠 30 Minutes Before Testing

### Docker Build & Start

**Option 1: Automatic (Recommended)**
```powershell
# Windows
./scripts/smart_start.ps1

# OR All platforms
python3 scripts/smart_start.py
```

**Option 2: Manual**
```bash
docker-compose up --build
```

**What to look for in output:**
```
✅ DO see these lines:
- "database system is ready to accept connections"
- "Application startup complete"
- "Uvicorn running on http://0.0.0.0:8000"

❌ DO NOT see these:
- "Address already in use"
- "Connection refused"
- "Cannot connect to Ollama"
```

If you see errors:
1. STOP (Ctrl+C)
2. Check port conflicts: `python3 scripts/diagnose_ports.py`
3. Check logs: `docker logs pmbot-backend`
4. Fix the issue BEFORE continuing

---

## 🔵 15 Minutes Before Testing

### Service Integration Verification

Run the integration test:
```bash
python3 scripts/integration_test.py
```

Expected output:
```
🔍 PMBOT Integration Test

✅ PASS - Backend Health
✅ PASS - Frontend Accessibility  
✅ PASS - Environment Variables
✅ PASS - Backend → LLM Connection
✅ PASS - LLM → Ollama Connection
✅ PASS - Database Connection
✅ PASS - API Endpoint

🎉 All tests passed! System is ready.
```

**If ANY test FAILS:**
- ❌ DO NOT PROCEED TO TESTING
- Read the error message carefully
- Check the troubleshooting guide: `AI_MODEL_ZERO_SCORE_FIX.md`
- Fix the issue first
- Re-run integration test
- Only proceed when ALL tests pass

### Website Access Verification

**In browser:**
- [ ] Open http://localhost:3000
- [ ] Page should load (no blank screen)
- [ ] Check browser console (F12 → Console tab)
  - [ ] NO red errors about API connection
  - [ ] NO CORS errors

**If page is blank or errors:**
1. Check backend is running: `docker logs pmbot-backend`
2. Verify VITE_API_BASE: `docker exec pmbot-frontend printenv VITE_API_BASE`
3. If issues, restart: `docker-compose down && docker-compose up --build`

---

## 🟢 Testing in Progress

### Monitor Logs in Separate Terminal

**Terminal 1: Keep running**
```bash
docker-compose logs -f
```

**As you test, look for:**
- ✅ API requests appear in logs
- ✅ No "Connection refused" messages
- ✅ No 500 errors

### Quick Test: Submit One Answer

1. Start interview
2. Submit one answer
3. Check score (should NOT be zero)
4. Check logs for errors

**If score is zero:**
1. STOP testing
2. Check logs: `docker logs pmbot-backend | tail -50`
3. Look for LLM connection errors
4. Follow `AI_MODEL_ZERO_SCORE_FIX.md` troubleshooting
5. Do NOT continue with full testing until fixed

---

## 🔴 Port Conflict Resolution (If Needed)

### Scenario: Port 8000 in Use

**Diagnostic output shows:**
```
❌ Port 8000 (Backend) is IN USE
   Process: python.exe (PID: 12345)
```

**Fix:**

1. **Kill the process** (if it's not important)
   ```powershell
   # Windows
   taskkill /PID 12345 /F
   
   # Mac/Linux
   kill -9 12345
   ```

   OR

2. **Use different port** (if process should stay running)

   Edit `docker-compose.yml`:
   ```yaml
   pmbot-backend:
     ports:
       - "8001:8000"  # Changed from 8000:8000
   ```

   Edit same file, frontend section:
   ```yaml
   pmbot-frontend:
     environment:
       VITE_API_BASE: http://localhost:8001  # Must match host port
   ```

   Then restart:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

3. **Re-verify**
   ```bash
   python3 scripts/integration_test.py
   ```

---

## 📋 Complete Pre-Test Rundown

**The Quick Version** (10 minutes):
```bash
# 1. Check ports
python3 scripts/diagnose_ports.py

# 2. Stop and clean
docker-compose down -v

# 3. Start Docker
python3 scripts/smart_start.py

# 4. Wait for startup (2 minutes)
# Watch for "Application startup complete"

# 5. Verify services
python3 scripts/integration_test.py

# 6. Browser test
# Open http://localhost:3000
# Should load without errors
```

**Expected time:** 10-15 minutes total

---

## 🚨 If Something Still Goes Wrong

### Step-by-Step Debug

1. **Stop everything**
   ```bash
   docker-compose down
   ```

2. **Check what's wrong**
   ```bash
   # Check ports
   python3 scripts/diagnose_ports.py
   
   # Check environment
   docker-compose config
   
   # Check logs
   docker logs pmbot-backend 2>&1 | tail -100
   ```

3. **Consult guides**
   - Zero scores → Read `AI_MODEL_ZERO_SCORE_FIX.md`
   - Port issues → Read `PORT_MANAGEMENT_GUIDE.md`
   - General help → Read `IMPLEMENTATION_GUIDE.md`

4. **Full reset** (last resort)
   ```bash
   # Remove everything
   docker-compose down -v
   docker system prune -a --volumes
   
   # Restart Ollama on host
   ollama serve
   
   # Start fresh
   python3 scripts/smart_start.py
   ```

---

## 📊 Success Criteria

✅ **You are ready to test when:**
- All ports are FREE (diagnose_ports.py shows green)
- All integration tests PASS (all 7 tests show ✅)
- Frontend loads without errors (http://localhost:3000)
- Browser console shows NO red errors
- You can see Docker logs flowing (docker-compose logs -f)

❌ **Do NOT test if:**
- Any diagnostic test FAILS
- Browser shows errors in console
- Backend logs show connection errors
- Integration test shows ❌ FAIL for any test

---

## Time Savings Summary

This checklist should take **15-20 minutes MAX** before testing.

**What you've prevented:**
- ❌ 1+ hour of debugging port conflicts (PREVENTED)
- ❌ Testing with wrong API URLs (PREVENTED)
- ❌ AI model returning zero scores (PREVENTED)
- ❌ Services unable to communicate (PREVENTED)

**Your testing will now:**
- ✅ Start cleanly
- ✅ Run smoothly
- ✅ Give accurate results
- ✅ Not be a waste of time

---

## Helpful Commands Reference

```bash
# Check ports
python3 scripts/diagnose_ports.py

# Run tests
python3 scripts/integration_test.py

# View logs
docker logs pmbot-backend
docker logs pmbot-llm-stub
docker logs pmbot-frontend

# Check containers
docker ps

# Get into backend container
docker exec -it pmbot-backend bash

# Get environment variables
docker exec pmbot-backend printenv | grep LLM

# Test service connectivity
docker exec pmbot-backend curl http://pmbot-llm-stub:5000

# Restart everything
docker-compose down -v
docker-compose up --build

# Check Docker health
docker-compose ps
```

---

## Questions?

1. **Port issues?** → `PORT_MANAGEMENT_GUIDE.md`
2. **Zero scores?** → `AI_MODEL_ZERO_SCORE_FIX.md`
3. **General help?** → `IMPLEMENTATION_GUIDE.md`
4. **Commands?** → Check "Helpful Commands Reference" above

**Remember:** Take 15-20 minutes to verify everything works BEFORE testing.
It's way faster than debugging for hours after testing fails.

Good luck! 🚀
