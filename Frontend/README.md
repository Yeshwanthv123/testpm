# PMBOT Auth Bundle (Light)

This bundle contains the **auth-only backend** and a **docker-compose.yml**.
Place your existing **frontend** folder next to this bundle (as `./frontend`) and run docker compose.

## Layout
- backend/   ← FastAPI + JWT (auth)
- frontend/  ← **Your existing frontend** (put it here, unchanged)
- docker-compose.yml

## Run
```bash
# 1) Put your frontend folder here, named `frontend` (unchanged).
# 2) Start both services
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend:  http://localhost:8000

## Backend Endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET  /auth/me
- POST /tts  (501 stub)
- POST /stt  (501 stub)
