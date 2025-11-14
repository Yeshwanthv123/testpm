# PMBOT Deployment Checklist

This checklist ensures PMBOT is properly configured for deployment.

## ✅ Pre-Deployment Checklist

### Repository Setup
- [ ] Repository has `.env.example` files for both backend and frontend
- [ ] Actual `.env` files are in `.gitignore` and NOT committed
- [ ] `.gitignore` contains `!backend/.env.example` and `!Frontend/.env.example` to force track examples
- [ ] All setup scripts are executable and included
- [ ] README.md has clear setup instructions
- [ ] SETUP.md exists with detailed troubleshooting

### Backend Configuration (`backend/.env.example`)
- [ ] DATABASE_URL configured correctly
- [ ] JWT_SECRET is a placeholder (not real secret)
- [ ] JWT_REFRESH_SECRET is a placeholder
- [ ] CORS_ORIGINS includes correct frontend URL
- [ ] LLM_API_URL points to correct wrapper service
- [ ] LLM_MODEL matches available models (llama3, qwen2:7b-instruct)
- [ ] LLM_FORCE=1 to enable AI mode
- [ ] PM_QUESTIONS_CSV path is correct

### Frontend Configuration (`Frontend/.env.example`)
- [ ] VITE_API_BASE points to backend URL
- [ ] No sensitive information exposed

### Docker Configuration
- [ ] docker-compose.yml includes all 4 services (db, backend, frontend, llm-stub)
- [ ] Volume mounts are correct
- [ ] Port mappings are sensible
- [ ] Health checks configured for database
- [ ] Environment variables passed correctly to services
- [ ] .env file references use `env_file` directive

### AI/LLM Configuration
- [ ] Ollama server accessible via `host.docker.internal:11434` (Windows/Mac)
- [ ] Required models pre-downloaded on host:
  - [ ] llama3
  - [ ] qwen2:7b-instruct
- [ ] Request timeouts set to 600 seconds (10 minutes) for LLM inference:
  - [ ] `_query_ollama()` timeout = 600s
  - [ ] `_wrapper_generate_answer()` timeout = 600s
  - [ ] `_wrapper_evaluate_answer()` timeout = 600s
- [ ] Flask wrapper properly proxies to host Ollama
- [ ] Response normalization handles both nested and flat JSON

### Frontend Integration
- [ ] `App.tsx` has `isSubmitting` state for loading feedback
- [ ] `handleInterviewComplete()` properly handles timeouts
- [ ] Navigation to `/results` works after interview submission
- [ ] `Dashboard.tsx` displays all AI fields:
  - [ ] model_answer (500+ words)
  - [ ] score (0-100)
  - [ ] strengths (bullet points)
  - [ ] weaknesses/improvements (bullet points)
  - [ ] feedback (human-readable summary)

### Documentation
- [ ] README.md updated with setup instructions
- [ ] SETUP.md created with detailed guide
- [ ] COMMANDS.md created with common commands
- [ ] Setup scripts created (setup.ps1, setup.sh)
- [ ] First-run scripts created (first-run.ps1, first-run.bat, first-run.sh)
- [ ] Architecture diagram included in documentation

### Security
- [ ] .env files never committed to git
- [ ] Secrets are placeholders in .env.example
- [ ] CORS configured appropriately
- [ ] JWT secrets use strong values in production
- [ ] Database password not exposed in code
- [ ] OAuth credentials (if used) stored only in .env

### Testing on Fresh Clone
- [ ] Clone repository on new machine
- [ ] Run `git clone https://github.com/Yeshwanthv123/PMBOTNEW.git`
- [ ] Navigate to directory: `cd PMBOTNEW`
- [ ] Run setup script: `.\scripts\first-run.ps1` or `bash scripts/first-run.sh`
- [ ] Verify all services start: `docker compose ps`
- [ ] Test backend health: `curl http://localhost:8000/health`
- [ ] Access frontend: `http://localhost:3000`
- [ ] Complete full interview flow:
  - [ ] Register/login
  - [ ] Start interview
  - [ ] Submit answers
  - [ ] View results with AI feedback

## 📋 Required Files Checklist

