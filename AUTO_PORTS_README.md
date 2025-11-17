# Auto-Port Detection & Configuration

This system automatically detects available ports and updates all configuration files whenever port conflicts occur.

## 🚀 Quick Start

### Windows
```bash
.\start_with_auto_ports.bat
```

### Mac/Linux
```bash
bash start_with_auto_ports.sh
chmod +x start_with_auto_ports.sh
```

## 🔧 How It Works

1. **Port Detection** (`scripts/detect_ports.py`)
   - Scans default ports (8000, 3000, 5432)
   - Finds available alternatives if ports are in use
   - Updates `.env` files automatically

2. **Configuration Updates**
   - `backend/.env` → Updates `VITE_API_BASE` and `DATABASE_URL`
   - `Frontend/.env` → Updates `VITE_API_BASE`
   - `docker-compose.yml` → Port mappings stay consistent

3. **Services Started**
   - Docker Compose uses updated configuration
   - All services know about new ports

## 📝 What Gets Updated

### Backend `.env`
```ini
VITE_API_BASE=http://localhost:8001  # Auto-updated if 8000 is busy
DATABASE_URL=postgresql://...@localhost:5433/pmbot  # Auto-updated if 5432 is busy
```

### Frontend `.env`
```ini
VITE_API_BASE=http://localhost:8001  # Auto-updated to match backend port
```

### Port Configuration
Saved to `.ports.json` for reference:
```json
{
  "pmbot-backend": 8001,
  "pmbot-frontend": 3000,
  "pmbot-db": 5433
}
```

## ✅ Features

- ✅ **Automatic Conflict Resolution**: Finds available ports if defaults are in use
- ✅ **No Manual Configuration**: Updates all files automatically
- ✅ **Works Across Devices**: Different machines = different port configs, all handled
- ✅ **Cross-Platform**: Windows, Mac, Linux support
- ✅ **Logging**: Shows what ports are being used
- ✅ **Persistent Configuration**: Saves port config for reference

## 🔄 Manual Port Configuration

If you need specific ports, edit `docker-compose.yml` before running:

```yaml
services:
  pmbot-backend:
    ports:
      - "9000:8000"  # Custom port
  pmbot-frontend:
    ports:
      - "3001:3000"  # Custom port
```

Then run the auto-port detection script to update `.env` files:

```bash
# Windows
python scripts\detect_ports.py

# Mac/Linux
python3 scripts/detect_ports.py
```

## 🛠️ Troubleshooting

### "Python not found"
- Windows: Install from https://www.python.org
- Mac: `brew install python3`
- Linux: `sudo apt-get install python3`

### "PyYAML not installed"
The script will auto-install it. If that fails:
```bash
pip install pyyaml
```

### "Port detection not working"
Check if specific ports are in use:
```bash
# Windows
netstat -ano | findstr :8000

# Mac/Linux
lsof -i :8000
```

## 📊 Example Scenarios

### Scenario 1: Fresh Installation
```
$ start_with_auto_ports.bat
🔍 Detecting available ports...
✅ pmbot-backend: Port 8000 available
✅ pmbot-frontend: Port 3000 available
✅ pmbot-db: Port 5432 available
🚀 Starting Docker services...
```

### Scenario 2: Port Conflict on New Machine
```
$ start_with_auto_ports.sh
🔍 Detecting available ports...
⚠️  pmbot-backend: Port 8000 → 8001
✅ pmbot-frontend: Port 3000 available
⚠️  pmbot-db: Port 5432 → 5433
✅ Updated backend/.env
✅ Updated Frontend/.env
🚀 Starting Docker services...
```

### Scenario 3: Manual Port Change
```yaml
# Edit docker-compose.yml
ports:
  - "9000:8000"  # Custom
```

```bash
$ python3 scripts/detect_ports.py
✅ pmbot-backend: Port 9000 available
✅ Updated backend/.env (VITE_API_BASE=http://localhost:9000)
✅ Updated Frontend/.env
```

## 🔐 Environment Variable Priority

1. **Detected Ports** (auto-detection)
2. **Custom Ports** (docker-compose.yml)
3. **Default Ports** (8000, 3000, 5432)

## 💡 Best Practices

- ✅ Always run `start_with_auto_ports` scripts for fresh deployments
- ✅ Check `.ports.json` to see current configuration
- ✅ Use custom ports by editing `docker-compose.yml` first
- ✅ Commit `.env.example` files, not `.env` (already in .gitignore)

## 🚀 CI/CD Integration

The detection script can be integrated into CI/CD pipelines:

```bash
# Before Docker Compose
python3 scripts/detect_ports.py

# Then run Docker
docker compose up --build
```

---

**Questions?** Check the main README.md or SETUP.md for more details.
