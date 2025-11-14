# PMBOT - Intern Quick Start Guide

Welcome! This guide gets you started with PMBOT in the fastest way possible.

## 5-Minute Quick Start

### 1️⃣ Prerequisites (One-time install)

**Windows:**
- Download & install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Download & install [Ollama](https://ollama.ai)
- Download & install [Git](https://git-scm.com) (if not already installed)

**Mac/Linux:**
- Same as above

### 2️⃣ Clone & Setup

**Windows PowerShell:**
```powershell
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
.\scripts\first-run.ps1
```

**Mac/Linux Terminal:**
```bash
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
bash scripts/first-run.sh
```

### 3️⃣ Start Ollama (New Terminal)

```bash
ollama serve
```

Leave this running in the background - it's the AI engine!

### 4️⃣ That's it! Access the app

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | What PMBOT is and how it works |
| **SETUP.md** | Detailed setup & troubleshooting (start here if stuck) |
| **COMMANDS.md** | Common Docker commands |
| **TROUBLESHOOTING.md** | Fix common problems |
| **DEPLOYMENT_CHECKLIST.md** | Pre-deployment verification |
| **COMMANDS.md** | Quick command reference |

## 🚨 Problems?

### "ollama: command not found"
→ Restart terminal after installing Ollama

### "Port 3000 already in use"
→ Change port in docker-compose.yml or kill the other app

### "Cannot reach host.docker.internal"
→ Ensure Docker Desktop is fully started

### "Timeout errors" during interview
→ This is normal! LLM takes 2-5 minutes to think. Wait for it.

**See TROUBLESHOOTING.md for more help.**

## 🎯 Daily Workflow

### Starting Development
```bash
# Terminal 1: Start Docker
docker compose up

# Terminal 2: Start Ollama (if not already running)
ollama serve

# Terminal 3: Make code changes
# (Changes auto-reload in containers)
```

### Stopping
```bash
# Stop services (keeps data)
docker compose stop

# Or fully remove containers
docker compose down
```

### Viewing Logs
```bash
# All services
docker compose logs -f

# Just backend
docker compose logs -f pmbot-backend

# Just frontend
docker compose logs -f pmbot-frontend
```

## 🔄 Common Tasks

### Reset Everything
```bash
docker compose down -v
docker compose build --no-cache
./scripts/first-run.ps1  # or first-run.sh
```

### Rebuild One Service
```bash
docker compose build pmbot-backend
docker compose up -d
```

### Access Database
```bash
docker compose exec pmbot-db psql -U user -d mydatabase
```

### View Backend Logs
```bash
docker compose logs pmbot-backend --tail 50
```

## ✅ Verify It Works

1. Frontend loads at http://localhost:3000 ✓
2. Can register/login ✓
3. Can start interview ✓
4. Can submit answers ✓
5. Results page shows AI feedback ✓

If any fails, check TROUBLESHOOTING.md

## 🏗️ Architecture (Simple Version)

```
Your Browser
    ↓
Frontend (React) :3000
    ↓
Backend (FastAPI) :8000
    ↓
LLM Wrapper :5000
    ↓
Ollama on Your Computer :11434
    ↓
AI Models (llama3, qwen2)
```

## 📝 Config Files

After first setup, these exist:

- `backend/.env` - Backend configuration
- `Frontend/.env` - Frontend configuration

**Never commit these to git!** They're gitignored for security.

The `.env.example` files show what variables you can set.

## 🎓 Learning Path

1. **First time:** Follow SETUP.md → Run setup script → Access app
2. **Having issues:** Check TROUBLESHOOTING.md
3. **Making changes:** Edit code, changes auto-reload in containers
4. **Deploying:** Check DEPLOYMENT_CHECKLIST.md
5. **Need commands:** Reference COMMANDS.md

## 💡 Pro Tips

- 🔄 Containers auto-reload on code changes (volume mounts)
- 📊 Use `docker stats` to see resource usage
- 🔍 Errors show in `docker compose logs`
- 🎯 Most problems have solutions in TROUBLESHOOTING.md
- ⚡ First LLM response is slow (models loading) - be patient!

## 🆘 When Stuck

1. **Read the error message carefully** - Often very helpful
2. **Check TROUBLESHOOTING.md** - Most common issues covered
3. **Run `docker compose logs`** - See what's actually happening
4. **Check SETUP.md** - Detailed explanations
5. **Restart services** - Fixes 50% of issues
   ```bash
   docker compose restart
   ```

## 📞 Quick Checklist

- [ ] Docker Desktop installed and running
- [ ] Ollama installed and `ollama serve` command works
- [ ] Git installed
- [ ] Ran setup script successfully
- [ ] Frontend loads at localhost:3000
- [ ] Backend responds at localhost:8000/health
- [ ] Can complete interview workflow
- [ ] Results page shows AI feedback

All checked? You're ready to go! 🚀

## 🎯 Next Steps

1. **Explore the code:**
   - Frontend: `Frontend/src/`
   - Backend: `backend/app/`
   - LLM wrapper: `backend/llm_stub/`

2. **Make a small change:**
   - Edit a component in `Frontend/src/components/`
   - See changes live in browser (no rebuild needed!)

3. **Run the interview:**
   - Create account
   - Complete interview
   - View results with AI feedback

4. **Check logs:**
   - `docker compose logs` to see everything happening
   - Understand the flow from frontend → backend → LLM

## 📖 Full Documentation

- [SETUP.md](./SETUP.md) - Complete setup guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Fix issues
- [COMMANDS.md](./COMMANDS.md) - Command reference
- [README.md](./README.md) - Project overview
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Production

---

**Need help?** Start with TROUBLESHOOTING.md  
**New to Docker?** Check COMMANDS.md  
**Want details?** Read SETUP.md  

Welcome to the team! 🎉
