@echo off
echo ============================================================
echo 🔍 System Diagnostic Tool
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo 📁 Project root: %PROJECT_ROOT%
echo.

:: Check basic requirements
echo 🔍 Checking basic requirements...

:: Check Python
echo.
echo 📋 Python Check:
python --version 2>&1
if errorlevel 1 (
    echo ❌ Python not found or not in PATH
) else (
    echo ✅ Python is available
)

:: Check Node.js
echo.
echo 📋 Node.js Check:
node --version 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found or not in PATH
) else (
    echo ✅ Node.js is available
)

:: Check project structure
echo.
echo 📋 Project Structure Check:
if exist "backend-ai" (
    echo ✅ backend-ai folder exists
) else (
    echo ❌ backend-ai folder missing
)

if exist "offline-ai-frontend" (
    echo ✅ offline-ai-frontend folder exists
) else (
    echo ❌ offline-ai-frontend folder missing
)

if exist "backend-ai\requirements.txt" (
    echo ✅ requirements.txt exists
) else (
    echo ❌ requirements.txt missing
)

if exist "offline-ai-frontend\package.json" (
    echo ✅ package.json exists
) else (
    echo ❌ package.json missing
)

:: Check virtual environment
echo.
echo 📋 Virtual Environment Check:
if exist "backend-ai\venv" (
    echo ✅ Virtual environment exists
    if exist "backend-ai\venv\Scripts\activate.bat" (
        echo ✅ Virtual environment activation script exists
    ) else (
        echo ❌ Virtual environment activation script missing
    )
) else (
    echo ❌ Virtual environment not found
)

:: Check Node modules
echo.
echo 📋 Node Modules Check:
if exist "offline-ai-frontend\node_modules" (
    echo ✅ Node modules exist
) else (
    echo ❌ Node modules not found
)

:: Check keys.txt
echo.
echo 📋 Configuration Check:
if exist "backend-ai\keys.txt" (
    echo ✅ keys.txt exists
    echo 📄 Keys file content:
    type "backend-ai\keys.txt"
) else (
    echo ❌ keys.txt missing
)

:: Check port status
echo.
echo 📋 Port Status Check:
echo Port 8000 (Main Backend):
netstat -an | findstr ":8000"
if errorlevel 1 (
    echo ✅ Port 8000 is free
) else (
    echo ⚠️ Port 8000 is in use
)

echo.
echo Port 8001 (Online Agent Service):
netstat -an | findstr ":8001"
if errorlevel 1 (
    echo ✅ Port 8001 is free
) else (
    echo ⚠️ Port 8001 is in use
)

echo.
echo Port 3000 (Frontend):
netstat -an | findstr ":3000"
if errorlevel 1 (
    echo ✅ Port 3000 is free
) else (
    echo ⚠️ Port 3000 is in use
)

:: Check running processes
echo.
echo 📋 Running Processes Check:
echo Python processes:
tasklist | findstr python.exe
if errorlevel 1 (
    echo ✅ No Python processes running
) else (
    echo ⚠️ Python processes are running
)

echo.
echo Node processes:
tasklist | findstr node.exe
if errorlevel 1 (
    echo ✅ No Node processes running
) else (
    echo ⚠️ Node processes are running
)

:: Check disk space
echo.
echo 📋 Disk Space Check:
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set free_space=%%a
echo Available disk space: %free_space% bytes

:: Check memory
echo.
echo 📋 Memory Check:
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:list | findstr "="

echo.
echo ============================================================
echo 🎯 Diagnostic Complete
echo ============================================================
echo.
echo 💡 Common issues and solutions:
echo.
echo ❌ Python not found:
echo    - Install Python from https://python.org/downloads/
echo    - Make sure to check "Add Python to PATH" during installation
echo.
echo ❌ Node.js not found:
echo    - Install Node.js from https://nodejs.org/downloads/
echo    - Choose LTS version
echo.
echo ⚠️ Ports in use:
echo    - Run: taskkill /f /im python.exe
echo    - Run: taskkill /f /im node.exe
echo    - Or restart your computer
echo.
echo ❌ Virtual environment issues:
echo    - Delete backend-ai\venv folder
echo    - Run the startup script again
echo.
echo ❌ Node modules issues:
echo    - Delete offline-ai-frontend\node_modules folder
echo    - Run: npm install in offline-ai-frontend folder
echo.
pause
