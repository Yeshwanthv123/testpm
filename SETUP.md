# PMBOT Setup Guide - Fresh Clone & Deployment

This guide walks you through setting up PMBOT from a fresh clone, ensuring all dependencies and configurations are properly set up.

## Prerequisites

- **Docker Desktop** (with WSL2 on Windows)
- **Ollama** running on your host machine
- **Git** for cloning the repository
- **Ollama Models** pre-downloaded on your host

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
```

### 2. Set Up Environment Files

The repository includes `.env.example` templates. You must generate actual `.env` files before running:

#### Option A: Automatic Setup (Recommended)

**On Windows (PowerShell):**
```powershell
.\scripts\setup.ps1
```

**On Mac/Linux:**
```bash
bash scripts/setup.sh
chmod +x scripts/setup.sh
bash scripts/setup.sh
```

#### Option B: Manual Setup

Copy the template files to create actual `.env` files:

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp Frontend/.env.example Frontend/.env
```

### 3. Prepare Ollama Models on Host

PMBOT uses local Ollama models running on your **host machine** (not in Docker).

**On Windows (PowerShell):**

1. **Download Ollama** from [ollama.ai](https://ollama.ai)

2. **Start Ollama server** in a separate terminal:
   ```powershell
   ollama serve
   ```
   
   This runs Ollama at `http://localhost:11434`

3. **Download the required models:**
   ```powershell
   ollama pull llama3
   ollama pull qwen2:7b-instruct
   ```

4. **Verify models are available:**
   ```powershell
   ollama list
   ```
   
   You should see:
   ```
   NAME                       ID              SIZE    MODIFIED
   llama3:latest              xxxxxxxxxxxxxx  4.7GB   ...
   qwen2:7b-instruct:latest   xxxxxxxxxxxxxx  4.0GB   ...
   ```

### 4. Start Docker Services

With Ollama running on your host and `.env` files created:

```bash
docker compose up --build
```

**Expected Output:**
```
✔ pmbot-db       Running
✔ pmbot-backend  Running
✔ pmbot-frontend Running
✔ pmbot-llm-stub Running
```

### 5. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

## ✅ Verification Checklist

After startup, verify everything is working:

- [ ] Frontend loads at http://localhost:3000
- [ ] Can access login/signup page
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Can start an interview and submit answers
- [ ] AI evaluation completes and shows results with scores, strengths, weaknesses, feedback

### Test with cURL

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok"}
```

## 🐛 Troubleshooting

### Issue: "Connection refused" or "service not found"

**Problem:** Backend can't reach Ollama or database

**Solution:**
```bash
# Ensure Ollama is running on host
ollama serve

# Check Docker network
docker network ls
docker network inspect pmbot-net

# View logs
docker compose logs pmbot-backend
docker compose logs pmbot-llm-stub
```

### Issue: "Timeout" errors in backend logs

**Problem:** LLM inference is taking too long

**Solution:**
- This is normal for first inference (models are loading)
- Subsequent calls are faster
- Check Ollama logs: `ollama` command in its terminal
- Verify models are fully downloaded: `ollama list`

### Issue: ".env files not found" error

**Problem:** Environment files weren't created

**Solution:**
```bash
# Ensure you ran setup script
./scripts/setup.ps1  # Windows
bash scripts/setup.sh # Mac/Linux

# Or manually copy
cp backend/.env.example backend/.env
cp Frontend/.env.example Frontend/.env
```

### Issue: "Cannot reach host.docker.internal"

**Problem:** Docker can't reach your host machine's Ollama

**Solution (Windows Docker Desktop):**
- Ensure Docker Desktop is configured for WSL2
- Check Ollama is listening on 11434: `netstat -ano | findstr :11434`
- If needed, update `docker-compose.yml`:
  ```yaml
  OLLAMA_URL: http://host.docker.internal:11434
  ```

**Solution (Mac Docker Desktop):**
- Same as above, `host.docker.internal` is built-in

**Solution (Linux - Docker without Desktop):**
- Use host IP instead: `OLLAMA_URL: http://192.168.x.x:11434`
- Or use `--network host` flag in docker compose

### Issue: "Module not found" or "Import errors"

**Problem:** Backend dependencies not installed

**Solution:**
```bash
# Rebuild backend image
docker compose build pmbot-backend

# Then restart
docker compose up
```

### Issue: Database connection errors

**Problem:** PostgreSQL isn't ready

**Solution:**
```bash
# Check database logs
docker compose logs pmbot-db

# Database has 10s healthcheck retries, usually stabilizes quickly
# If stuck, recreate volume
docker compose down -v
docker compose up
```

## 📁 Project Structure

```
PMBOTNEW/
├── backend/
│   ├── .env.example          ← Copy to .env
│   ├── .env                  ← (generated, not committed)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py           ← FastAPI app
│   │   ├── config.py         ← Settings & env vars
│   │   ├── ai_services.py    ← LLM integration (600s timeouts)
│   │   └── ...
│   └── llm_stub/
│       ├── ollama_wrapper.py ← Flask proxy to Ollama
│       └── requirements.txt
├── Frontend/
│   ├── .env.example          ← Copy to .env
│   ├── .env                  ← (generated, not committed)
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx           ← Main app with interview flow
│   │   ├── components/
│   │   │   └── Dashboard.tsx ← Results display
│   │   └── ...
│   └── Dockerfile
├── docker-compose.yml        ← Service orchestration
├── SETUP.md                  ← You are here!
└── scripts/
    ├── setup.ps1             ← Auto-setup (Windows)
    └── setup.sh              ← Auto-setup (Unix)
```

## 🔄 Development Workflow

### Running with Hot Reload

Both frontend and backend support hot reload in Docker:

```bash
# Start in foreground to see logs
docker compose up

# In another terminal, edit files
# Changes reflect immediately in containers
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f pmbot-backend
docker compose logs -f pmbot-llm-stub
docker compose logs -f pmbot-frontend

# Last 50 lines
docker compose logs --tail 50 pmbot-backend
```

### Stopping Services

```bash
# Stop but keep volumes
docker compose stop

# Fully remove (caution: loses database data)
docker compose down

# Remove everything including volumes
docker compose down -v
```

## 🚀 Production Deployment

For production deployment:

1. **Set strong secrets in `.env` files:**
   - Change `JWT_SECRET` and `JWT_REFRESH_SECRET` to random 32+ character strings
   - Change `SECRET_KEY` similarly

2. **Update CORS origins:**
   - Replace `http://localhost:3000` with your production domain
   - Remove `http://localhost:5173` development URL

3. **Configure OAuth (if using):**
   - Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, etc.
   - Update redirect URIs in Google Cloud Console and LinkedIn Developer Portal

4. **Use environment-specific settings:**
   - Create `.env.production` with production values
   - Point docker-compose to production `.env` file

5. **Use PostgreSQL connection pooling:**
   - Update `DATABASE_URL` to include connection pool parameters
   - Example: `postgresql://user:password@db-host:5432/db?sslmode=require`

## 📝 Key Technologies

- **Backend:** FastAPI (Python 3.10)
- **Frontend:** React + TypeScript (Vite)
- **Database:** PostgreSQL 13
- **LLM:** Ollama with llama3 & qwen2:7b-instruct
- **Container:** Docker Compose

## 🆘 Need Help?

1. Check the troubleshooting section above
2. View backend logs: `docker compose logs pmbot-backend`
3. View wrapper logs: `docker compose logs pmbot-llm-stub`
4. Verify Ollama is running: `ollama list`
5. Check database: `docker compose logs pmbot-db`

## ✨ Success Indicators

You'll know everything is working when:

✅ Frontend loads at http://localhost:3000  
✅ Backend API responds at http://localhost:8000/health  
✅ Can create account and log in  
✅ Can complete interview questions  
✅ AI evaluation returns real scores and feedback (not templates)  
✅ Results page shows all AI-generated fields:
  - Score (0-100)
  - Model Answer (500+ words)
  - Strengths (bullet points)
  - Weaknesses/Improvements (bullet points)
  - Feedback (human-readable summary)
