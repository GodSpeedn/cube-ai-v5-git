# 🚀 Universal Startup Guide

## Quick Start

Choose one of these startup methods:

### Option 1: Windows Batch File (Recommended for Windows)
```bash
# Double-click or run:
start_all.bat
```

### Option 2: PowerShell Script (Windows)
```powershell
# Right-click and "Run with PowerShell" or:
powershell -ExecutionPolicy Bypass -File start_all.ps1
```

### Option 3: Python Script (Cross-Platform)
```bash
# Works on Windows, macOS, Linux:
python start_all.py
```

---

## What Each Script Does

### 🔧 Automatic Setup
- ✅ Checks if Python and Node.js are installed
- ✅ Creates Python virtual environment if needed
- ✅ Installs Python dependencies from `requirements.txt`
- ✅ Installs Node.js dependencies with `npm install`
- ✅ Checks GitHub configuration in `keys.txt`

### 🚀 Starts All Services
- 📡 **Main Backend** (Port 8000) - Core API and file management
- 🤖 **Online Agent Service** (Port 8001) - AI agent workflows
- 🌐 **Frontend** (Port 3000) - React web interface

### 🌐 Opens Browser
- Automatically opens http://localhost:3000 in your default browser

---

## Service URLs

After starting, you can access:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main web interface |
| **Main Backend** | http://localhost:8000 | API endpoints, file management |
| **Online Agents** | http://localhost:8001 | AI agent workflows |

---

## Prerequisites

### Required Software
- **Python 3.8+** - [Download here](https://python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/downloads/)

### Required Files
- `backend-ai/requirements.txt` - Python dependencies
- `offline-ai-frontend/package.json` - Node.js dependencies

---

## GitHub Auto-Upload Setup

To enable automatic code upload to GitHub:

1. **Get GitHub Token**:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `workflow`, `write:packages`
   - Copy the token

2. **Edit Configuration**:
   ```bash
   # Edit backend-ai/keys.txt
   GITHUB_TOKEN=ghp_your_actual_token_here
   GITHUB_USERNAME=your_github_username
   ```

3. **Restart Services**:
   - Close all service windows
   - Run startup script again

---

## Troubleshooting

### ❌ "Python not found"
**Solution**: Install Python from https://python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### ❌ "Node.js not found"
**Solution**: Install Node.js from https://nodejs.org/downloads/
- Choose LTS version

### ❌ "backend-ai folder not found"
**Solution**: Run the script from the project root directory
- The script should be in the same folder as `backend-ai/` and `offline-ai-frontend/`

### ❌ "Port already in use" (Error 10048)
**Quick Fix**: 
```bash
# Run the port conflict resolver:
resolve_port_conflicts.bat
```

**Advanced Port Management**:
```bash
# Full port management tool:
manage_ports.bat
```

**Startup Script Options**:
- The improved `start_all.bat` now detects port conflicts and offers options:
  - Option 1: Kill existing services and restart (Recommended)
  - Option 2: Start services anyway (will show errors)
  - Option 3: Exit and check manually
  - Option 4: Show detailed port information

**Manual Fix**:
1. Run `stop_all.bat` to stop all services
2. Then run `start_all.bat` again

### ❌ "GitHub upload not working"
**Solution**:
- Check `backend-ai/keys.txt` has valid credentials
- Verify token has correct scopes (`repo`, `workflow`, `write:packages`)
- Check service logs for error messages

### ❌ "Frontend not loading"
**Solution**:
- Wait a few minutes for compilation to complete
- Check the frontend window for error messages
- Try refreshing the browser

---

## Manual Service Control

If you prefer to start services individually:

### Main Backend
```bash
cd backend-ai
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Online Agent Service
```bash
cd backend-ai
# Activate virtual environment (same as above)
python online_agent_service.py
```

### Frontend
```bash
cd offline-ai-frontend
npm install
npm run dev
```

---

## Service Management

### Stop All Services
- Close all command/terminal windows
- Or press `Ctrl+C` in each service window

### Restart Services
- Stop all services
- Run startup script again

### Check Service Status
- Look at each service window for error messages
- Check browser console for frontend errors
- Visit service URLs to test connectivity

---

## File Structure

```
project-root/
├── start_all.bat          # Windows batch file
├── start_all.ps1          # PowerShell script
├── start_all.py           # Cross-platform Python script
├── STARTUP_GUIDE.md       # This guide
├── backend-ai/
│   ├── main.py            # Main backend service
│   ├── online_agent_service.py  # Online agent service
│   ├── requirements.txt   # Python dependencies
│   ├── keys.txt          # API keys and GitHub config
│   └── venv/             # Python virtual environment
└── offline-ai-frontend/
    ├── package.json       # Node.js dependencies
    ├── src/              # React source code
    └── node_modules/     # Node.js dependencies
```

---

## Support

If you encounter issues:

1. **Check the logs** in each service window
2. **Verify prerequisites** (Python, Node.js)
3. **Check file structure** (all folders present)
4. **Test individual services** manually
5. **Check GitHub configuration** if upload issues

---

## Success Indicators

When everything is working correctly, you should see:

✅ **All three services started**  
✅ **No error messages in service windows**  
✅ **Frontend loads at http://localhost:3000**  
✅ **GitHub auto-upload works** (if configured)  
✅ **Agent workflows function properly**  

🎉 **You're ready to use the AI agent system!**
