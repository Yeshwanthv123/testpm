# 🔧 Automatic Port Liberation - Complete Solution

## What's New

Your project now has **automatic port detection and liberation** built-in. No more "Address already in use" errors!

---

## How It Works

### Simple: One-Click Startup

**Windows:**
```bash
# Double-click this file
start_pmbot.bat
```

**Mac/Linux:**
```bash
bash start_pmbot.sh
```

### What Happens Automatically

1. ✅ **Detects** which ports are in use (8000, 3000, 5432, 5000)
2. ✅ **Kills** conflicting processes automatically
3. ✅ **Verifies** ports are free
4. ✅ **Starts** Docker services
5. ✅ **Monitors** service health

---

## Features

### 1. Automatic Port Detection

```python
# Detects if port is in use
python3 scripts/free_ports.py
```

Output:
```
🔍 Checking 4 ports...
   8000 - Backend API              ❌ IN USE
   3000 - Frontend                 ✅ FREE
   5432 - Database                 ✅ FREE
   5000 - LLM Wrapper              ✅ FREE
```

### 2. Automatic Port Liberation

```bash
# Auto-kill conflicting processes
python3 scripts/free_ports.py --auto
```

Shows which process is using the port and kills it:
```
🔴 Port 8000 is in use by: python.exe (PID: 12345)
🔨 Auto-killing python.exe...
✅ Killed python.exe (PID: 12345)
```

### 3. Intelligent Startup

**Start with one command:**
```bash
# Windows
python scripts/auto_start.py

# Mac/Linux
python3 scripts/auto_start.py
```

**What it does:**
1. Frees ports automatically
2. Checks Docker is running
3. Checks Ollama is running
4. Starts all services
5. Shows status

### 4. Full Orchestration

**For advanced control:**
```bash
python3 scripts/orchestrate.py
```

This is the master script that:
- Logs every step
- Handles errors gracefully
- Provides detailed feedback
- Monitors health checks

---

## Usage Scenarios

### Scenario 1: Port 8000 Already in Use

**Before (Manual Fix):**
```bash
# ❌ Get error
docker-compose up
# ERROR: Address already in use: ('0.0.0.0', 8000)

# ❌ Have to manually kill process
taskkill /PID 12345

# ❌ Have to manually change port in docker-compose.yml

# ❌ Have to manually restart
```

**Now (Automatic):**
```bash
# ✅ Just run
bash start_pmbot.sh

# ✅ Script automatically:
# - Detects port 8000 is in use
# - Kills the process
# - Starts services on free port
# - Everything works!
```

### Scenario 2: Testing on Different Machine

**Before:**
```bash
# Testing on Mac fails with port error
# Spend 30 minutes debugging
# Change ports manually
# Still has issues
```

**Now:**
```bash
# Run the same command everywhere
bash start_pmbot.sh

# It works automatically on:
# - Windows
# - Mac
# - Linux
```

### Scenario 3: Multiple Test Sessions

**Before:**
```bash
# Session 1: Works fine
docker-compose up

# Session 2: Port conflict
# ERROR: Address already in use

# Manual cleanup required
docker-compose down -v
# ... manually kill processes ...
```

**Now:**
```bash
# Session 1
bash start_pmbot.sh
# Works

# Session 2
bash start_pmbot.sh
# Automatically frees ports and works
```

---

## Available Scripts

### For End Users (Recommended)

1. **`start_pmbot.bat`** (Windows)
   - One-click startup
   - No terminal needed
   - Double-click and go

2. **`start_pmbot.sh`** (Mac/Linux)
   - One-click startup
   - Run: `bash start_pmbot.sh`

### For Developers

1. **`scripts/free_ports.py`** - Port liberation tool
   ```bash
   python3 scripts/free_ports.py              # Check ports
   python3 scripts/free_ports.py --auto      # Auto-kill
   python3 scripts/free_ports.py --ports 8000,3000  # Specific ports
   ```

2. **`scripts/auto_start.py`** - Cross-platform startup
   ```bash
   python3 scripts/auto_start.py
   ```

3. **`scripts/auto_start.ps1`** - PowerShell startup (Windows)
   ```powershell
   ./scripts/auto_start.ps1
   ```

