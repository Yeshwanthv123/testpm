# PMBOT Auth Backend (Email/Password + Google/LinkedIn OAuth)
See `.env.example` for required environment variables and redirect URIs.

Quick setup
1. Copy the example into a working `.env` file inside the `backend` folder and fill in real values:

	PowerShell:

	```powershell
	Copy-Item -Path .\backend\.env.example -Destination .\backend\.env -Force
	# then edit backend\.env with your secrets
	```

2. Important: do NOT commit `backend/.env` to source control. If you need to share variables with teammates, commit `backend/.env.example` and have them copy it locally.

Quick runnable defaults
----------------------
To make the repo runnable right after cloning (without adding secrets), there's a safe file checked in: `backend/.env.local`.

- `backend/.env.local` contains non-secret defaults (for example `LLM_API_URL=http://localhost:11434` and a placeholder `SECRET_KEY`).
- To run locally, copy it to `backend/.env`:

	```powershell
	Copy-Item -Path .\backend\.env.local -Destination .\backend\.env -Force
	notepad .\backend\.env   # edit if you need to change values
	```

Setup helper (Windows PowerShell)
--------------------------------
Run the `scripts\setup_dev.ps1` helper to create a Python venv and install required Python packages for backend and the LLM stub:

```powershell
# from repository root
.\scripts\setup_dev.ps1
# then run the backend (example):
# cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload
```

Notes
-----
- `backend/.env.local` is intentionally safe to commit and will not expose secrets. If you have real secrets, put them into `backend/.env` and do NOT commit that file.
- For CI/deploy environments, use the platform's secrets feature instead of committing credentials.
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
