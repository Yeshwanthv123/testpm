# PMBOT Quick Reference Card

Print this out or bookmark it! Quick answers to common questions.

---

## 🚀 Fresh Setup (Do This First!)

### Windows
```powershell
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
.\scripts\first-run.ps1
ollama serve  # In new terminal
```

### Mac/Linux
```bash
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
bash scripts/first-run.sh
ollama serve  # In new terminal
```

Access: http://localhost:3000

---

## 📚 Documentation Quick Links

| Need | File |
|------|------|
| I'm new | **INTERN_START.md** |
| Setup help | **SETUP.md** |
| Problem? | **TROUBLESHOOTING.md** |
| Commands | **COMMANDS.md** |
| Deploy? | **DEPLOYMENT_CHECKLIST.md** |
| What's done? | **COMPLETE_REPORT.md** |

---

## 🐳 Essential Docker Commands

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f pmbot-backend

# Stop services
docker compose stop

# Fully restart
docker compose restart

# Check status
docker compose ps

# Full reset (WARNING: deletes data!)
docker compose down -v
```

---

## ✅ Is It Working?

| Check | Command |
|-------|---------|
| Backend up? | `curl http://localhost:8000/health` |
| Ollama running? | `ollama list` |
| Docker services? | `docker compose ps` |
| Database OK? | `docker compose exec pmbot-db psql -U user -d mydatabase -c "SELECT 1"` |
| Frontend loads? | Open http://localhost:3000 in browser |

---

## 🆘 Common Issues (Quick Fixes)

| Problem | Solution |
|---------|----------|
| "Port already in use" | Change port in docker-compose.yml or kill other app |
| "Connection refused" | Ensure `ollama serve` is running in another terminal |
| "Docker not found" | Install Docker Desktop from docker.com |
| "Services keep crashing" | Check `docker compose logs` for errors |
| "Timeout errors" | Normal for LLM (takes 2-5 min). Just wait! |
| ".env file missing" | Run setup script: `./scripts/setup.ps1` |
| "Can't register/login" | Restart backend: `docker compose restart pmbot-backend` |

---

## 📝 Configuration Files

After setup, you'll have:

