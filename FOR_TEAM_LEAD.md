# 🚀 Instructions for Team Lead / In-Charge

## When You Want to Start the Project

Instead of typing `docker-compose up --build`, just run this one command:

### Mac/Linux
```bash
bash run.sh
```

### Windows
```bash
run.bat
```

That's it! It will handle everything automatically.

## What It Does

When you run that command:
1. ✅ Checks Docker is installed
2. ✅ Checks Python is installed
3. ✅ Checks Ollama is running
4. ✅ Frees any ports that are in use
5. ✅ Starts all services
6. ✅ Tells you when it's ready

## Prerequisites (One-Time Setup)

Make sure these are installed:
- Docker: https://www.docker.com
- Ollama: https://ollama.ai
- Python: https://www.python.org

## Keep This Running

Before starting the project, make sure Ollama is running:
```bash
ollama serve
```

Keep this terminal open while using the project.

## Access the Application

Once the startup script completes:
- Open browser to: http://localhost:3000
- Everything should work!

## If Something Goes Wrong

If port conflicts or issues occur, the script handles them automatically. If you still have problems:

```bash
# Check service health
python3 scripts/integration_test.py

# Check logs
docker logs pmbot-backend
```

## That's It!

Just remember:
- **Mac/Linux:** `bash run.sh`
- **Windows:** `run.bat`

No need to know about `docker-compose` or port numbers. Everything is automatic! 🎉
