# PMBOT Startup Guide - No Python Required

## Quick Start (One Command)

### Windows
```bash
start_pmbot.bat
```

### Mac/Linux
```bash
bash start_pmbot.sh
```

That's it! It will:
- ✅ Check Docker is running
- ✅ Auto-detect available ports
- ✅ Update configuration files
- ✅ Check for AI models
- ✅ Start all services

Access PMBOT at **http://localhost:3000**

---

## What Happens Automatically

### 1. Port Detection (Pure Bash/Batch)
- Scans ports 3000, 5432, 8000
- Finds alternatives if ports are busy
- Updates `.env` files automatically
- **No Python needed** - uses `netstat` (Windows) or `nc` (Linux/Mac)

### 2. AI Model Check (Pure Bash/Batch)
- Checks if Ollama is running
- Verifies if `qwen2:7b-instruct` is downloaded
- Auto-pulls model if needed
- Falls back to `llama2` if primary fails
- **No Python needed** - uses `curl` and `ollama` command

### 3. Docker Services
- Starts 4 containers (frontend, backend, database, LLM)
- Applies detected port configuration
- Creates database tables
- Loads interview questions

---

## Before First Run

### Install Required Tools (ONE TIME)

1. **Docker Desktop** (all platforms)
   - Download: https://www.docker.com/products/docker-desktop
   - Install and keep it running

2. **Ollama** (required for AI)
   - Download: https://ollama.ai
   - Install (takes 1-2 minutes)
   - Start manually: `ollama serve` (keep terminal open)

That's all! **No Python installation needed.**

---

## Manual Commands (If Needed)

### Just detect ports (don't start services)
**Windows:**
```bash
scripts\detect_ports.bat
```

**Mac/Linux:**
```bash
bash scripts/detect_ports.sh
```

### Just pull AI model (don't start services)
**Windows:**
```bash
scripts\auto_pull_model.bat
```

**Mac/Linux:**
```bash
bash scripts/auto_pull_model.sh
```

### Manual Docker start (after running above)
```bash
docker-compose up --build
```

---

## Troubleshooting

### "Port already in use"
Just run the startup script again - it will automatically find free ports:
```bash
start_pmbot.bat     # Windows
bash start_pmbot.sh # Mac/Linux
```

### "Ollama is not responding"
Ollama service needs to run in a separate terminal:
```bash
ollama serve
```
Keep this running while using PMBOT. Then start PMBOT normally.

### "Model not found"
Manually pull the model:
```bash
ollama pull qwen2:7b-instruct
```
This takes 5-15 minutes first time (downloads ~4GB).

### "Docker not found"
Install Docker Desktop from https://www.docker.com/products/docker-desktop

### "PMBOT not loading at http://localhost:3000"
Check the actual port in `.ports.json`:
```bash
cat .ports.json  # Mac/Linux
type .ports.json # Windows
```
Access at the port listed there.

---

## Configuration Files

After first run, you'll have:

**`.ports.json`** - Current port configuration
```json
{
  "backend": 8000,
  "frontend": 3000,
  "database": 5432
}
```

**`backend/.env`** - Backend settings
```
VITE_API_BASE=http://localhost:8000
DATABASE_URL=postgresql://postgres:password@localhost:5432/pmbot
LLM_API_URL=http://localhost:11434
```

**`Frontend/.env`** - Frontend settings
```
VITE_API_BASE=http://localhost:8000
```

---

## Advanced: Custom Ports

Edit `docker-compose.yml` to change default ports:
```yaml
services:
  pmbot-backend:
    ports:
      - "9000:8000"  # Use port 9000 instead of 8000
  pmbot-frontend:
    ports:
      - "3001:3000"  # Use port 3001 instead of 3000
  pmbot-db:
    ports:
      - "5433:5432"  # Use port 5433 instead of 5432
```

Then run startup script - it will detect your custom ports automatically.

---

## Scripts Overview

| Script | Purpose | Platform |
|--------|---------|----------|
| `start_pmbot.bat` | One-click startup | Windows |
| `start_pmbot.sh` | One-click startup | Mac/Linux |
| `scripts/detect_ports.bat` | Port detection | Windows |
| `scripts/detect_ports.sh` | Port detection | Mac/Linux |
| `scripts/auto_pull_model.bat` | AI model setup | Windows |
| `scripts/auto_pull_model.sh` | AI model setup | Mac/Linux |

All scripts use **native tools only** - no Python required!

---

## System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|------------|
| RAM | 4GB | 8GB+ |
| Disk | 15GB free | 20GB+ |
| CPU | 2 cores | 4+ cores |
| Network | 2 Mbps | 10+ Mbps |

First-time setup: ~5-15 minutes (mostly downloading AI model)

---

## Support

### Check System Status
```bash
# View running services
docker ps

# Check port configuration
cat .ports.json

# Test API connectivity
curl http://localhost:8000/health

# View logs
docker logs pmbot-backend
docker logs pmbot-frontend
```

### Common Issues
1. **Ports busy?** → Run startup script again
2. **Ollama offline?** → Run `ollama serve` in separate terminal
3. **Model missing?** → Run `ollama pull qwen2:7b-instruct`
4. **Docker failing?** → Restart Docker Desktop

---

## Summary

✅ **Zero Python dependencies** - uses pure Bash/Batch scripts
✅ **Single command startup** - just run `start_pmbot.bat` or `start_pmbot.sh`
✅ **Auto port detection** - finds free ports automatically
✅ **Auto model setup** - downloads AI model when needed
✅ **Cross-platform** - works on Windows, Mac, Linux

**Ready to start? Just run:**
```bash
start_pmbot.bat     # Windows
bash start_pmbot.sh # Mac/Linux
```

That's it! 🚀