- `backend/.env` - Backend config (DATABASE_URL, JWT secrets, etc.)
- `Frontend/.env` - Frontend config (VITE_API_BASE=http://localhost:8000)

**Never commit these! They're gitignored.**

---

## 🔄 Development Workflow

```bash
# 1. Start everything
docker compose up

# 2. Edit code (changes auto-reload!)
# Open Frontend/src/components/Dashboard.tsx and edit

# 3. See changes live in browser (no rebuild!)
# Refresh at http://localhost:3000

# 4. Check backend logs if needed
docker compose logs -f pmbot-backend

# 5. Stop when done
docker compose stop
```

---

## 🧪 Test Everything

1. Frontend: http://localhost:3000 → Should load
2. Backend: http://localhost:8000/health → Should return {"status":"ok"}
3. Register: Create account at localhost:3000
4. Interview: Start interview → Submit answers
5. Results: Should show AI feedback with score, strengths, weaknesses

If all 5 work → You're good! ✅

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Change JWT_SECRET in backend/.env to random 32+ char string
- [ ] Change SECRET_KEY similarly
- [ ] Update CORS_ORIGINS to your domain
- [ ] Configure database connection string
- [ ] Set up OAuth (if using)
- [ ] Update all URLs to production domain
- [ ] Set LLM_FORCE=1 for real AI (not templates)
- [ ] Read DEPLOYMENT_CHECKLIST.md

---

## 📞 Getting Help

### Step 1: Check TROUBLESHOOTING.md
Has 40+ solutions. You probably find your answer there.

### Step 2: Run docker compose logs
Shows actual error messages (very helpful!)

```bash
docker compose logs pmbot-backend | grep -i "error"
```

### Step 3: Check SETUP.md
Detailed explanations of what should happen at each step.

### Step 4: Ask team
If still stuck, ask with:
- Exact error message (copy-paste)
- Output of `docker compose logs`
- What you were doing when error occurred

---

## 💾 Backup Database

```bash
docker compose exec pmbot-db pg_dump -U user mydatabase > backup.sql
```

Restore:
```bash
docker compose exec -T pmbot-db psql -U user mydatabase < backup.sql
```

---

## 🔧 Advanced Debugging

### Access database directly
```bash
docker compose exec pmbot-db psql -U user -d mydatabase
```

### Check environment variables
```bash
docker compose exec pmbot-backend env | grep LLM
```

### Run command in container
```bash
docker compose exec pmbot-backend python -c "import sys; print(sys.version)"
```

### View container details
```bash
docker inspect pmbot-backend
```

---

## 📊 System Requirements

Minimum:
- 8GB RAM
- 10GB disk space
- Docker Desktop installed
- Ollama installed

Recommended:
- 16GB RAM
- 20GB disk space
- SSD storage
- GPU (for faster LLM inference)

---

## ⚡ Performance Tips

1. More RAM = Faster LLM inference
2. SSD = Faster Docker operations
3. GPU = Dramatically faster LLM
4. Close other apps = More resources for Docker
5. First LLM response = Slow (models loading)
6. Subsequent responses = Faster (cached)

---

## 🔐 Security Reminders

- ✅ Never commit .env files
- ✅ Change secrets before production
- ✅ Use strong random values for JWT_SECRET
- ✅ Don't share .env file details publicly
- ✅ Use HTTPS in production
- ✅ Rotate OAuth secrets regularly

---

## 📱 Mobile Access

To access from another device on your network:

```bash
# Find your machine IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# Access from other device
http://<your-ip>:3000
```

Note: May need to adjust CORS_ORIGINS in backend/.env

---

## 🎯 Quick Decision Tree

```
Application won't start?
├─ Check: docker compose ps
├─ Read: TROUBLESHOOTING.md
└─ Try: docker compose logs

Code changes not showing?
├─ Refresh browser
└─ Check: docker compose logs pmbot-frontend

LLM slow?
├─ Normal for first request (2-5 min)
├─ Check: docker stats
└─ Tip: More RAM = faster

Can't connect to Ollama?
├─ Check: ollama serve is running
├─ Check: ollama list shows models
└─ Verify: curl http://localhost:11434/api/tags

Database error?
├─ Check: docker compose logs pmbot-db
├─ Try: docker compose restart pmbot-db
└─ Last resort: docker compose down -v
```

---

## 📋 Maintenance Checklist

Weekly:
- [ ] Check disk space: `docker system df`
- [ ] Review logs for errors: `docker compose logs`

Monthly:
- [ ] Update models: `ollama pull llama3` (if new version)
- [ ] Backup database: `pg_dump ... > backup.sql`
- [ ] Check for Docker updates: Docker Desktop updates

Quarterly:
- [ ] Review security settings
- [ ] Rotate OAuth secrets if using
- [ ] Check performance metrics

---

## 🎓 Learning Resources

- Docker Docs: https://docs.docker.com
- Ollama Docs: https://ollama.ai
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
- PostgreSQL Docs: https://www.postgresql.org/docs

---

## 📝 Template Variables

Backend (.env):
```
DATABASE_URL=postgresql://user:password@db:5432/mydatabase
JWT_SECRET=<random-string>
CORS_ORIGINS=http://localhost:3000
LLM_API_URL=http://pmbot-llm-stub:5000
LLM_MODEL=qwen2:7b-instruct
```

Frontend (.env):
```
VITE_API_BASE=http://localhost:8000
```

---

## 🚀 One-Liner Cheatsheet

```bash
# Start
docker compose up -d && echo "✅ Started!"

# Logs
docker compose logs -f --tail=100

# Status
docker compose ps

# Stop
docker compose stop

# Reset
docker compose down -v && docker compose up -d

# Clean
docker system prune -a

# Backup DB
docker compose exec pmbot-db pg_dump -U user mydatabase > backup.sql

# Test Backend
curl http://localhost:8000/health

# Test Ollama
curl http://localhost:11434/api/tags
```

---

## 🎯 Success Indicators

You're all set when:
- ✅ `docker compose ps` shows 4 services running
- ✅ `curl http://localhost:8000/health` returns OK
- ✅ Frontend loads at http://localhost:3000
- ✅ Can create account and complete interview
- ✅ Results show real AI feedback (not templates)

---

**Print this card. Keep it handy. Problem solved!** 📌

Last Updated: November 2025  
Version: 1.0.0
