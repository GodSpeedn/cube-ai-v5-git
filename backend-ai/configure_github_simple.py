#!/usr/bin/env python3
"""
Simple GitHub configuration script
"""

import requests
import json

def configure_github():
    """Configure GitHub integration"""
    print("🔧 GitHub Configuration")
    print("=" * 40)
    print("You need to configure GitHub to enable uploads.")
    print()
    print("To get a GitHub Personal Access Token:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select these scopes:")
    print("   ✅ repo (Full control of private repositories)")
    print("   ✅ workflow (Update GitHub Action workflows)")
    print("   ✅ write:packages (Upload packages to GitHub Package Registry)")
    print("4. Click 'Generate token'")
    print("5. Copy the token (you won't see it again!)")
    print()
    
    # Get credentials
    token = input("Enter your GitHub Personal Access Token: ").strip()
    username = input("Enter your GitHub username: ").strip()
    
    if not token or not username:
        print("❌ Both token and username are required!")
        return False
    
    # Configure GitHub
    config_data = {
        "token": token,
        "username": username
    }
    
    try:
        print("🔄 Configuring GitHub...")
        response = requests.post("http://localhost:8000/git/configure", json=config_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ GitHub configured successfully!")
            print(f"   User: {result.get('user', 'Unknown')}")
            print(f"   Repositories: {len(result.get('repositories', []))}")
            print()
            print("🎉 You can now upload code to GitHub!")
            return True
        else:
            error = response.json()
            print(f"❌ Configuration failed: {error.get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring GitHub: {e}")
        return False

def test_upload():
    """Test upload after configuration"""
    print("\n🧪 Testing Upload...")
    
    try:
        # Test upload to a repository
        upload_data = {
            "repository": "your-username/test-repo",  # Change this to your repo
            "commit_message": "Test upload from AI system",
            "project_name": "test-project"
        }
        
        response = requests.post("http://localhost:8000/git/push", json=upload_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload test successful!")
            print(f"   Repository: {result.get('repository_url', 'Unknown')}")
            print(f"   Files: {result.get('files_pushed', 0)}")
        else:
            error = response.json()
            print(f"❌ Upload test failed: {error.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")

if __name__ == "__main__":
    print("GitHub Configuration Tool")
    print("=" * 50)
    
    # Configure GitHub
    if configure_github():
        print("\n" + "=" * 50)
        test_upload()
    else:
        print("\n❌ Configuration failed. Please try again.")

