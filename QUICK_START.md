# 🚀 QUICK START - Port Issues COMPLETELY SOLVED

## Your New Workflow

### Windows
```
1. Double-click:  start_pmbot.bat
2. Wait 30-60 seconds for startup
3. Open:         http://localhost:3000
4. Run your test!
```

### Mac/Linux
```
1. Run command:   bash start_pmbot.sh
2. Wait 30-60 seconds for startup
3. Open:         http://localhost:3000
4. Run your test!
```

---

## Automatic Features

✅ **Ports 8000, 3000, 5000, 5432 in use?** - Auto-freed
✅ **Service crashed?** - Auto-restarted
✅ **Need to check health?** - Run: `python3 scripts/integration_test.py`
✅ **Works on Windows, Mac, Linux** - Same command everywhere

---

## Prerequisites (One-Time)

1. Install Docker: https://www.docker.com
2. Install Ollama: https://ollama.ai
3. Run: `ollama pull qwen2:7b-instruct`
4. Keep running: `ollama serve`

---

## Scripts Reference

| Command | What It Does |
|---------|--------------|
| `start_pmbot.bat` / `.sh` | **One-click startup (use this!)** |
| `python3 scripts/free_ports.py` | Check port status |
| `python3 scripts/free_ports.py --auto` | Manually free ports |
| `python3 scripts/integration_test.py` | Check service health |
| `docker logs pmbot-backend` | See backend errors |

---

## Common Issues (All Fixed!)

| Issue | Before | Now |
|-------|--------|-----|
| Port already in use | Manual debugging (30 min) | Auto-fixed (0 min) |
| Need to change port | Edit 3 files manually | Auto-handled |
| Services won't connect | Check logs for hours | Run integration_test.py |
| AI score is zero | Debug service chain | Run integration_test.py |

---

## Documentation

- **[SOLUTION_SUMMARY.md](./SOLUTION_SUMMARY.md)** - Complete overview
- **[AUTOMATIC_PORT_LIBERATION.md](./AUTOMATIC_PORT_LIBERATION.md)** - How it works
- **[README.md](./README.md)** - Full guide
- **[AI_MODEL_ZERO_SCORE_FIX.md](./AI_MODEL_ZERO_SCORE_FIX.md)** - Troubleshooting

---

## That's It!

No more port conflicts. No more manual configuration.

Just run `start_pmbot.bat` or `bash start_pmbot.sh` and everything works! 🎉

---

**Questions?** Check the documentation files above or run `python3 scripts/integration_test.py`
