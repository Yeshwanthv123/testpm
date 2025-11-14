# PMBOT Troubleshooting Guide

Quick solutions to common problems when setting up or running PMBOT.

## 🚀 Startup Issues

### Issue: "docker: command not found"

**Cause:** Docker is not installed or not in PATH

**Solution:**
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Restart your terminal/PowerShell after installing
3. Verify: `docker --version`

---

### Issue: "docker-compose: command not found"

**Cause:** Docker Compose is not installed or old version

**Solution:**
1. Update Docker Desktop (includes Docker Compose)
2. Or install separately: https://docs.docker.com/compose/install/
3. Verify: `docker compose version`

---

### Issue: "ollama: command not found"

**Cause:** Ollama is not installed

**Solution:**
1. Install Ollama from https://ollama.ai
2. Restart terminal after installing
3. Verify: `ollama --version`

---

### Issue: "Cannot connect to Docker daemon"

**Cause:** Docker daemon is not running

**Solution (Windows/Mac):**
1. Open Docker Desktop application
2. Wait for it to fully start (check icon in taskbar)
3. Try again

**Solution (Linux):**
```bash
sudo systemctl start docker
```

---

## 🔧 Setup Script Issues

### Issue: Setup script says ".env files already exist"

**Cause:** You already ran setup once

**Solution:**
- This is normal! The script won't overwrite existing .env files
- Your .env files are preserved for the next run
- To reset: `rm backend/.env Frontend/.env` then run setup again

---

### Issue: "cp: command not found" on Windows

**Cause:** Running bash commands in PowerShell

**Solution:**
- Use PowerShell setup script instead: `.\scripts\setup.ps1`
- Or use Git Bash terminal (comes with Git for Windows)

---

## 🐳 Docker Issues

### Issue: "Cannot reach host.docker.internal"

**Cause:** Docker can't access your host machine's services

**Windows Docker Desktop:**
- `host.docker.internal` should work automatically
- If not, restart Docker Desktop

**Mac Docker Desktop:**
- Should work automatically (built-in)
- If not, verify Docker settings

**Linux (Docker Engine):**
- `host.docker.internal` doesn't exist on Linux
- Use your machine's IP instead: `192.168.x.x` or `172.17.0.1`
- Update `docker-compose.yml` OLLAMA_URL accordingly

---

### Issue: "Port 3000 is already in use"

**Cause:** Another application is using port 3000

**Solution:**
1. Find what's using port 3000:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   
   # Mac/Linux
   lsof -i :3000
   ```

2. Either:
   - Kill the other process
   - Change port in docker-compose.yml: `3001:3000`
   - Change port in Frontend/.env: `VITE_PORT=3001`

---

### Issue: "Port 8000 is already in use"

**Cause:** Another application is using port 8000

**Solution:**
1. Kill other process or change port in docker-compose.yml
2. If you change it, update Frontend/.env VITE_API_BASE

---

### Issue: "Bind for 0.0.0.0:5432 failed: port is already in use"

**Cause:** PostgreSQL or another database is using port 5432

**Solution:**
```bash
# Option 1: Stop the conflicting service
docker stop <container-name>

# Option 2: Change port in docker-compose.yml
# Change "5432:5432" to "5433:5432" to use port 5433 on host
```

---

### Issue: Services keep restarting/crashing

**Cause:** Usually a configuration or startup error

**Solution:**
```bash
# Check detailed logs
docker compose logs pmbot-backend
docker compose logs pmbot-frontend
docker compose logs pmbot-db
docker compose logs pmbot-llm-stub

# Look for specific error messages
# Common ones:
# - "cannot find module" → missing pip dependencies
# - "connection refused" → service not running
# - "EADDRINUSE" → port already in use
```

---

## 🤖 Ollama & AI Issues

### Issue: "Failed to connect to Ollama" in backend logs

**Cause:** Ollama is not running or not accessible

**Solution:**
1. Start Ollama server:
   ```bash
   ollama serve
   ```
   
2. Verify it's running (separate terminal):
   ```bash
   ollama list
   ```

3. Check it's accessible:
   ```bash
   curl http://localhost:11434/api/tags
   ```

---

### Issue: "Model not found: llama3"

**Cause:** Model not downloaded

**Solution:**
```bash
ollama pull llama3
ollama pull qwen2:7b-instruct

# Verify they're downloaded
ollama list
```

---

### Issue: "Request timeout" in backend logs

**Cause:** LLM inference is taking too long

**Solution:**
1. Wait - first inference is slow as models load
2. Check Ollama is responsive:
   ```bash
   time ollama run llama3 "hello"
   ```

3. If still timing out, verify:
   - Models are fully downloaded: `ollama list`
   - System has enough RAM (8GB+ recommended)
   - Disk space available (models are 4-5GB each)

4. Timeouts are already set to 600 seconds - should be enough

---

### Issue: "Model response is empty" or "Response parsing error"

**Cause:** LLM returned invalid JSON or empty response

**Solution:**
1. Check Ollama is working:
   ```bash
   ollama run qwen2:7b-instruct "Write JSON: {\"test\": true}"
   ```

2. Restart the LLM stub service:
   ```bash
   docker compose restart pmbot-llm-stub
   ```

3. Check for memory issues:
   ```bash
   docker stats
   ```

---

## 🗄️ Database Issues

### Issue: "Connection refused" to database

**Cause:** PostgreSQL container isn't running or healthy

**Solution:**
```bash
# Check database status
docker compose ps pmbot-db

# Check database logs
docker compose logs pmbot-db

# Restart database
docker compose restart pmbot-db

