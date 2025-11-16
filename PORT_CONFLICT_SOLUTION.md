# Port 5432 (Database) Already in Use - Solution Guide

If you see this error:
```
(HTTP code 500) server error - Ports are not available: 
exposing port TCP 0.0.0.0:5432 -> 127.0.0.1:0: 
listen tcp 0.0.0.0:5432: bind: address already in use
```

**This means another process is using port 5432 (the database port).**

## ✅ Solution 1: Automatic Fix (Recommended)

### Windows
```bash
fix-ports.bat
```

Then try setup again:
```bash
setup.bat
```

### macOS/Linux
```bash
chmod +x fix-ports.sh
./fix-ports.sh
```

Then try setup again:
```bash
chmod +x setup.sh
./setup.sh
```

**The script will automatically kill any processes using required ports.**

---

## ✅ Solution 2: Manual Fix

### Windows - Find and Kill Process

**Step 1: Find what's using port 5432**
```bash
netstat -ano | findstr :5432
```

You'll see output like:
```
TCP    0.0.0.0:5432    0.0.0.0:0    LISTENING    1234
```

The number at the end (1234) is the Process ID (PID).

**Step 2: Kill the process**
```bash
taskkill /PID 1234 /F
```

Replace `1234` with the actual PID from Step 1.

---

### macOS/Linux - Find and Kill Process

**Step 1: Find what's using port 5432**
```bash
lsof -i :5432
```

Or:
```bash
sudo lsof -i :5432
```

You'll see output showing the PID and process name.

**Step 2: Kill the process**
```bash
kill -9 <PID>
```

Or if you need admin rights:
```bash
sudo kill -9 <PID>
```

Replace `<PID>` with the actual process ID.

---

## ✅ Solution 3: Stop Docker Containers

If the port is being used by a previous Docker container:

### Windows/macOS/Linux

**Stop all Docker containers:**
```bash
docker compose down -v
```

Or stop all containers:
```bash
docker stop $(docker ps -q)
```

Or remove containers using the port:
```bash
docker rm -f $(docker ps -a | grep 5432 | awk '{print $1}')
```

---

## ✅ Solution 4: Change the Port

If you can't free port 5432, you can change it in `docker-compose.yml`:

**Open `docker-compose.yml` and find the database service:**

**Before:**
```yaml
pmbot-db:
  image: postgres:13
  ports:
    - "5432:5432"  ← Change this first number
  environment:
    POSTGRES_PASSWORD: password
```

**After (using port 5433 instead):**
```yaml
pmbot-db:
  image: postgres:13
  ports:
    - "5433:5432"  ← Changed to 5433
  environment:
    POSTGRES_PASSWORD: password
```

Also update `backend/.env`:
```
DATABASE_URL=postgresql://user:password@db:5433/mydatabase
                                              ↑ Change from 5432 to 5433
```

---

## 🔍 Check What's Using Each Port

### Windows
```bash
netstat -ano | findstr :3000   # Frontend
netstat -ano | findstr :8000   # Backend
netstat -ano | findstr :5432   # Database
netstat -ano | findstr :5000   # LLM Service
```

### macOS/Linux
```bash
lsof -i :3000   # Frontend
lsof -i :8000   # Backend
lsof -i :5432   # Database
lsof -i :5000   # LLM Service
```

---

## 🛠️ Common Port Conflicts

| Service | Port | Usually Used By |
|---------|------|-----------------|
| Frontend | 3000 | Node.js, other apps |
| Backend | 8000 | FastAPI, Flask, other web apps |
| Database | 5432 | PostgreSQL, other databases |
| LLM | 5000 | Flask, other web services |

---

## 🚀 After Fixing Ports

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
./setup.sh
```

The setup script now **automatically checks and frees ports** before starting!

---

## 📞 Still Having Issues?

1. Run the automatic port fixer: `fix-ports.bat` or `./fix-ports.sh`
2. Stop all Docker: `docker compose down -v`
3. Restart your computer (clears all ports)
4. Try setup again: `setup.bat` or `./setup.sh`

**The updated setup script now handles port conflicts automatically!**
