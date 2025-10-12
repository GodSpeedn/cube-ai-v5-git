@echo off
echo Starting Complete AI Coding Assistant System...
echo.

echo ========================================
echo Starting Main Service (Port 8000)...
echo ========================================
start "Main Service" cmd /k "cd backend-ai && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Waiting 5 seconds for main service to start...
timeout /t 5 /nobreak >nul

echo ========================================
echo Starting Online Service (Port 8001)...
echo ========================================
start "Online Service" cmd /k "cd backend-ai && python online_agent_service.py"

echo.
echo Waiting 3 seconds for online service to start...
timeout /t 3 /nobreak >nul

echo ========================================
echo Starting Frontend (Port 5173)...
echo ========================================
start "Frontend" cmd /k "cd offline-ai-frontend && npm run dev"

echo.
echo ========================================
echo All Services Starting...
echo ========================================
echo Main Service:    http://localhost:8000
echo Online Service:  http://localhost:8001  
echo Frontend:        http://localhost:5173
echo.
echo Models will be available once both services are running!
echo.
pause