# Wait 10 seconds for health check, then try again
```

---

### Issue: "FATAL: password authentication failed for user 'user'"

**Cause:** Wrong password in connection string

**Solution:**
1. Check `backend/.env` DATABASE_URL matches docker-compose.yml
2. Default is: `postgresql://user:password@db:5432/mydatabase`
3. Database service sets these in environment variables
4. If you changed them, update both places

---

### Issue: "Database does not exist"

**Cause:** Database initialization failed

**Solution:**
```bash
# Remove database volume (CAUTION: deletes data!)
docker compose down -v

# Restart services
docker compose up -d

# Wait for database to initialize
sleep 15

# Verify it's healthy
docker compose ps
```

---

## 🔗 Network & Connection Issues

### Issue: Frontend can't reach backend (CORS error)

**Cause:** Incorrect CORS configuration or API URL

**Solution:**
1. Check Frontend/.env VITE_API_BASE is correct:
   ```
   VITE_API_BASE=http://localhost:8000
   ```

2. Check backend/.env CORS_ORIGINS includes frontend:
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

3. Verify with curl:
   ```bash
   curl http://localhost:8000/health
   ```

4. Rebuild frontend:
   ```bash
   docker compose build pmbot-frontend
   docker compose restart pmbot-frontend
   ```

---

### Issue: "ERR_CONNECTION_REFUSED" when accessing localhost:3000

**Cause:** Frontend container isn't running or didn't start properly

**Solution:**
```bash
# Check if running
docker compose ps pmbot-frontend

# Check logs
docker compose logs pmbot-frontend

# Rebuild and restart
docker compose build pmbot-frontend
docker compose up -d pmbot-frontend

# Wait 10 seconds and try again
```

---

### Issue: Services can't communicate in Docker

**Cause:** Network misconfiguration

**Solution:**
```bash
# Verify network exists
docker network ls
docker network inspect pmbot-net

# Check service connections
docker compose exec pmbot-backend ping pmbot-llm-stub
docker compose exec pmbot-backend ping db

# If pings fail, restart networks
docker compose down
docker compose up -d
```

---

## 📊 Performance Issues

### Issue: Application runs very slowly

**Cause:** Insufficient system resources

**Solution:**
1. Check system resources:
   ```bash
   docker stats
   ```

2. Increase Docker memory allocation:
   - Open Docker Desktop settings
   - Go to Resources
   - Increase available memory (recommend 8GB+)

3. Stop other heavy applications

---

### Issue: LLM responses very slow (>5 minutes)

**Cause:** System loading models into VRAM slowly

**Solution:**
1. Increase Docker memory allocation
2. Increase Docker CPU allocation
3. Close other applications using GPU/CPU
4. First inference is always slower - run again
5. Consider smaller models if system is slow

---

## 🔐 Authentication & Security Issues

### Issue: "Invalid token" or "Unauthorized" errors

**Cause:** JWT token expired or invalid

**Solution:**
1. Clear browser cookies:
   - Open DevTools (F12)
   - Application → Cookies → Delete all
   - Refresh page and log in again

2. Or restart backend (generates new keys):
   ```bash
   docker compose restart pmbot-backend
   ```

---

### Issue: Can't register or login

**Cause:** Usually database or password hashing issue

**Solution:**
1. Verify database is running:
   ```bash
   docker compose exec pmbot-db psql -U user -d mydatabase -c "SELECT 1"
   ```

2. Check backend logs:
   ```bash
   docker compose logs pmbot-backend | grep -i "error\|auth"
   ```

3. Try different email address
4. Restart backend:
   ```bash
   docker compose restart pmbot-backend
   ```

---

## 🔍 Debugging Steps

### General Debugging Workflow

1. **Check service status:**
   ```bash
   docker compose ps
   ```

2. **View relevant logs:**
   ```bash
   docker compose logs <service-name> --tail 50
   ```

3. **Check network connectivity:**
   ```bash
   docker compose exec pmbot-backend curl http://pmbot-llm-stub:5000/health
   ```

4. **Inspect container environment:**
   ```bash
   docker compose exec pmbot-backend env | grep -i <search-term>
   ```

5. **Test specific components:**
   ```bash
   # Backend health
   curl http://localhost:8000/health
   
   # Ollama
   curl http://localhost:11434/api/tags
   
   # LLM wrapper
   docker compose exec pmbot-llm-stub curl localhost:5000/health
   ```

---

### Collecting Logs for Support

If you need help, collect these logs:

```bash
# Full system logs
docker compose logs > logs.txt

# Backend logs only
docker compose logs pmbot-backend > backend.log

# Frontend build logs
docker compose logs pmbot-frontend > frontend.log

# Ollama terminal output (copy from ollama serve terminal)
```

Share these files with support.

---

## 🆘 Still Stuck?

1. **Read SETUP.md** - Has comprehensive guide
2. **Check COMMANDS.md** - Common commands reference
3. **Review docker-compose.yml** - See configuration
4. **Check backend/.env.example** - See all config options
5. **Search error message** - Often found in issues/docs
6. **Run fresh setup** - Sometimes fixes configuration issues
   ```bash
   docker compose down -v
   ./scripts/first-run.sh  # or first-run.ps1
   ```

---

## 📞 Reporting Issues

When reporting an issue, include:

1. **Exact error message** - Copy and paste it
2. **Relevant logs** - `docker compose logs <service>`
3. **What you were doing** - Step-by-step reproduction
4. **Your environment** - Windows/Mac/Linux, Docker version
5. **Steps you've already tried** - So we don't repeat

---

**Last Updated:** November 2025  
**Version:** 1.0.0
