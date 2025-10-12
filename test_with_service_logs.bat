@echo off
echo [INFO] Starting service with logging...

cd "backend-ai"

:: Kill existing python processes
taskkill /F /IM python.exe >nul 2>&1

:: Start service and save logs
echo [INFO] Starting online agent service...
start /B python online_agent_service.py > service_log.txt 2>&1

:: Wait for service to start
timeout /t 5 /nobreak >nul

:: Run test
echo [INFO] Running test workflow...
python test_workflow_detailed.py

:: Show service logs
echo.
echo [INFO] Service logs:
echo ============================================================
type service_log.txt
echo ============================================================

:: Kill service
taskkill /F /IM python.exe >nul 2>&1

pause

