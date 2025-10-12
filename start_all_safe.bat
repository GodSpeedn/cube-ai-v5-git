@echo off
setlocal enabledelayedexpansion
echo ============================================================
echo 🚀 Starting All Services - Safe Mode
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
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Virtual environment created
)

:: Activate virtual environment
echo 🔧 Activating Python virtual environment...
call backend-ai\venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

:: Load environment variables from keys.txt (simplified)
echo 🔑 Loading API keys and GitHub configuration...
if exist "backend-ai\keys.txt" (
    echo ✅ Found keys.txt file
) else (
    echo ⚠️ Warning: keys.txt not found - GitHub auto-upload will not work
)

:: Install Python dependencies
echo 📦 Installing Python dependencies...
cd backend-ai
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️ Warning: Some Python dependencies may not have installed correctly
    echo Continuing anyway...
)
cd ..

:: Check if Node modules exist
if not exist "offline-ai-frontend\node_modules" (
    echo 📦 Installing Node.js dependencies...
    cd offline-ai-frontend
    npm install
    if errorlevel 1 (
        echo ⚠️ Warning: Some Node.js dependencies may not have installed correctly
        echo Continuing anyway...
    )
    cd ..
)

echo ✅ Dependencies installed
echo.

:: Simple port check (no complex logic)
echo 🔍 Checking ports...
set port_8000_free=1
set port_8001_free=1
set port_3000_free=1

netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 set port_8000_free=0

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 set port_8001_free=0

netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 set port_3000_free=0

if %port_8000_free%==0 echo ⚠️ Port 8000 is in use
if %port_8001_free%==0 echo ⚠️ Port 8001 is in use
if %port_3000_free%==0 echo ⚠️ Port 3000 is in use

if %port_8000_free%==1 if %port_8001_free%==1 if %port_3000_free%==1 (
    echo ✅ All ports are available
) else (
    echo.
    echo ⚠️ Some ports are in use. You can:
    echo    1. Continue anyway (may show errors)
    echo    2. Exit and stop existing services manually
    echo.
    set /p choice="Choose (1 or 2): "
    if "!choice!"=="2" (
        echo.
        echo 💡 To stop existing services:
        echo    - Close any open command windows running services
        echo    - Or run: taskkill /f /im python.exe
        echo    - Or run: taskkill /f /im node.exe
        pause
        exit /b 0
    )
)

echo.
echo ============================================================
echo 🚀 Starting Services...
echo ============================================================
echo.

:: Start services with simple error handling
echo 📡 Starting Main Backend (Port 8000)...
start "Main Backend - Port 8000" cmd /k "cd /d %PROJECT_ROOT%\backend-ai && call venv\Scripts\activate.bat && python main.py"
if errorlevel 1 (
    echo ❌ Failed to start Main Backend
) else (
    echo ✅ Main Backend started
)

:: Wait a moment
timeout /t 3 /nobreak >nul

echo 🤖 Starting Online Agent Service (Port 8001)...
start "Online Agent Service - Port 8001" cmd /k "cd /d %PROJECT_ROOT%\backend-ai && call venv\Scripts\activate.bat && python online_agent_service.py"
if errorlevel 1 (
    echo ❌ Failed to start Online Agent Service
) else (
    echo ✅ Online Agent Service started
)

:: Wait a moment
timeout /t 3 /nobreak >nul

echo 🌐 Starting Frontend (Port 3000)...
start "Frontend - Port 3000" cmd /k "cd /d %PROJECT_ROOT%\offline-ai-frontend && npm run dev"
if errorlevel 1 (
    echo ❌ Failed to start Frontend
) else (
    echo ✅ Frontend started
)

echo.
echo ============================================================
echo ✅ Services Started!
echo ============================================================
echo.
echo 📡 Main Backend:     http://localhost:8000
echo 🤖 Online Agents:    http://localhost:8001
echo 🌐 Frontend:         http://localhost:3000
echo.
echo 💡 Check the service windows for any error messages
echo.
echo Press any key to open the frontend in your browser...
pause >nul

:: Try to open frontend in browser
start http://localhost:3000

echo.
echo 🎉 Setup complete! Check the service windows for any issues.
echo.
pause
