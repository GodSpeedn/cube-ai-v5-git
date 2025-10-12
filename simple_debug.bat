@echo off
echo ============================================================
echo 🔍 Simple GitHub Debug Tool
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo 📁 Project root: %PROJECT_ROOT%
echo.

:: Check if we're in the right directory
if not exist "backend-ai" (
    echo ❌ Error: backend-ai folder not found
    echo Please run this script from the project root directory
    echo.
    pause
    exit /b 1
)

if not exist "git-integration" (
    echo ❌ Error: git-integration folder not found
    echo Please run this script from the project root directory
    echo.
    pause
    exit /b 1
)

echo ✅ Project structure looks good
echo.

:: Check keys.txt
echo 🔍 Checking keys.txt...
if exist "backend-ai\keys.txt" (
    echo ✅ keys.txt exists
    echo.
    echo 📄 Keys file content:
    type "backend-ai\keys.txt"
    echo.
) else (
    echo ❌ keys.txt not found
    echo.
    pause
    exit /b 1
)

:: Check git-integration files
echo 🔍 Checking git-integration files...
if exist "git-integration\github_service.py" (
    echo ✅ github_service.py exists
) else (
    echo ❌ github_service.py not found
    echo.
    pause
    exit /b 1
)

:: Check if services are running
echo.
echo 🔍 Checking if services are running...
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Online Agent Service (Port 8001) is running
) else (
    echo ❌ Online Agent Service (Port 8001) is NOT running
    echo 💡 Start the service first with start_all_safe.bat
    echo.
    pause
    exit /b 1
)

:: Test Python import
echo.
echo 🔍 Testing Python import...
cd backend-ai
python -c "print('✅ Python is working')"
if errorlevel 1 (
    echo ❌ Python test failed
    cd ..
    echo.
    pause
    exit /b 1
)

:: Test GitHub import
echo.
echo 🔍 Testing GitHub service import...
python -c "
import sys
from pathlib import Path

print('Python path:')
for p in sys.path:
    print(f'  - {p}')

# Add git-integration to path
git_integration_path = Path('..') / 'git-integration'
print(f'Git integration path: {git_integration_path}')
print(f'Git integration exists: {git_integration_path.exists()}')

if git_integration_path.exists():
    sys.path.insert(0, str(git_integration_path))
    print('✅ Added git-integration to path')
    
    try:
        from github_service import GitHubService
        print('✅ GitHubService imported successfully')
    except ImportError as e:
        print(f'❌ Import failed: {e}')
        print('Available files in git-integration:')
        for item in git_integration_path.iterdir():
            print(f'  - {item.name}')
    except Exception as e:
        print(f'❌ Other error: {e}')
else:
    print('❌ git-integration folder not found')
"

if errorlevel 1 (
    echo ❌ GitHub import test failed
    cd ..
    echo.
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================================
echo 🎯 Debug Complete
echo ============================================================
echo.
echo 💡 If all checks passed, the issue might be:
echo    1. Environment variables not loaded in the service
echo    2. GitHub token invalid or expired
echo    3. Network/firewall issues
echo.
echo Next steps:
echo    1. Check the service logs for error messages
echo    2. Try generating code and watch the logs
echo    3. Look for '🚀 STARTING GITHUB AUTO-UPLOAD' in logs
echo.
pause
