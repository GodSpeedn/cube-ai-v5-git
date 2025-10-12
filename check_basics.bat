@echo off
echo ============================================================
echo 🔍 Basic System Check
echo ============================================================
echo.

:: Check current directory
echo 📁 Current directory: %CD%
echo.

:: Check if we're in the right place
if exist "backend-ai" (
    echo ✅ backend-ai folder found
) else (
    echo ❌ backend-ai folder NOT found
    echo Please run this from the project root directory
    echo.
    pause
    exit /b 1
)

if exist "git-integration" (
    echo ✅ git-integration folder found
) else (
    echo ❌ git-integration folder NOT found
    echo Please run this from the project root directory
    echo.
    pause
    exit /b 1
)

:: Check Python
echo.
echo 🔍 Checking Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python is working
)

:: Check Node.js
echo.
echo 🔍 Checking Node.js...
node --version
if errorlevel 1 (
    echo ❌ Node.js not found
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Node.js is working
)

:: Check keys.txt
echo.
echo 🔍 Checking keys.txt...
if exist "backend-ai\keys.txt" (
    echo ✅ keys.txt exists
    echo.
    echo First few lines of keys.txt:
    type "backend-ai\keys.txt" | more
) else (
    echo ❌ keys.txt NOT found
    echo.
    pause
    exit /b 1
)

:: Check github_service.py
echo.
echo 🔍 Checking github_service.py...
if exist "git-integration\github_service.py" (
    echo ✅ github_service.py exists
) else (
    echo ❌ github_service.py NOT found
    echo.
    pause
    exit /b 1
)

:: Check if services are running
echo.
echo 🔍 Checking running services...
echo Port 8000 (Main Backend):
netstat -an | findstr ":8000"
if errorlevel 1 (
    echo   Not running
) else (
    echo   Running
)

echo.
echo Port 8001 (Online Agent Service):
netstat -an | findstr ":8001"
if errorlevel 1 (
    echo   Not running
) else (
    echo   Running
)

echo.
echo Port 3000 (Frontend):
netstat -an | findstr ":3000"
if errorlevel 1 (
    echo   Not running
) else (
    echo   Running
)

echo.
echo ============================================================
echo ✅ Basic Check Complete
echo ============================================================
echo.
echo If all items show ✅, your system is ready.
echo If any show ❌, fix those issues first.
echo.
pause
