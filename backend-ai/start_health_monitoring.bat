@echo off
echo Starting Health Monitoring System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "health_monitoring" (
    echo Error: health_monitoring directory not found
    echo Please run this script from the backend-ai directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Start the health monitoring system
echo.
echo Starting Health Monitoring API on port 8001...
echo Health monitoring endpoints will be available at:
echo   - http://localhost:8001/health
echo   - http://localhost:8001/system-status
echo   - http://localhost:8001/api-keys
echo   - http://localhost:8001/models
echo.

python start_with_health_monitoring.py

pause
