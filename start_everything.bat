@echo off
setlocal enabledelayedexpansion
title AI Services - All in One

echo ============================================================
echo Starting All Services - Backend, Online Agent, Frontend
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

:: Check if we're in the right directory
if not exist "backend-ai" (
    echo [ERROR] backend-ai folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "offline-ai-frontend" (
    echo [ERROR] offline-ai-frontend folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo [OK] Project structure verified
echo.

:: Load environment variables from keys.txt
echo [INFO] Loading API keys and GitHub credentials from keys.txt...
if exist "backend-ai\keys.txt" (
    for /f "usebackq tokens=1,* delims==" %%a in ("backend-ai\keys.txt") do (
        set "line=%%a"
        :: Skip comments and empty lines
        echo !line! | findstr /r "^#" >nul
        if errorlevel 1 (
            if not "%%a"=="" (
                if not "%%b"=="" (
                    set "%%a=%%b"
                    echo [OK] Loaded: %%a
                )
            )
        )
    )
    echo [OK] Environment variables loaded from keys.txt
) else (
    echo [WARN] keys.txt not found - services will use environment variables only
)
echo.

:: Check for port conflicts
echo [INFO] Checking for port conflicts...
set PORT_CONFLICT=0

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 8000 is already in use
    set PORT_CONFLICT=1
)

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 8001 is already in use
    set PORT_CONFLICT=1
)

netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 3000 is already in use
    set PORT_CONFLICT=1
)

if %PORT_CONFLICT%==1 (
    echo.
    echo [WARN] Port conflicts detected!
    echo.
    choice /C YN /M "Kill existing processes and continue"
    if errorlevel 2 (
        echo [INFO] Startup cancelled
        pause
        exit /b 0
    )
    echo [INFO] Stopping existing services...
    taskkill /F /IM python.exe /T >nul 2>&1
    taskkill /F /IM node.exe /T >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo [OK] Existing processes stopped
    echo.
)

:: Start services in separate windows
echo [INFO] Starting services...
echo.

:: Start Main Backend (Port 8000)
echo [1/3] Starting Main Backend Service (Port 8000)...
start "Main Backend (8000)" cmd /k "cd /d "%PROJECT_ROOT%backend-ai" && set OPENAI_API_KEY=%OPENAI_API_KEY% && set MISTRAL_API_KEY=%MISTRAL_API_KEY% && set GEMINI_API_KEY=%GEMINI_API_KEY% && set GITHUB_TOKEN=%GITHUB_TOKEN% && set GITHUB_USERNAME=%GITHUB_USERNAME% && python main.py"
timeout /t 3 /nobreak >nul

:: Start Online Agent Service (Port 8001)
echo [2/3] Starting Online Agent Service (Port 8001)...
start "Online Agent Service (8001)" cmd /k "cd /d "%PROJECT_ROOT%backend-ai" && set OPENAI_API_KEY=%OPENAI_API_KEY% && set MISTRAL_API_KEY=%MISTRAL_API_KEY% && set GEMINI_API_KEY=%GEMINI_API_KEY% && set GITHUB_TOKEN=%GITHUB_TOKEN% && set GITHUB_USERNAME=%GITHUB_USERNAME% && python online_agent_service.py"
timeout /t 3 /nobreak >nul

:: Start Frontend (Port 3000)
echo [3/3] Starting Frontend (Port 3000)...
start "Frontend (3000)" cmd /k "cd /d "%PROJECT_ROOT%offline-ai-frontend" && npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo [SUCCESS] All services started!
echo ============================================================
echo.
echo Services running:
echo   - Main Backend:        http://localhost:8000
echo   - Online Agent Service: http://localhost:8001
echo   - Frontend:            http://localhost:3000
echo.
echo ============================================================
echo.
echo [INFO] All services are running in separate windows.
echo [INFO] Check each window for service status and logs.
echo.
echo To stop all services, press any key in this window...
pause >nul

:: Stop all services
echo.
echo [INFO] Stopping all services...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo [OK] All services stopped.
echo.
pause

