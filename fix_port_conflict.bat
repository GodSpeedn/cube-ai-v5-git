@echo off
echo ============================================================
echo 🔧 Fixing Port Conflict (Port 8001)
echo ============================================================
echo.

echo 🔍 Checking for processes using port 8001...

:: Find and kill processes on port 8001
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8001 is in use. Stopping conflicting process...
    
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001"') do (
        echo 🛑 Stopping process ID: %%a
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo ✅ Process stopped successfully
        ) else (
            echo ❌ Failed to stop process %%a
        )
    )
    
    echo.
    echo ✅ Port 8001 should now be available
    echo You can now run start_all.bat again
) else (
    echo ✅ Port 8001 is already available
    echo No action needed
)

echo.
echo 💡 If you continue to have issues:
echo    1. Run stop_all.bat to stop all services
echo    2. Then run start_all.bat to restart everything
echo.
pause
