@echo off
echo ============================================================
echo 🔍 GitHub Upload Debug Tool
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo 📁 Project root: %PROJECT_ROOT%
echo.

:: Load environment variables from keys.txt
echo 🔑 Loading environment variables from keys.txt...
if exist "backend-ai\keys.txt" (
    for /f "usebackq tokens=1,2 delims==" %%a in ("backend-ai\keys.txt") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    echo ✅ Environment variables loaded
) else (
    echo ❌ keys.txt not found
    pause
    exit /b 1
)

echo.
echo 📋 Current GitHub Configuration:
echo    GITHUB_TOKEN: %GITHUB_TOKEN:~0,20%...
echo    GITHUB_USERNAME: %GITHUB_USERNAME%
echo.

:: Test 1: Check if GitHub service can be imported
echo 🔍 Test 1: Checking GitHub service import...
cd backend-ai
python test_github_import.py
if errorlevel 1 (
    echo ❌ GitHub import test failed
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo 🔍 Test 2: Checking if services are running...
echo.

:: Check if services are running
netstat -an | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Online Agent Service (Port 8001) is running
) else (
    echo ❌ Online Agent Service (Port 8001) is NOT running
    echo 💡 Start the service first with start_all_safe.bat
    pause
    exit /b 1
)

echo.
echo 🔍 Test 3: Testing GitHub API connection directly...
echo.

python -c "
import os
import requests

token = os.environ.get('GITHUB_TOKEN')
username = os.environ.get('GITHUB_USERNAME')

if not token or not username:
    print('❌ GitHub credentials not found in environment')
    exit(1)

if token == 'your_github_token_here':
    print('❌ GitHub token is still set to placeholder value')
    exit(1)

print(f'✅ Testing GitHub API with user: {username}')

try:
    headers = {'Authorization': f'token {token}'}
    response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f'✅ GitHub API connection successful!')
        print(f'   User: {user_data.get(\"login\", \"Unknown\")}')
        print(f'   Name: {user_data.get(\"name\", \"Unknown\")}')
        print(f'   Public repos: {user_data.get(\"public_repos\", 0)}')
        
        # Test repository creation permission
        print('🔍 Testing repository creation permission...')
        test_repo_data = {
            'name': 'test-repo-debug-check',
            'description': 'Test repository for debug check',
            'private': True,
            'auto_init': False
        }
        
        create_response = requests.post('https://api.github.com/user/repos', 
                                      headers=headers, 
                                      json=test_repo_data, 
                                      timeout=10)
        
        if create_response.status_code == 201:
            print('✅ Repository creation permission confirmed!')
            # Delete the test repository
            delete_response = requests.delete(f'https://api.github.com/repos/{username}/test-repo-debug-check', 
                                            headers=headers, 
                                            timeout=10)
            if delete_response.status_code == 204:
                print('✅ Test repository cleaned up')
            else:
                print('⚠️ Could not delete test repository (you may need to delete it manually)')
        else:
            print(f'❌ Repository creation failed: {create_response.status_code}')
            print(f'   Response: {create_response.text[:200]}')
            
    else:
        print(f'❌ GitHub API connection failed: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
except requests.exceptions.RequestException as e:
    print(f'❌ Network error: {e}')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo.
echo 🔍 Test 4: Checking recent project files...
echo.

:: Check if there are any recent projects
if exist "backend-ai\generated\projects" (
    echo ✅ Generated projects folder exists
    echo.
    echo 📁 Recent projects:
    for /f "delims=" %%i in ('dir "backend-ai\generated\projects" /b /od /t:w') do (
        echo   - %%i
    )
) else (
    echo ❌ No generated projects folder found
    echo 💡 Run a workflow that generates code first
)

echo.
echo 🔍 Test 5: Checking file_manager logs...
echo.

:: Check if we can import file_manager
cd backend-ai
python -c "
import sys
from pathlib import Path

# Add git-integration to path
git_integration_path = Path('..') / 'git-integration'
if git_integration_path.exists():
    sys.path.insert(0, str(git_integration_path))

try:
    from file_manager import file_manager
    print('✅ File manager imported successfully')
    print(f'   Base directory: {file_manager.base_dir}')
    print(f'   Git available: {hasattr(file_manager, \"GIT_AVAILABLE\")}')
except Exception as e:
    print(f'❌ Failed to import file manager: {e}')
"
cd ..

echo.
echo ============================================================
echo 🎯 Debug Complete
echo ============================================================
echo.
echo 💡 Next steps:
echo    1. If all tests passed, try generating code again
echo    2. Check the service logs for detailed error messages
echo    3. Look for '🚀 STARTING GITHUB AUTO-UPLOAD' in logs
echo    4. If upload fails, check the specific error message
echo.
pause
