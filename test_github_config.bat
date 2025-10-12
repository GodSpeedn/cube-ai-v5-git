@echo off
echo ============================================================
echo 🔍 Testing GitHub Configuration
echo ============================================================
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

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
echo 📋 Current Configuration:
echo    GITHUB_TOKEN: %GITHUB_TOKEN:~0,20%...
echo    GITHUB_USERNAME: %GITHUB_USERNAME%
echo.

:: Test GitHub API connection
echo 🔍 Testing GitHub API connection...
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

print(f'✅ GitHub credentials found: {username}')
print('🔍 Testing GitHub API connection...')

try:
    headers = {'Authorization': f'token {token}'}
    response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f'✅ GitHub API connection successful!')
        print(f'   User: {user_data.get(\"login\", \"Unknown\")}')
        print(f'   Name: {user_data.get(\"name\", \"Unknown\")}')
        print(f'   Repositories: {user_data.get(\"public_repos\", 0)} public')
        
        # Test repository creation permission
        print('🔍 Testing repository creation permission...')
        test_repo_data = {
            'name': 'test-repo-permission-check',
            'description': 'Test repository to check permissions',
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
            repo_name = test_repo_data['name']
            delete_response = requests.delete(f'https://api.github.com/repos/{username}/{repo_name}', 
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
echo ============================================================
echo 🎯 GitHub Configuration Test Complete
echo ============================================================
echo.
echo 💡 If the test passed, GitHub auto-upload should work.
echo If it failed, check your token and username in keys.txt
echo.
pause