### Must Exist (Committed to Git)
- [ ] README.md - Main documentation
- [ ] SETUP.md - Detailed setup guide
- [ ] COMMANDS.md - Common commands reference
- [ ] docker-compose.yml - Container configuration
- [ ] backend/.env.example - Backend config template
- [ ] Frontend/.env.example - Frontend config template
- [ ] scripts/setup.ps1 - Windows setup script
- [ ] scripts/setup.sh - Unix setup script
- [ ] scripts/first-run.ps1 - Windows automated setup
- [ ] scripts/first-run.bat - Windows automated setup (batch)
- [ ] scripts/first-run.sh - Unix automated setup
- [ ] .gitignore - Excludes actual .env files but includes .env.example

### Must NOT Exist (Gitignored)
- [ ] backend/.env - Never commit actual env file
- [ ] Frontend/.env - Never commit actual env file
- [ ] Any file containing real secrets or API keys

## 🔍 Verification Steps

### 1. Fresh Clone Test
```bash
# Remove local copy
rm -rf PMBOTNEW

# Clone fresh
git clone https://github.com/Yeshwanthv123/PMBOTNEW.git
cd PMBOTNEW

# Run setup
./scripts/first-run.sh  # or first-run.ps1 on Windows

# Verify
docker compose ps
curl http://localhost:8000/health
```

### 2. Environment File Verification
```bash
# Should exist (tracked)
ls backend/.env.example
ls Frontend/.env.example

# Should NOT exist until setup runs
ls backend/.env    # Should fail initially
ls Frontend/.env   # Should fail initially

# After setup
./scripts/setup.sh
ls backend/.env    # Should succeed
ls Frontend/.env   # Should succeed
```

### 3. Docker Verification
```bash
# Should build successfully
docker compose build

# Should start without errors
docker compose up -d

# Check all services healthy
docker compose ps

# Verify each service
curl http://localhost:8000/health           # Backend
docker compose exec pmbot-llm-stub curl localhost:5000/health  # Wrapper
```

### 4. Full Integration Test
```bash
# Frontend loads
curl http://localhost:3000

# Backend responds
curl http://localhost:8000/health

# Can make auth request
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Interview endpoint responds
curl http://localhost:8000/api/questions
```

## 🚀 Production Deployment Checklist

### Before Going Live
- [ ] All placeholder secrets in `.env.example` are clearly marked
- [ ] Documentation explains how to set production secrets
- [ ] Database backups are configured
- [ ] Monitoring/logging is set up
- [ ] CORS is restricted to production domain only
- [ ] SSL/TLS certificates configured
- [ ] Database connection pooling configured
- [ ] Rate limiting configured for API
- [ ] Backup and disaster recovery plan documented

### Environment Variables to Change for Production
```
JWT_SECRET=<generate-random-64-char-string>
JWT_REFRESH_SECRET=<generate-random-64-char-string>
SECRET_KEY=<generate-random-64-char-string>
CORS_ORIGINS=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
OAUTH_REDIRECT_BASE=https://yourdomain.com
DATABASE_URL=postgresql://prod_user:secure_password@db-host:5432/pmbot_prod
```

## 📝 Intern Handoff Checklist

When handing to intern:
- [ ] Provide link to this repo
- [ ] Point to SETUP.md for first-time setup
- [ ] Point to COMMANDS.md for daily operations
- [ ] Ensure they have Docker Desktop installed
- [ ] Ensure they have Ollama installed
- [ ] Have them complete fresh setup on their machine
- [ ] Verify they can access app at localhost:3000
- [ ] Provide backend API documentation
- [ ] Set up any credentials they need (GitHub, etc.)

## ✨ Success Criteria

Your deployment is ready when:

✅ Fresh clone + setup script works without errors  
✅ All services start and are healthy  
✅ Frontend loads at http://localhost:3000  
✅ Backend responds at http://localhost:8000  
✅ Can complete full interview workflow  
✅ AI evaluation returns real feedback (not templates)  
✅ Results display all fields correctly  
✅ No .env files accidentally committed  
✅ All documentation is clear and complete  
✅ Setup takes <5 minutes on a new machine  

## 🆘 If Something Goes Wrong

1. Check SETUP.md troubleshooting section
2. Run `docker compose logs` to see detailed errors
3. Verify Ollama is running: `ollama list`
4. Verify models are downloaded: `ollama serve` should show them
5. Check .gitignore: `.env` files should be ignored
6. Verify all scripts are executable (Unix systems)
7. Check docker-compose.yml for environment variable errors

---

**Last Updated:** November 2025  
**Version:** 1.0.0
