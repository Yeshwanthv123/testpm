# PM Bot - Setup Guide for Code Review

This guide ensures the project runs perfectly on a fresh clone with no errors.

## Prerequisites

1. **Docker & Docker Compose** installed and running
2. **Git** installed
3. **Ollama** (for local AI model) - Download offline before starting

## Step 1: Clone Repository

```bash
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
```

## Step 2: Download AI Model (Offline)

Before running Docker, download the AI model that the project uses:

```bash
# Download the Qwen model (approximately 4.7GB)
ollama pull qwen2:7b-instruct

# Verify it's installed
ollama list
```

**Note:** If you don't have Ollama installed yet, visit https://ollama.ai and download it first.

## Step 3: Configure Environment

### Option A: Using Default Configuration (Recommended for Review)

Copy the example environment file to create your `.env`:

```bash
cd backend
cp .env.example .env
cd ..
```

This will use development defaults which include:
- SQLite/PostgreSQL (auto-created in Docker)
- Mock OAuth credentials (optional feature)
- Local LLM setup

### Option B: Custom Configuration

If you need to modify settings (e.g., add your Google OAuth credentials):

```bash
cd backend
nano .env  # or edit with your preferred editor
cd ..
```

**Important Settings:**
- `DATABASE_URL`: Already configured for Docker (uses `db` container)
- `LLM_API_URL`: Already configured for Docker (uses `pmbot-llm-stub` container)
- `LLM_MODEL`: Set to `qwen2:7b-instruct` (must match downloaded model)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: Optional (leave blank to skip OAuth)

## Step 4: Start the Project

```bash
# Build and start all services (backend, frontend, database, LLM)
docker-compose up -d --build

# Wait for services to be healthy (30-60 seconds)
docker-compose ps
```

**All containers should show "healthy" or "running" status.**

## Step 5: Verify Setup

### Check Backend Logs
```bash
docker-compose logs pmbot-backend
```

**Expected output:**
```
INFO:     Application startup complete
INFO:     Uvicorn running on 0.0.0.0:8000
```

### Check Database is Ready
```bash
docker-compose logs pmbot-db
```

**Expected output:**
```
PostgreSQL init process complete; ready for start up.
database system is ready to accept connections
```

### Check LLM Service
```bash
docker-compose logs pmbot-llm-stub
```

**Expected output:**
```
LLM service running on 0.0.0.0:5000
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Step 6: Test Core Features

### Test 1: Get Interview Questions
```bash
curl "http://localhost:8000/api/interview/questions?company=Google&experience=6-10"
```

**Expected:** Returns array of 8 interview questions

### Test 2: Test OAuth Endpoint (if credentials provided)
```bash
curl -i "http://localhost:8000/oauth/google/start"
```

**Expected:** Redirects to Google (302) or shows auth URL

### Test 3: Health Check
```bash
curl http://localhost:8000/
```

**Expected:** `{"message": "Welcome to the Interview App API"}`

## Troubleshooting

### Container fails to start
```bash
# View detailed error logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose up -d --build
```

### Database connection errors
```bash
# Wait for DB container to be healthy
docker-compose ps
# Should show pmbot-db with status "healthy"

# If stuck, restart database
docker-compose restart pmbot-db
```

### LLM service not responding
```bash
# Verify Ollama is running
ollama list

# Restart LLM service
docker-compose restart pmbot-llm-stub

# Check if model is loaded
docker-compose exec pmbot-llm-stub curl http://localhost:5000/tags
```

### Port conflicts
If ports 3000, 5000, 5173, 8000 are already in use:
- Edit `docker-compose.yml` and change port mappings
- Or close applications using those ports

## Project Structure

```
PMBOTNEW/
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app setup
│   │   ├── routers/
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── oauth.py        # Google OAuth
│   │   │   └── interview.py    # Interview questions
│   │   ├── models.py           # Database models
│   │   └── ai_services.py      # LLM integration
│   ├── .env.example            # Example environment config
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
│
├── Frontend/                    # React/Vite frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/             # Custom hooks (auth, voice)
│   │   └── utils/             # API client, auth utilities
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml          # Orchestrates all services
├── openapi.json                # API documentation
└── README.md                   # Project overview

```

## Services Breakdown

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 3000 | React app |
| **Backend** | 8000 | FastAPI server |
| **Database** | 5432 | PostgreSQL |
| **LLM Stub** | 5000 | Ollama wrapper for AI |

## Environment Variables Reference

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:password@db:5432/mydatabase` |
| `JWT_SECRET` | Token signing key | `dev-secret-change-me` |
| `FRONTEND_URL` | Frontend domain | `http://localhost:3000` |
| `LLM_API_URL` | LLM service URL | `http://pmbot-llm-stub:5000` |
| `LLM_MODEL` | Model name | `qwen2:7b-instruct` |
| `GOOGLE_CLIENT_ID` | OAuth credential | (optional) |
| `GOOGLE_CLIENT_SECRET` | OAuth credential | (optional) |

## Common Issues & Solutions

### "Address already in use"
Multiple instances of the project are running. Use `docker-compose down` to stop all containers.

### Frontend shows "Cannot reach backend"
- Verify backend is running: `docker-compose logs pmbot-backend`
- Check network: `docker network ls`
- Restart all services: `docker-compose down && docker-compose up -d --build`

### Questions not loading
- Ensure CSV file exists: `backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`
- Check database is initialized: `docker-compose logs pmbot-db`
- Verify database migrations ran: `docker-compose logs pmbot-backend | grep "create_tables"`

### OAuth not working
- Add Google credentials to `backend/.env`
- Ensure redirect URI registered in Google Cloud Console: `http://localhost:8000/oauth/google/callback`
- Rebuild backend: `docker-compose up -d --build pmbot-backend`

## Support

For issues or questions, check:
1. Docker logs: `docker-compose logs`
2. Backend logs: `docker-compose logs pmbot-backend`
3. Frontend console: Browser DevTools > Console tab
4. API docs: http://localhost:8000/docs (Swagger UI)

