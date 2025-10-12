@echo off
echo ============================================================
echo 🔧 Port Management Tool
echo ============================================================
echo.

:main_menu
echo 🔧 Choose an option:
echo    1. Check port status
echo    2. Stop all services (kill processes on ports 8000, 8001, 3000)
echo    3. Stop specific port
echo    4. Show detailed port information
echo    5. Force kill all Python/Node processes
echo    6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto :check_ports
if "%choice%"=="2" goto :stop_all_services
if "%choice%"=="3" goto :stop_specific_port
if "%choice%"=="4" goto :show_detailed_info
if "%choice%"=="5" goto :force_kill_all
if "%choice%"=="6" goto :exit
echo ❌ Invalid choice. Please try again.
echo.
goto :main_menu

:check_ports
echo.
echo 🔍 Checking port status...
echo.

:: Check port 8000 (Main Backend)
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8000 (Main Backend): IN USE
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
        echo   Process ID: %%a
    )
) else (
    echo ✅ Port 8000 (Main Backend): AVAILABLE
)

:: Check port 8001 (Online Agent Service)
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 8001 (Online Agent Service): IN USE
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001"') do (
        echo   Process ID: %%a
    )
) else (
    echo ✅ Port 8001 (Online Agent Service): AVAILABLE
)

:: Check port 3000 (Frontend)
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ Port 3000 (Frontend): IN USE
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000"') do (
        echo   Process ID: %%a
    )
) else (
    echo ✅ Port 3000 (Frontend): AVAILABLE
)

echo.
pause
goto :main_menu

:stop_all_services
echo.
echo 🛑 Stopping all services...
echo.

:: Stop port 8000
echo 📡 Stopping processes on port 8000...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
) else (
    echo   ℹ️ No processes on port 8000
)

:: Stop port 8001
echo 🤖 Stopping processes on port 8001...
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
) else (
    echo   ℹ️ No processes on port 8001
)

:: Stop port 3000
echo 🌐 Stopping processes on port 3000...
netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
) else (
    echo   ℹ️ No processes on port 3000
)

echo.
echo ✅ All services stopped
echo ⏳ Waiting 2 seconds for ports to be released...
timeout /t 2 /nobreak >nul
pause
goto :main_menu

:stop_specific_port
echo.
echo 🔧 Stop specific port:
echo    1. Port 8000 (Main Backend)
echo    2. Port 8001 (Online Agent Service)
echo    3. Port 3000 (Frontend)
echo    4. Back to main menu
echo.
set /p port_choice="Enter your choice (1-4): "

if "%port_choice%"=="1" set target_port=8000
if "%port_choice%"=="2" set target_port=8001
if "%port_choice%"=="3" set target_port=3000
if "%port_choice%"=="4" goto :main_menu

if not defined target_port (
    echo ❌ Invalid choice
    goto :stop_specific_port
)

echo.
echo 🛑 Stopping processes on port %target_port%...
netstat -an | findstr ":%target_port%" >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%target_port%"') do (
        echo   Killing process %%a...
        taskkill /f /pid %%a >nul 2>&1
        if not errorlevel 1 (
            echo   ✅ Process %%a stopped
        ) else (
            echo   ⚠️ Could not stop process %%a
        )
    )
) else (
    echo   ℹ️ No processes on port %target_port%
)

echo.
pause
goto :main_menu

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
goto :main_menu

:force_kill_all
echo.
echo ⚠️ WARNING: This will kill ALL Python and Node.js processes!
echo This may affect other applications using Python or Node.js.
echo.
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    goto :main_menu
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
echo ✅ All Python and Node.js processes stopped
echo ⏳ Waiting 3 seconds for ports to be released...
timeout /t 3 /nobreak >nul
pause
goto :main_menu

:exit
echo.
echo 👋 Goodbye!
exit /b 0
