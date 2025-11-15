# PM Bot - Complete Setup Guide

This guide will help you set up and run the PM Bot project from scratch after cloning from GitHub.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Docker** (latest version) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (comes with Docker Desktop) - v2.0+
- **Git** - [Install Git](https://git-scm.com/downloads)

### Optional (for local development without Docker)
- **Python 3.10+** - For backend development
- **Node.js 20+** - For frontend development
- **PostgreSQL 13+** - If running database locally

## Quick Start (Recommended - With Docker)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW
```

### Step 2: Verify Environment Files

The project includes pre-configured `.env` files. Check that these files exist:

```bash
# Check backend .env
ls -la backend/.env

# Check frontend .env
ls -la Frontend/.env
```

**If any `.env` file is missing, they will be automatically created by Docker Compose.**

### Step 3: Start the Project

```bash
# Build and start all containers
docker compose up --build

# Or if you just want to start (images already built)
docker compose up -d
```

### Step 4: Access the Application

Once all containers are running (you'll see "Application startup complete" in logs):

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 5: First Time Setup

When you first open the frontend, you'll need to:

1. Click on "Sign Up" to create a new account, or
2. Use "Google Login" for OAuth authentication
3. Once logged in, you'll be prompted to select your region
4. Complete the onboarding by selecting experience level and current role
5. Start practicing interviews!

## Project Structure

```
PMBOTNEW/
├── Frontend/                 # React + TypeScript frontend
│   ├── src/                 # Source code
│   ├── .env                 # Frontend environment variables (auto-created)
│   └── package.json         # Node.js dependencies
├── backend/                 # FastAPI Python backend
│   ├── app/                 # Main application code
│   ├── .env                 # Backend environment variables
│   ├── requirements.txt      # Python dependencies
│   └── PM_Questions_*.csv   # Question database files
├── docker-compose.yml       # Docker composition file
└── scripts/                 # Utility scripts
```

## Docker Compose Services

The project consists of 4 services:

1. **pmbot-db** (PostgreSQL 13)
   - Port: 5432
   - Credentials: user/password (from docker-compose.yml)
   - Database: mydatabase

2. **pmbot-backend** (FastAPI)
   - Port: 8000
   - Auto-creates tables and loads questions on startup
   - Connects to database and LLM service

3. **pmbot-frontend** (Vite + React)
   - Port: 3000
   - Auto-recompiles on file changes
   - Connects to backend API

4. **pmbot-llm-stub** (LLM Wrapper - Qwen2)
   - Port: 5000
   - Provides AI evaluation for interviews
   - Uses qwen2:7b-instruct model

## Environment Variables

### Backend (.env)

Key variables that control backend behavior:

```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/mydatabase

# JWT Security
JWT_SECRET=dev-secret-change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Endpoints
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# LLM Service
LLM_API_URL=http://pmbot-llm-stub:5000
LLM_MODEL=qwen2:7b-instruct

# Questions Dataset
PM_QUESTIONS_CSV=/backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

### Frontend (.env)

Key variables for frontend configuration:

```env
VITE_API_BASE=http://localhost:8000
VITE_APP_NAME=PM Bot
VITE_APP_VERSION=1.0.0
```

## Common Commands

### Start the application
```bash
docker compose up -d
```

### Stop the application
```bash
docker compose down
```

### Stop and remove all data (fresh start)
```bash
docker compose down -v
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f pmbot-backend
docker compose logs -f pmbot-frontend
docker compose logs -f pmbot-db
```

### Rebuild containers
```bash
docker compose up -d --build
```

### Run backend tests
```bash
docker compose exec pmbot-backend python -m pytest tests/
```

## Troubleshooting

### Docker containers won't start

**Issue**: "Port 3000 already in use"

**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different ports
docker compose -p pmbot --compatibility up -d
```

### Database connection errors

**Issue**: "Failed to connect to database"

**Solution**:
```bash
# Check database container logs
docker compose logs pmbot-db

# Recreate database
docker compose down -v
docker compose up -d
```

### Frontend can't connect to backend

**Issue**: "Failed to fetch from http://localhost:8000"

**Solution**:
1. Check that backend is running: `docker compose logs pmbot-backend`
2. Verify API is responding: `curl http://localhost:8000/docs`
3. Check VITE_API_BASE in Frontend/.env is set to `http://localhost:8000`

### Questions not loading

**Issue**: "No interview questions available"

**Solution**:
```bash
# Check if questions were loaded
docker compose logs pmbot-backend | grep "Loaded questions"

# Should see: "Loaded questions. Read=18168, Inserted=18168"
```

### Performance issues

**Issue**: Application running slowly

**Solutions**:
1. Allocate more resources to Docker
2. Clear Docker cache: `docker system prune -a`
3. Rebuild containers: `docker compose up -d --build`

## Development Workflow

### Frontend Development

```bash
# Files are automatically reloaded when you edit them
# Edit files in Frontend/src/ and changes appear instantly

# Navigate to: http://localhost:3000
```

### Backend Development

```bash
# To run backend locally (without Docker):
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose exec pmbot-db psql -U user -d mydatabase

# List tables
\dt

# View users
SELECT * FROM "user";
```

## Production Deployment

For production, update these environment variables:

### Backend Production Settings
```env
JWT_SECRET=<generate-a-strong-secret>
JWT_REFRESH_SECRET=<generate-another-strong-secret>
SECRET_KEY=<generate-a-random-secret>
CORS_ORIGINS=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
OAUTH_REDIRECT_BASE=https://yourdomain.com:8000
DATABASE_URL=postgresql://user:strong_password@db-host:5432/prod_db
```

### Frontend Production Settings
```env
VITE_API_BASE=https://api.yourdomain.com
```

### Docker Compose for Production
```bash
docker compose -f docker-compose.yml up -d --scale pmbot-backend=2
```

## API Documentation

Once the backend is running, access comprehensive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support & Documentation

- See `README.md` for project overview
- See `TROUBLESHOOTING.md` for common issues
- See `DOCUMENTATION_INDEX.md` for detailed docs
- See `backend/README.md` for backend-specific info

## Quick Verification Checklist

After setup, verify everything works:

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API responds at http://localhost:8000/docs
- [ ] Can sign up / login with email or Google
- [ ] Region selection modal appears after login
- [ ] Can complete onboarding
- [ ] Can start an interview
- [ ] Logout button works properly
- [ ] Profile shows correct data
- [ ] Leaderboard displays rankings

## Next Steps

1. **Configure OAuth** (Optional):
   - Create a Google OAuth app at [Google Cloud Console](https://console.cloud.google.com/)
   - Update `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in backend/.env
   - Restart backend: `docker compose restart pmbot-backend`

2. **Customize Questions** (Optional):
   - Place your PM questions CSV in `backend/` folder
   - Update `PM_QUESTIONS_CSV` path in backend/.env
   - Restart backend to reload questions

3. **Configure LLM** (Optional):
   - By default uses qwen2:7b-instruct
   - Change `LLM_MODEL` in backend/.env for different model
   - Requires [Ollama](https://ollama.ai/) installed locally

---

**Happy Interviewing! 🚀**
