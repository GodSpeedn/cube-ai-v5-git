@echo off
echo ============================================================
echo 🔧 Recovery and Restart Tool
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo 📁 Project root: %PROJECT_ROOT%
echo.

echo 🛑 Step 1: Stopping all existing services...
echo.

:: Kill all Python processes
echo 📡 Stopping Python processes...
taskkill /f /im python.exe >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python processes stopped
) else (
    echo ℹ️ No Python processes found
)

:: Kill all Node processes
echo 🌐 Stopping Node.js processes...
taskkill /f /im node.exe >nul 2>&1
if not errorlevel 1 (
    echo ✅ Node.js processes stopped
) else (
    echo ℹ️ No Node.js processes found
)

echo.
echo ⏳ Waiting 5 seconds for processes to fully stop...
timeout /t 5 /nobreak >nul

echo.
echo 🔍 Step 2: Checking port status...
echo.

:: Check ports
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8000 still in use
) else (
    echo ✅ Port 8000 is free
)

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8001 still in use
) else (
    echo ✅ Port 8001 is free
)

netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 3000 still in use
) else (
    echo ✅ Port 3000 is free
)

echo.
echo 🔧 Step 3: Cleaning up (optional)...
echo.
echo Do you want to clean up and recreate virtual environment?
echo This will delete backend-ai\venv and recreate it.
echo.
set /p cleanup="Clean up virtual environment? (y/N): "

if /i "%cleanup%"=="y" (
    echo.
    echo 🧹 Cleaning up virtual environment...
    if exist "backend-ai\venv" (
        rmdir /s /q "backend-ai\venv"
        echo ✅ Virtual environment deleted
    )
    
    echo 📦 Creating new virtual environment...
    cd backend-ai
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Virtual environment recreated
) else (
    echo ℹ️ Skipping virtual environment cleanup
)

echo.
echo 🔧 Step 4: Cleaning up Node modules (optional)...
echo.
echo Do you want to clean up and reinstall Node modules?
echo This will delete offline-ai-frontend\node_modules and reinstall.
echo.
set /p cleanup_node="Clean up Node modules? (y/N): "

if /i "%cleanup_node%"=="y" (
    echo.
    echo 🧹 Cleaning up Node modules...
    if exist "offline-ai-frontend\node_modules" (
        rmdir /s /q "offline-ai-frontend\node_modules"
        echo ✅ Node modules deleted
    )
    
    echo 📦 Installing Node modules...
    cd offline-ai-frontend
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install Node modules
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Node modules reinstalled
) else (
    echo ℹ️ Skipping Node modules cleanup
)

echo.
echo ============================================================
echo 🚀 Step 5: Starting Services (Safe Mode)
echo ============================================================
echo.

echo 📡 Starting Main Backend (Port 8000)...
start "Main Backend - Port 8000" cmd /k "cd /d %PROJECT_ROOT%\backend-ai && call venv\Scripts\activate.bat && python main.py"

echo ⏳ Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo 🤖 Starting Online Agent Service (Port 8001)...
start "Online Agent Service - Port 8001" cmd /k "cd /d %PROJECT_ROOT%\backend-ai && call venv\Scripts\activate.bat && python online_agent_service.py"

echo ⏳ Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo 🌐 Starting Frontend (Port 3000)...
start "Frontend - Port 3000" cmd /k "cd /d %PROJECT_ROOT%\offline-ai-frontend && npm run dev"

echo.
echo ============================================================
echo ✅ Recovery Complete!
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
echo 🎉 Recovery complete! Check the service windows for any issues.
echo.
pause
