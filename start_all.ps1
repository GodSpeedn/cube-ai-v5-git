# PowerShell script to start all services
# Run with: powershell -ExecutionPolicy Bypass -File start_all.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting All Services - Backend, Online Agent, Frontend" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set the project root directory
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

# Check if we're in the right directory
if (-not (Test-Path "backend-ai")) {
    Write-Host "❌ Error: backend-ai folder not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "offline-ai-frontend")) {
    Write-Host "❌ Error: offline-ai-frontend folder not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📁 Project root: $PROJECT_ROOT" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "backend-ai\venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    Set-Location "backend-ai"
    python -m venv venv
    Set-Location ".."
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating Python virtual environment..." -ForegroundColor Yellow
$activateScript = "backend-ai\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "⚠️ Warning: Could not activate virtual environment" -ForegroundColor Yellow
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "backend-ai"
try {
    pip install -r requirements.txt | Out-Null
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: Some Python dependencies may not have installed correctly" -ForegroundColor Yellow
}
Set-Location ".."

# Check if Node modules exist
if (-not (Test-Path "offline-ai-frontend\node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    Set-Location "offline-ai-frontend"
    try {
        npm install | Out-Null
        Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Warning: Some Node.js dependencies may not have installed correctly" -ForegroundColor Yellow
    }
    Set-Location ".."
}

Write-Host ""

# Check GitHub configuration
Write-Host "🔍 Checking GitHub configuration..." -ForegroundColor Yellow
if (Test-Path "backend-ai\keys.txt") {
    $keysContent = Get-Content "backend-ai\keys.txt" -Raw
    if ($keysContent -match "GITHUB_TOKEN=(?!your_github_token_here).*") {
        Write-Host "✅ GitHub configuration found" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Warning: GitHub token not configured in keys.txt" -ForegroundColor Yellow
        Write-Host "Code will be saved locally but not uploaded to GitHub" -ForegroundColor Yellow
        Write-Host "To enable GitHub upload, edit backend-ai\keys.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Warning: keys.txt not found" -ForegroundColor Yellow
    Write-Host "GitHub auto-upload will not work" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Services..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start services in separate windows
Write-Host "📡 Starting Main Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PROJECT_ROOT\backend-ai'; .\venv\Scripts\Activate.ps1; python main.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host "🤖 Starting Online Agent Service (Port 8001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PROJECT_ROOT\backend-ai'; .\venv\Scripts\Activate.ps1; python online_agent_service.py" -WindowStyle Normal

# Wait a moment for online service to start
Start-Sleep -Seconds 3

Write-Host "🌐 Starting Frontend (Port 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PROJECT_ROOT\offline-ai-frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "✅ All Services Started!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Main Backend:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "🤖 Online Agents:    http://localhost:8001" -ForegroundColor Cyan
Write-Host "🌐 Frontend:         http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Service Status:" -ForegroundColor Yellow
Write-Host "   - Main Backend:    Starting... (check window for status)" -ForegroundColor White
Write-Host "   - Online Agents:   Starting... (check window for status)" -ForegroundColor White
Write-Host "   - Frontend:        Starting... (check window for status)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Each service runs in its own window" -ForegroundColor White
Write-Host "   - Check the windows for any error messages" -ForegroundColor White
Write-Host "   - Frontend may take a moment to compile" -ForegroundColor White
Write-Host "   - GitHub auto-upload requires valid credentials in keys.txt" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To stop all services:" -ForegroundColor Yellow
Write-Host "   - Close all the opened PowerShell windows" -ForegroundColor White
Write-Host "   - Or press Ctrl+C in each window" -ForegroundColor White
Write-Host ""

# Try to open frontend in browser
Write-Host "🌐 Opening frontend in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    Start-Process "http://localhost:3000"
    Write-Host "✅ Frontend opened in browser" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not open browser automatically" -ForegroundColor Yellow
    Write-Host "Please open http://localhost:3000 manually" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup complete! Check the service windows for any issues." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