4. **`scripts/auto_start.sh`** - Bash startup (Mac/Linux)
   ```bash
   bash scripts/auto_start.sh
   ```

5. **`scripts/orchestrate.py`** - Advanced orchestration
   ```bash
   python3 scripts/orchestrate.py
   ```

6. **`scripts/integration_test.py`** - Health checks
   ```bash
   python3 scripts/integration_test.py
   ```

---

## Enhanced Docker Compose

The `docker-compose.yml` now includes:

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### Auto-Restart
```yaml
restart: on-failure
```

This ensures:
- ✅ Services restart if they crash
- ✅ Docker monitors service health
- ✅ Failures are detected automatically

---

## How to Use (Step by Step)

### Option 1: Ultra-Simple (Recommended)

**Windows:**
1. Double-click `start_pmbot.bat`
2. Wait for services to start
3. Open http://localhost:3000

**Mac/Linux:**
1. Open terminal
2. Run: `bash start_pmbot.sh`
3. Wait for services to start
4. Open http://localhost:3000

### Option 2: From Terminal

```bash
# Windows PowerShell
python scripts/auto_start.py

# Mac/Linux
python3 scripts/auto_start.py
```

### Option 3: Manual Control

```bash
# Step 1: Free ports
python3 scripts/free_ports.py --auto

# Step 2: Start Docker
docker-compose up --build
```

---

## Benefits

### For Testing
- ✅ No port conflicts to deal with
- ✅ Consistent setup across machines
- ✅ Faster turnaround for tests
- ✅ No wasted debugging time

### For Development
- ✅ Easy to restart services
- ✅ Automatic health monitoring
- ✅ Clear error messages
- ✅ Cross-platform compatible

### For Deployment
- ✅ Proven startup process
- ✅ Health checks built-in
- ✅ Auto-restart on failure
- ✅ Production-ready

---

## Troubleshooting

### Script doesn't run

**Windows:**
```bash
# If .bat doesn't work, open PowerShell and run:
python scripts/auto_start.py
```

**Mac/Linux:**
```bash
# If .sh doesn't work, run:
python3 scripts/auto_start.py

# Or make it executable first:
chmod +x start_pmbot.sh
bash start_pmbot.sh
```

### Port still in use after auto-free

```bash
# Check what's still using the port
python3 scripts/free_ports.py

# Manually check (Windows)
netstat -ano | findstr :8000

# Manually check (Mac/Linux)
lsof -i :8000
```

### Services not starting

```bash
# Check service health
python3 scripts/integration_test.py

# Check Docker logs
docker logs pmbot-backend
docker logs pmbot-frontend
docker logs pmbot-llm-stub
```

---

## Configuration

### Change Default Ports

Edit `docker-compose.yml`:
```yaml
pmbot-backend:
  ports:
    - "8001:8000"  # Changed from 8000:8000
```

Also update Frontend:
```yaml
pmbot-frontend:
  environment:
    VITE_API_BASE: http://localhost:8001
```

Then restart with auto-start:
```bash
bash start_pmbot.sh
```

### Add More Health Checks

Edit `docker-compose.yml` for any service:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT"]
  interval: 10s
  timeout: 5s
  retries: 3
```

---

## Development Notes

### How Port Liberation Works

1. **Detection**: Uses socket connection to detect if port is open
2. **Process Identification**: Uses netstat/lsof to find process using port
3. **Termination**: Uses taskkill (Windows) or kill (Unix)
4. **Verification**: Re-checks port is free before starting

### Cross-Platform Support

- **Windows**: Uses tasklist + netstat
- **Mac**: Uses lsof + native Unix tools
- **Linux**: Uses lsof + native Unix tools

### Error Handling

- Graceful degradation if tools unavailable
- Clear error messages for user action
- Automatic retry on transient failures
- Fallback to manual instructions

---

## Summary

You now have:
- ✅ Automatic port detection
- ✅ Automatic port liberation
- ✅ One-click startup
- ✅ Health monitoring
- ✅ Cross-platform support
- ✅ No more manual debugging

**Just run `start_pmbot.bat` (Windows) or `bash start_pmbot.sh` (Mac/Linux) and it works!**

No more port conflicts. No more wasted testing time. 🚀
