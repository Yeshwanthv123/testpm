# 🚀 PMBOT - The Simplest Setup Ever!

## All You Need to Know

### Prerequisites (Install Once)
1. **Docker Desktop** - https://www.docker.com/products/docker-desktop
2. **Ollama** - https://ollama.ai

That's it! ✨

### Run PMBOT

**Windows:**
```
Double-click: start_pmbot.bat
```

**Mac/Linux:**
```
bash start_pmbot.sh
```

### Access It
```
Open browser: http://localhost:3000
```

---

## What Happens Automatically

✅ Checks Docker is running
✅ Checks Ollama is available  
✅ Detects and configures ports (handles conflicts!)
✅ Downloads AI model if needed (~4GB, first time only)
✅ Starts all services
✅ Shows when ready

---

## Troubleshooting (5 Common Issues)

### "Docker not running"
**Fix:** Start Docker Desktop, then run startup script again

### "Ollama not responding"
**Fix:** Open terminal, run `ollama serve`, keep it open, then run startup script again

### "Port already in use"
**Fix:** Script auto-detects conflicts and uses different ports. Check `.ports.json` for actual port

### "Model download too slow"
**Fix:** First download takes 5-15 min (~4GB). Be patient, don't close terminal

### "Model download failed"
**Fix:** Script tries backup models. If still fails, run `ollama pull llama2` manually

---

## First Run Timeline

```
Startup        0-10 sec
Port Detection 10-20 sec
Model Download 20-300 sec (depends on internet speed)
Docker Start   300-350 sec
Ready!         🎉
```

---

## That's All!

No Python to install.
No setup files to configure.
No dependencies to manage.

**Just run and go!** 🚀
