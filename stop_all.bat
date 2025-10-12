@echo off
echo ============================================================
echo 🛑 Stopping All Services
echo ============================================================
echo.

echo 🔍 Checking for running services...

:: Check and stop services on ports 8000, 8001, 3000
set services_stopped=0

:: Port 8000 (Main Backend)
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo 📡 Stopping Main Backend (Port 8000)...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo ✅ Main Backend stopped
            set /a services_stopped+=1
        )
    )
) else (
    echo ℹ️ Main Backend (Port 8000) not running
)

:: Port 8001 (Online Agent Service)
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo 🤖 Stopping Online Agent Service (Port 8001)...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001"') do (
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo ✅ Online Agent Service stopped
            set /a services_stopped+=1
        )
    )
) else (
    echo ℹ️ Online Agent Service (Port 8001) not running
)

:: Port 3000 (Frontend)
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo 🌐 Stopping Frontend (Port 3000)...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000"') do (
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo ✅ Frontend stopped
            set /a services_stopped+=1
        )
    )
) else (
    echo ℹ️ Frontend (Port 3000) not running
)

echo.
echo ============================================================
if %services_stopped% gtr 0 (
    echo ✅ Stopped %services_stopped% service(s)
) else (
    echo ℹ️ No services were running
)
echo ============================================================
echo.

echo 💡 All services have been stopped.
echo You can now run start_all.bat to start them again.
echo.
pause
