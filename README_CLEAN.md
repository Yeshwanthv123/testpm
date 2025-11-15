# PM Bot - Project Manager Interview Assistant

An intelligent interview training platform powered by AI. Practice, get evaluated, and improve your Project Manager interview skills.

## ⚡ 30-Second Setup

### Fresh Clone? Just Run This:

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

✅ Everything else happens automatically!

---

## 🎯 What is PM Bot?

PM Bot is an AI-powered interview training platform that:
- 🎯 Tests you with 18,000+ authentic PM interview questions
- 🤖 Uses AI to evaluate your answers in real-time
- 📊 Compares your performance with other candidates
- 🏆 Tracks improvement over time
- 🌍 Supports multiple regions (India, US, EU, APAC)
- 🔐 Secure login with Google OAuth

## 🌐 Access After Setup

| Component | URL |
|-----------|-----|
| **Application** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Database** | localhost:5432 (postgres) |

## 📚 Documentation

### Getting Started
- **[QUICK_START.md](./QUICK_START.md)** - Fastest way to get running (5 minutes)
- **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** - Detailed setup with all options
- **[SETUP_FOR_REVIEW.md](./SETUP_FOR_REVIEW.md)** - Setup guide for code reviews

### Development & Troubleshooting
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[Backend README](./backend/README.md)** - Backend architecture and APIs
- **[Frontend README](./Frontend/README.md)** - Frontend setup and development
- **[COMMANDS.md](./COMMANDS.md)** - Docker and useful commands

### Project Info
- **[PRODUCTION_READY.md](./PRODUCTION_READY.md)** - Production deployment checklist
- **[FINAL_SUMMARY.md](./FINAL_SUMMARY.md)** - Complete project summary

## 🏗️ Project Architecture

### Tech Stack
```
Frontend:  React 20 + TypeScript + Vite 5.4.8 + Tailwind CSS
Backend:   FastAPI (Python 3.10) + SQLAlchemy ORM
Database:  PostgreSQL 13.23
LLM:       Qwen2:7b-instruct (via HTTP)
Deploy:    Docker Compose v2.0+
```

### 4 Services (All in Docker)

| Service | Tech | Port | Purpose |
|---------|------|------|---------|
| **Frontend** | React + TypeScript | 3000 | Web interface |
| **Backend** | FastAPI + Python | 8000 | API & AI evaluation |
| **Database** | PostgreSQL | 5432 | Data persistence |
| **LLM** | Qwen2 + Flask | 5000 | AI model service |

## ✨ Key Features

### 📝 Interview Practice
- 18,168 authentic PM interview questions
- Questions organized by region and topic
- Realistic interview scenarios

### 🤖 AI Evaluation
- Real-time answer evaluation (0-100 score)
- Detailed feedback on strengths and weaknesses
- AI-powered improvement suggestions
- Honest assessment and constructive criticism

### 📊 Performance Tracking
- Personal interview history
- Performance trends and improvement rate
- Percentile rankings:
  - **Regional**: Compare with candidates in your region
  - **Experience**: Compare with similar experience level
  - **Global**: See your standing worldwide
- Category-wise performance breakdown

### 🏆 Social Features
- Leaderboards (Global, Regional, Experience-based)
- Share your results with others
- Download performance reports
- Compare with peers

### 🔐 Security
- Google OAuth 2.0 authentication
- JWT token-based API security
- Secure database with password hashing
- Environment-based configuration

## 🚀 First Run Walkthrough

1. **Run Setup**
   ```bash
   # Windows
   setup.bat
   
   # macOS/Linux
   ./setup.sh
   ```

2. **Open Application**
   - Go to http://localhost:3000

3. **Sign Up**
   - Click "Sign Up"
   - Use Google OAuth or create account
   - Fill in your name and email

4. **Complete Onboarding**
   - Select your region (India/US/EU/APAC)
   - Choose your experience level
   - Select interview topics

5. **Start Practicing**
   - Begin with easy questions
   - Record your answer (or type)
   - Get AI feedback
   - View your score
   - Check leaderboard rankings

