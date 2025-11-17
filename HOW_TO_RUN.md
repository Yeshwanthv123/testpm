# ✅ Everything Works! Here's How to Run PMBOT

## Simplest Way (Just Click or Run One Command)

### Windows 🪟
```
1. Double-click: start_pmbot.bat
   OR
2. Run in terminal: start_pmbot.bat
```

### Mac/Linux 🍎🐧
```
1. Run in terminal: bash start_pmbot.sh
```

That's it! Everything else happens automatically.

---

## What Happens Automatically (Step by Step)

### Step 0: Check Docker
```
✅ Verifies Docker is running
❌ If not: Shows error message with fix
```

### Step 1: Check Ollama (Optional)
```
✅ Checks if Ollama server is responding
⚠️  If not: Shows warning (but continues - user can start it)
```

### Step 2: Detect Ports & Update Config
```
1. Checks if ports 3000, 5432, 8000 are free
2. If busy, finds free alternatives
3. Updates backend/.env with new ports
4. Updates Frontend/.env with new ports
5. Saves config to .ports.json
```

### Step 3: Setup AI Models
```
1. Waits for Ollama to start (up to 120 seconds)
2. Checks if qwen2:7b-instruct is already downloaded
3. If not found, downloads it (~4GB, takes 5-15 minutes)
4. If download fails, tries llama2 (backup model)
5. Verifies model works
```

### Step 4: Start Services
```
docker-compose up --build

Creates 4 containers:
  • Frontend (React) - http://localhost:3000
  • Backend (Python API) - http://localhost:8000
  • Database (PostgreSQL) - localhost:5432
  • LLM Stub (Ollama wrapper) - localhost:5000
```

---

## Real-World Timeline

### First Time Running PMBOT
```
0-5 seconds   : Docker check ✅
5-10 seconds  : Ollama check ✅
10-20 seconds : Port detection ✅
20-30 seconds : Model check (downloads if needed)
30-180 seconds: Model download (if needed) ⏳ Takes 5-15 minutes!
180+ seconds  : Docker services start ✅
              : Ready at http://localhost:3000 🎉
```

### Subsequent Runs (Model Already Downloaded)
```
0-5 seconds   : Docker check ✅
5-10 seconds  : Ollama check ✅
10-20 seconds : Port detection ✅
20-30 seconds : Model check (already exists) ✅
30-60 seconds : Docker services start ✅
              : Ready at http://localhost:3000 🎉
```

---

## Prerequisite: What You Need Before Running

### Must Have ✅
1. **Docker Desktop** installed
   - Windows: https://www.docker.com/products/docker-desktop
   - Mac: https://www.docker.com/products/docker-desktop
   - Linux: `sudo apt install docker.io` (Ubuntu/Debian)

2. **Ollama** installed and running
   - Download: https://ollama.ai
   - Run: `ollama serve` in a terminal (keep it open!)

### That's All! ✨
- No Python needed
- No pip packages
- No virtual environments
- No extra setup

---

## Accessing PMBOT

After everything starts, open your browser:

**http://localhost:3000**

You'll see:
- Interview setup form
- Job description upload
- Question selection
- Interview flow
- Results and evaluation

---

## If Something Goes Wrong

### Docker Not Running
```
Error: ❌ Docker is not installed or not running

Fix:
  1. Start Docker Desktop
  2. Run: start_pmbot.bat (Windows) or bash start_pmbot.sh (Mac/Linux)
```

### Ollama Not Responding
```
Warning: ⚠️ Ollama is not responding

Fix:
  1. Open new terminal
  2. Run: ollama serve
  3. Keep that terminal open
  4. Run startup script again
```

### Port Already in Use
```
The script automatically finds alternative ports!
Check: cat .ports.json (or type .ports.json on Windows)
Access at: http://localhost:3000 (or the port listed in .ports.json)
```

### Model Download Too Slow
```
The model (~4GB) takes 5-15 minutes first time.
Network speed matters! Download speed example:
  - 1 Mbps: ~60 minutes
  - 10 Mbps: ~10 minutes
  - 50 Mbps: ~2 minutes
  - 100+ Mbps: <1 minute

Don't close the terminal while downloading!
```

### Model Download Failed
```
Error: ❌ Failed to pull qwen2:7b-instruct

Fix 1 (automatic):
  The script tries fallback models (llama2, neural-chat, mistral)
  One of them should work!

Fix 2 (manual):
  1. Open terminal
  2. Run: ollama pull llama2
  3. Run startup script again
```

---

## What Gets Created

After first run, you'll have:

### Configuration Files
```
.ports.json           - Current port mapping
backend/.env          - Backend configuration
Frontend/.env         - Frontend configuration
```

### Data Files
```
docker volumes/       - Persistent database
ollama models/        - Downloaded AI models (~4GB)
```

---

## Quick Reference

| Task | Windows | Mac/Linux |
|------|---------|----------|
| Start PMBOT | `start_pmbot.bat` | `bash start_pmbot.sh` |
| Check ports | `type .ports.json` | `cat .ports.json` |
| View logs | `docker logs pmbot-backend` | `docker logs pmbot-backend` |
| Stop services | Ctrl+C in terminal | Ctrl+C in terminal |
| See backend logs | `docker logs pmbot-backend` | `docker logs pmbot-backend` |
| See frontend logs | `docker logs pmbot-frontend` | `docker logs pmbot-frontend` |
| See database logs | `docker logs pmbot-db` | `docker logs pmbot-db` |

---

## Summary

✅ **One command to start:** `start_pmbot.bat` or `bash start_pmbot.sh`
✅ **Automatic setup:** Ports, models, database
✅ **Works everywhere:** Windows, Mac, Linux
✅ **No Python:** 100% native shell scripts
✅ **Handles conflicts:** Finds free ports automatically
✅ **Fast:** <1 minute after first run

**Everything is automated. Just run and enjoy PMBOT!** 🚀
