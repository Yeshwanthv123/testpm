# 🚀 PM Bot - START HERE

Welcome! This is your starting point. Follow these steps to get the entire project running in just a few minutes.

## ⚡ The 30-Second Setup

Pick your operating system and run ONE command:

### Windows PowerShell or Command Prompt
```bash
setup.bat
```

### macOS or Linux
```bash
chmod +x setup.sh
./setup.sh
```

**That's it!** Everything else happens automatically. ✅

---

## 📋 What Just Happened?

The setup script:
1. ✅ Checked Docker installation
2. ✅ Created environment files
3. ✅ Built Docker images
4. ✅ Started all 4 services
5. ✅ Waited for everything to be ready
6. ✅ Showed you the access URLs

---

## 🌐 Access Your Application

Once setup completes, open these in your browser:

| Component | URL |
|-----------|-----|
| **Application** | http://localhost:3000 |
| **API Documentation** | http://localhost:8000/docs |

---

## 🎯 First Time? Here's What to Do

1. **Open** http://localhost:3000
2. **Click** "Sign Up"
3. **Login** with Google or create account
4. **Select** your region (India, US, EU, APAC)
5. **Choose** your experience level
6. **Start** practicing!

---

## ❓ Did Something Go Wrong?

### 1. Docker not found?
**Install Docker:** https://docs.docker.com/get-docker/

After installing, run the setup script again.

### 2. Port already in use?
**Automatic Fix (Easiest):**

Windows:
```bash
fix-ports.bat
```

macOS/Linux:
```bash
chmod +x fix-ports.sh
./fix-ports.sh
```

**Manual Check:**
- Windows: `netstat -ano | findstr :3000`
- macOS/Linux: `lsof -i :3000`

### 3. Services won't start?
```bash
# Check what's happening
docker compose logs -f

# Restart everything
docker compose down
docker compose up -d
```

### 4. Need more help?
See **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** for detailed solutions.

---

## 📚 Full Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Quick reference
- **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** - Detailed guide
- **[README.md](./README.md)** - Project overview
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Problem solving

---

## ✅ Verify Everything Works

After setup, run the health check:

### Windows
```bash
docker-health-check.bat
```

### macOS/Linux
```bash
chmod +x docker-health-check.sh
./docker-health-check.sh
```

Should show: **[OK]** for all services ✅

---

## 🛠️ Useful Commands

### View logs (all services)
```bash
docker compose logs -f
```

### View logs (specific service)
```bash
docker compose logs -f pmbot-backend
```

### Stop everything
```bash
docker compose down
```

### Start everything again
```bash
docker compose up -d
```

### Access database
```bash
docker compose exec pmbot-db psql -U postgres -d mydatabase
```

---

## 🏗️ What's Running?

Your project has 4 services running in Docker:

| Service | Port | What it does |
|---------|------|-------------|
| **Frontend** | 3000 | Web interface (React) |
| **Backend** | 8000 | API and AI evaluation |
| **Database** | 5432 | Data storage (PostgreSQL) |
| **LLM Service** | 5000 | AI model (Qwen2) |

---

## 🚀 Ready to Code?

### Frontend Development
```bash
cd Frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

---

## 💡 Pro Tips

1. **First run takes longer** - Docker is downloading images. Next runs are faster.
2. **Database initializes automatically** - Questions load on first startup.
3. **Changes auto-reload** - Edit code and refresh browser to see changes.
4. **Check logs if stuck** - Always helpful: `docker compose logs -f`

---

## 📊 Project at a Glance

- **Language:** Python (backend), TypeScript (frontend)
- **Database:** PostgreSQL
- **AI Model:** Qwen2 7B
- **Questions:** 18,168 PM interview questions
- **Deployment:** Docker Compose
- **Auth:** Google OAuth 2.0

---

## 🎓 What is PM Bot?

An AI-powered platform that:
- 📝 Gives you 18,000+ PM interview questions
- 🤖 Uses AI to evaluate your answers
- 📊 Tracks your improvement
- 🏆 Compares you with other candidates
- 🌍 Works globally with regional rankings

---

## 📞 Support Checklist

Having issues? Check these in order:

1. ✅ Docker is installed and running
2. ✅ Ports 3000, 8000, 5432, 5000 are available
3. ✅ You have internet (for Docker images)
4. ✅ Environment files were created (run setup again)
5. ✅ All services are running (`docker compose ps`)
6. ✅ Check logs: `docker compose logs -f`

---

## 🚀 You're All Set!

**Next Step:** Open http://localhost:3000 and start practicing!

---

### Still need help?
- **Quick questions:** See [QUICK_START.md](./QUICK_START.md)
- **Setup details:** See [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Tech details:** See [README.md](./README.md)

---

**Made with ❤️ for aspiring Project Managers**

*Last Updated: 2024*
