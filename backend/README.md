# PMBOT Auth Backend (Email/Password + Google/LinkedIn OAuth)
See .env.example for required environment variables and redirect URIs.
Endpoints:
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET  /auth/me
- GET  /auth/oauth/google/start
- GET  /auth/oauth/google/callback
- GET  /auth/oauth/linkedin/start
- GET  /auth/oauth/linkedin/callback
- POST /tts (stub), POST /stt (stub)
- GET  /health
