#!/usr/bin/env python3
"""
Configure Backend GitHub Service
This script configures the backend GitHub service to match your frontend configuration
"""

import requests
import json

def configure_backend_github():
    """Configure the backend GitHub service"""
    
    print("🔧 Configuring Backend GitHub Service")
    print("=" * 50)
    
    # Get GitHub credentials from user
    print("Enter your GitHub credentials (same as used in frontend):")
    token = input("GitHub Personal Access Token: ").strip()
    username = input("GitHub Username: ").strip()
    email = input("GitHub Email (optional): ").strip()
    
    if not token or not username:
        print("❌ Token and username are required!")
        return False
    
    # Configure backend GitHub service
    config_data = {
        "token": token,
        "username": username,
        "email": email
    }
    
    try:
        print("\n🚀 Configuring backend GitHub service...")
        response = requests.post('http://localhost:8000/git/configure', json=config_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend GitHub service configured successfully!")
            print(f"👤 User: {result.get('user', {}).get('login', 'Unknown')}")
            print(f"📊 Repositories: {len(result.get('repositories', []))}")
            return True
        else:
            error = response.json()
            print(f"❌ Configuration failed: {error.get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to configure: {str(e)}")
        return False

def test_backend_github():
    """Test if backend GitHub is working"""
    
    print("\n🧪 Testing Backend GitHub Configuration")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8000/git/status')
        
        if response.status_code == 200:
            status = response.json()
            if status.get('configured'):
                print("✅ Backend GitHub is configured and working!")
                print(f"👤 User: {status.get('user', {}).get('login', 'Unknown')}")
                print(f"📊 Repositories: {len(status.get('repositories', []))}")
                return True
            else:
                print("❌ Backend GitHub is not configured")
                return False
        else:
            print(f"❌ Failed to check status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test: {str(e)}")
        return False

def test_auto_upload():
    """Test auto-upload functionality"""
    
    print("\n🚀 Testing Auto-Upload Functionality")
    print("=" * 50)
    
    # Test data
    test_data = {
        "code": 'print("Hello from Auto-Upload Test!")\nprint("This should create a new GitHub repository")',
        "task_description": "Auto-Upload Test - Backend GitHub Configuration",
        "filename": "test_auto_upload_backend.py"
    }
    
    try:
        print("📝 Testing code save with auto-upload...")
        response = requests.post('http://localhost:8000/projects/save-code', json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code saved successfully!")
            
            # Check GitHub result
            github_result = result.get('result', {}).get('github_result', {})
            if github_result.get('status') == 'success':
                print("🐙 GitHub Upload: SUCCESS!")
                print(f"🔗 Repository: {github_result.get('repo_url', 'Unknown')}")
                print(f"📊 Files uploaded: {github_result.get('files_uploaded', 0)}")
                return True
            elif github_result.get('status') == 'github_not_available':
                print("ℹ️ GitHub not available - code saved locally only")
                return False
            else:
                print(f"⚠️ GitHub upload issue: {github_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Save failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Backend GitHub Configuration Tool")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code != 200:
            print("❌ Backend service is not running!")
            print("Please start the backend service first: python main.py")
            exit(1)
    except:
        print("❌ Backend service is not running!")
        print("Please start the backend service first: python main.py")
        exit(1)
    
    print("✅ Backend service is running")
    
    # Test current status
    if test_backend_github():
        print("\n🎉 Backend GitHub is already configured!")
        if test_auto_upload():
            print("\n🎉 Auto-upload is working perfectly!")
        else:
            print("\n⚠️ Auto-upload needs fixing")
    else:
        print("\n🔧 Backend GitHub needs configuration")
        if configure_backend_github():
            if test_auto_upload():
                print("\n🎉 Configuration successful! Auto-upload is working!")
            else:
                print("\n⚠️ Configuration successful but auto-upload needs fixing")
        else:
            print("\n❌ Configuration failed")

