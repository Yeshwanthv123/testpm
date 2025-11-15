# PM Bot - Quick Start Guide

Welcome to PM Bot! This guide will get you up and running in just a few minutes.

## ⚡ Quick Start (5 minutes)

### On Windows
```bash
setup.bat
```

### On macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

That's it! The script will:
- ✅ Check Docker installation
- ✅ Create environment files
- ✅ Build Docker images
- ✅ Start all services
- ✅ Wait for services to be ready

## 🌐 Access Your Application

Once setup completes, open your browser to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🚀 What's Next?

1. Sign up or login with Google
2. Select your region (India, US, EU, APAC)
3. Complete the onboarding
4. Start practicing PM interview questions!

## 📋 Project Structure

```
PMBOTNEW/
├── Frontend/              # React TypeScript application
├── backend/               # FastAPI Python backend
├── docker-compose.yml     # Docker service configuration
├── setup.sh              # Automated setup script (macOS/Linux)
├── setup.bat             # Automated setup script (Windows)
├── docker-health-check.sh # Health check script (macOS/Linux)
├── docker-health-check.bat # Health check script (Windows)
└── COMPLETE_SETUP_GUIDE.md # Detailed setup documentation
```

## 🐳 Services

The project runs 4 Docker containers:

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 3000 | React application |
| **Backend** | 8000 | FastAPI server |
| **Database** | 5432 | PostgreSQL database |
| **LLM Service** | 5000 | Qwen2 AI model |

## 🔍 Verify Everything Works

Check that all services are running:

### Windows
```bash
docker-health-check.bat
```

### macOS/Linux
```bash
./docker-health-check.sh
```

## 🛠️ Common Commands

### View logs
```bash
docker compose logs -f
```

### View specific service logs
```bash
docker compose logs -f pmbot-backend
```

### Restart services
```bash
docker compose restart
```

### Stop services
```bash
docker compose down
```

### Start services again
```bash
docker compose up -d
```

### Access database
```bash
docker compose exec pmbot-db psql -U postgres -d mydatabase
```

## 🔑 Default Credentials

- **Database User**: postgres
- **Database Password**: Check `backend/.env`
- **Database Name**: mydatabase

## ❓ Issues?

### Port already in use?
**Automatic Fix (Recommended):**

Windows:
```bash
fix-ports.bat
```

macOS/Linux:
```bash
chmod +x fix-ports.sh
./fix-ports.sh
```

This will automatically kill any processes using ports 3000, 8000, 5432, or 5000.

**Manual Fix:**
```bash
# Find what's using port 3000
# Windows:
netstat -ano | findstr :3000

# macOS/Linux:
lsof -i :3000

# Then stop the process or change ports in docker-compose.yml
```

### Services won't start?
1. Check Docker is running: `docker --version`
2. Run port fix: `fix-ports.bat` or `./fix-ports.sh`
3. Check logs: `docker compose logs -f`
4. See COMPLETE_SETUP_GUIDE.md for detailed troubleshooting

### Docker takes too long to start?
This is normal on first run (downloading images, initializing database). Subsequent runs are much faster.

## 📚 Full Documentation

For more detailed information, see:
- **COMPLETE_SETUP_GUIDE.md** - Comprehensive setup and configuration
- **README.md** - Project overview
- **COMMANDS.md** - Docker and development commands

## 🚀 Development

To contribute or develop:

1. Frontend changes: Edit files in `Frontend/src/`
2. Backend changes: Edit files in `backend/app/`
3. Changes automatically reload in development (if you set up development mode)

## 📞 Support

If you encounter issues:
1. Check COMPLETE_SETUP_GUIDE.md troubleshooting section
2. Review Docker logs: `docker compose logs -f`
3. Verify all ports are available
4. Ensure Docker Desktop is running (Windows/macOS)

---

**Happy practicing! 🎉**
