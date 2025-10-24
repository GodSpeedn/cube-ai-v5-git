@echo off
echo ============================================================
echo 🚀 Starting All Services - Backend, Online Agent, Frontend
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

:: Check if we're in the right directory
if not exist "backend-ai" (
    echo ❌ Error: backend-ai folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "offline-ai-frontend" (
    echo ❌ Error: offline-ai-frontend folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo 📁 Project root: %PROJECT_ROOT%
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

:: Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo ✅ Python and Node.js are available
echo.

:: Check if virtual environment exists
if not exist "backend-ai\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend-ai
    python -m venv venv
    cd ..
    echo ✅ Virtual environment created
)

:: Activate virtual environment
echo 🔧 Activating Python virtual environment...
call backend-ai\venv\Scripts\activate.bat

:: Load environment variables from keys.txt
echo 🔑 Loading API keys and GitHub configuration...
if exist "backend-ai\keys.txt" (
    for /f "usebackq tokens=1,2 delims==" %%a in ("backend-ai\keys.txt") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    echo ✅ Environment variables loaded from keys.txt
) else (
    echo ⚠️ Warning: keys.txt not found - GitHub auto-upload will not work
)

:: Install Python dependencies
echo 📦 Installing Python dependencies...
cd backend-ai
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Warning: Some Python dependencies may not have installed correctly
    echo Continuing anyway...
)
cd ..

:: Check if Node modules exist
if not exist "offline-ai-frontend\node_modules" (
    echo 📦 Installing Node.js dependencies...
    cd offline-ai-frontend
    npm install >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ Warning: Some Node.js dependencies may not have installed correctly
        echo Continuing anyway...
    )
    cd ..
)

echo ✅ Dependencies installed
echo.

:: Check GitHub configuration
echo 🔍 Checking GitHub configuration...
if exist "backend-ai\keys.txt" (
    findstr /C:"GITHUB_TOKEN=" backend-ai\keys.txt | findstr /V "your_github_token_here" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ Warning: GitHub token not configured in keys.txt
        echo Code will be saved locally but not uploaded to GitHub
        echo To enable GitHub upload, edit backend-ai\keys.txt
    ) else (
        echo ✅ GitHub configuration found
    )
) else (
    echo ⚠️ Warning: keys.txt not found
    echo GitHub auto-upload will not work
)

echo.
echo ============================================================
echo 🚀 Starting Services...
echo ============================================================
echo.

:: Simple port check - just warn if ports are in use
echo 🔍 Checking if services are already running...

:: Check port 8000 (Main Backend)
netstat -an 2>nul | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8000 is already in use - Main Backend may already be running
) else (
    echo ✅ Port 8000 is available
)

:: Check port 8001 (Online Agent Service)
netstat -an 2>nul | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8001 is already in use - Online Agent Service may already be running
) else (
    echo ✅ Port 8001 is available
)

:: Check port 5173 (Frontend)
netstat -an 2>nul | findstr ":5173" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 5173 is already in use - Frontend may already be running
) else (
    echo ✅ Port 5173 is available
)

echo.
echo ============================================================
echo 🚀 Starting Services...
echo ============================================================
echo.

:: Start services in separate windows
echo 📡 Starting Main Backend (Port 8000)...
start "Main Backend - Port 8000" cmd /k "cd /d %PROJECT_ROOT%\backend-ai && call venv\Scripts\activate.bat && set OPENAI_API_KEY=%OPENAI_API_KEY% && set MISTRAL_API_KEY=%MISTRAL_API_KEY% && set GEMINI_API_KEY=%GEMINI_API_KEY% && set GITHUB_TOKEN=%GITHUB_TOKEN% && set GITHUB_USERNAME=%GITHUB_USERNAME% && python main.py"

:: Wait a moment for backend to start
ping 127.0.0.1 -n 4 >nul

echo 🤖 Starting Online Agent Service (Port 8001)...
start "Online Agent Service - Port 8001" cmd /k "cd /d %PROJECT_ROOT%\backend-ai && call venv\Scripts\activate.bat && set OPENAI_API_KEY=%OPENAI_API_KEY% && set MISTRAL_API_KEY=%MISTRAL_API_KEY% && set GEMINI_API_KEY=%GEMINI_API_KEY% && set GITHUB_TOKEN=%GITHUB_TOKEN% && set GITHUB_USERNAME=%GITHUB_USERNAME% && python online_agent_service.py"

:: Wait a moment for online service to start
ping 127.0.0.1 -n 4 >nul

echo 🌐 Starting Frontend (Port 5173)...
start "Frontend - Port 5173" cmd /k "cd /d %PROJECT_ROOT%\offline-ai-frontend && npm run dev"

echo.
echo ============================================================
echo ✅ All Services Started!
echo ============================================================
echo.
echo 📡 Main Backend:     http://localhost:8000
echo 🤖 Online Agents:    http://localhost:8001
echo 🌐 Frontend:         http://localhost:5173
echo.
echo 📋 Service Status:
echo    - Main Backend:    Starting... (check window for status)
echo    - Online Agents:   Starting... (check window for status)
echo    - Frontend:        Starting... (check window for status)
echo.
echo 💡 Tips:
echo    - Each service runs in its own window
echo    - Check the windows for any error messages
echo    - Frontend may take a moment to compile
echo    - GitHub auto-upload requires valid credentials in keys.txt
echo.
echo 🔧 To stop all services:
echo    - Close all the opened command windows
echo    - Or press Ctrl+C in each window
echo.
echo Press any key to open the frontend in your browser...
pause >nul

:: Try to open frontend in browser
start http://localhost:5173

echo.
echo 🎉 Setup complete! Check the service windows for any issues.
echo.
pause