## 🔍 Verify Setup

After running the setup script, verify everything works:

**Windows:**
```bash
docker-health-check.bat
```

**macOS/Linux:**
```bash
./docker-health-check.sh
```

Should see: ✅ All services running and responding

## 🛠️ Useful Commands

### View Everything
```bash
# All services and logs
docker compose logs -f

# Just one service
docker compose logs -f pmbot-backend
```

### Control Services
```bash
# Stop everything
docker compose down

# Start again
docker compose up -d

# Restart one service
docker compose restart pmbot-backend
```

### Database Access
```bash
# Open database console
docker compose exec pmbot-db psql -U postgres -d mydatabase

# Useful commands inside database:
\dt              # List all tables
SELECT COUNT(*) FROM questions;  # Count questions
\q               # Exit
```

## ❓ Issues?

See **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** for:
- Port already in use
- Services won't start
- Slow startup times
- Docker not found
- API errors
- Database connection issues

## 👨‍💻 Development

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

### Database
- Location: `/var/lib/postgresql/data` (in container)
- User: `postgres`
- Password: Check `backend/.env`
- Database: `mydatabase`
- Port: `5432`

## 📦 Environment Variables

All `.env` files are auto-created from `.env.example` templates:

**Frontend (.env):**
```
VITE_API_BASE=http://localhost:8000
```

**Backend (.env):**
```
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
GOOGLE_CLIENT_ID=your-client-id
```

See **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** for all variables.

## 🌟 Features Overview

| Feature | Status | Details |
|---------|--------|---------|
| Interview Questions | ✅ Complete | 18,168 questions loaded |
| AI Evaluation | ✅ Complete | Qwen2 model integrated |
| User Authentication | ✅ Complete | Google OAuth + JWT |
| Leaderboards | ✅ Complete | Global, Regional, Experience |
| Performance Tracking | ✅ Complete | Scores, percentiles, trends |
| Admin Features | ✅ Complete | User management, reports |
| Mobile Responsive | ✅ Complete | Works on all devices |

## 📊 Data

### Questions Database
- **Total Questions:** 18,168
- **Source:** PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv
- **Categories:** Multiple PM domains
- **Auto-loaded:** On first run

### Sample Regions
- India (most users)
- United States
- European Union
- APAC region

## 🔒 Security

- ✅ Google OAuth 2.0
- ✅ JWT token authentication
- ✅ Password hashing (bcrypt)
- ✅ CORS properly configured
- ✅ Environment secrets management
- ✅ Database connection encryption

## 📈 Performance

- **Questions Load:** < 1 second
- **AI Evaluation:** 3-5 seconds
- **Database Queries:** < 100ms
- **Leaderboard Updates:** Real-time
- **Concurrent Users:** Scales with Docker resources

## 🚢 Production Ready

For deploying to production:
1. See [PRODUCTION_READY.md](./PRODUCTION_READY.md)
2. Configure environment variables
3. Set up proper secrets management
4. Configure reverse proxy (nginx/traefik)
5. Set up HTTPS/SSL
6. Configure backup strategy

## 📞 Support & Troubleshooting

1. **Quick Check:** Run `docker-health-check.bat/sh`
2. **View Logs:** `docker compose logs -f`
3. **Full Guide:** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
4. **Setup Help:** See [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)

## 🎓 Learning Resources

- FastAPI Docs: http://localhost:8000/docs
- Frontend: React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, SQLAlchemy
- Database: PostgreSQL, SQL
- DevOps: Docker, Docker Compose

## 📝 License

This project is proprietary. All rights reserved.

## 🙏 Contributors

Built with ❤️ for aspiring Project Managers

---

### Next Steps

1. **New User?** → See [QUICK_START.md](./QUICK_START.md)
2. **Having Issues?** → See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. **Full Setup Details?** → See [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)
4. **Want to Review Code?** → See [SETUP_FOR_REVIEW.md](./SETUP_FOR_REVIEW.md)

---

**Ready to practice? Run `setup.bat` or `./setup.sh` now! 🚀**
