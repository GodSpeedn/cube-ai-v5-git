@echo off
echo ============================================================
echo 🔧 Quick Port Conflict Resolver
echo ============================================================
echo.

echo 🔍 Detecting port conflicts...

set conflicts_found=0

:: Check each port and count conflicts
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 set /a conflicts_found+=1

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 set /a conflicts_found+=1

netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 set /a conflicts_found+=1

if %conflicts_found%==0 (
    echo ✅ No port conflicts detected
    echo All ports (8000, 8001, 3000) are available
    echo.
    pause
    exit /b 0
)

echo ⚠️ Found %conflicts_found% port conflict(s)
echo.

:: Show which ports are in use
echo 📋 Ports in use:
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 echo   ⚠️ Port 8000 (Main Backend)

netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 echo   ⚠️ Port 8001 (Online Agent Service)

netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 echo   ⚠️ Port 3000 (Frontend)

echo.
echo 🔧 Choose resolution method:
echo    1. Kill processes on conflicting ports (Recommended)
echo    2. Force kill all Python/Node processes
echo    3. Show detailed information and exit
echo    4. Exit without resolving
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :kill_conflicting_ports
if "%choice%"=="2" goto :force_kill_all
if "%choice%"=="3" goto :show_detailed_info
if "%choice%"=="4" goto :exit
echo ❌ Invalid choice
goto :resolve_port_conflicts

:kill_conflicting_ports
echo.
echo 🛑 Killing processes on conflicting ports...

:: Kill port 8000
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo 📡 Stopping processes on port 8000...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
)

:: Kill port 8001
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo 🤖 Stopping processes on port 8001...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
)

:: Kill port 3000
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo 🌐 Stopping processes on port 3000...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
)

echo.
echo ✅ Port conflicts resolved
echo ⏳ Waiting 3 seconds for ports to be released...
timeout /t 3 /nobreak >nul

:: Verify resolution
echo 🔍 Verifying ports are now available...
set resolved=0

netstat -an | findstr ":8000" >nul 2>&1
if errorlevel 1 set /a resolved+=1

netstat -an | findstr ":8001" >nul 2>&1
if errorlevel 1 set /a resolved+=1

netstat -an | findstr ":3000" >nul 2>&1
if errorlevel 1 set /a resolved+=1

echo ✅ %resolved% out of 3 ports are now available
echo.
echo 💡 You can now run start_all.bat to start the services
pause
exit /b 0

:force_kill_all
echo.
echo ⚠️ WARNING: This will kill ALL Python and Node.js processes!
echo.
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    goto :resolve_port_conflicts
)

echo.
echo 🛑 Force killing all Python processes...
taskkill /f /im python.exe >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python processes stopped
) else (
    echo ℹ️ No Python processes found
)

echo 🛑 Force killing all Node.js processes...
taskkill /f /im node.exe >nul 2>&1
if not errorlevel 1 (
    echo ✅ Node.js processes stopped
) else (
    echo ℹ️ No Node.js processes found
)

echo.
echo ✅ All processes stopped
echo ⏳ Waiting 3 seconds...
timeout /t 3 /nobreak >nul
echo 💡 You can now run start_all.bat to start the services
pause
exit /b 0

:show_detailed_info
echo.
echo 📋 Detailed Port Information:
echo.

echo Port 8000 (Main Backend):
netstat -aon | findstr ":8000"
echo.

echo Port 8001 (Online Agent Service):
netstat -aon | findstr ":8001"
echo.

echo Port 3000 (Frontend):
netstat -aon | findstr ":3000"
echo.

echo All Python processes:
tasklist | findstr python.exe
echo.

echo All Node processes:
tasklist | findstr node.exe
echo.

pause
exit /b 0

:exit
echo.
echo 👋 Exiting without resolving conflicts
echo You may need to manually stop the conflicting processes
exit /b 0
