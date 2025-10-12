#!/usr/bin/env python3
"""
Test script to verify GitHub integration and upload functionality
"""

import requests
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_github_integration():
    """Test GitHub integration functionality"""
    print("🧪 Testing GitHub Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check Git status
    print("\n1. Checking Git status...")
    try:
        response = requests.get(f"{base_url}/git/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Git Status: {status}")
            
            if not status.get('configured', False):
                print("❌ GitHub is NOT configured!")
                print("   You need to configure GitHub first.")
                print("   Use the /git/configure endpoint with your GitHub token and username.")
                return False
            else:
                print("✅ GitHub is configured!")
        else:
            print(f"❌ Failed to get Git status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking Git status: {e}")
        return False
    
    # Test 2: List repositories
    print("\n2. Listing GitHub repositories...")
    try:
        response = requests.get(f"{base_url}/git/repositories")
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {len(repos.get('repositories', []))} repositories")
            for repo in repos.get('repositories', [])[:5]:  # Show first 5
                print(f"   - {repo.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to list repositories: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing repositories: {e}")
    
    # Test 3: Test upload functionality
    print("\n3. Testing upload functionality...")
    try:
        # Try to upload to a test repository
        upload_data = {
            "repository": "test-ai-upload",
            "commit_message": "Test upload from AI system",
            "project_name": "test-project"
        }
        
        response = requests.post(f"{base_url}/git/push", json=upload_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful: {result}")
        else:
            error = response.json()
            print(f"❌ Upload failed: {error}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {error.get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
    
    print("\n" + "=" * 50)
    print("GitHub integration test completed!")
    return True

def configure_github_interactive():
    """Interactive GitHub configuration"""
    print("\n🔧 GitHub Configuration")
    print("=" * 30)
    print("To configure GitHub, you need:")
    print("1. A GitHub Personal Access Token")
    print("2. Your GitHub username")
    print()
    print("To get a GitHub token:")
    print("1. Go to GitHub.com → Settings → Developer settings")
    print("2. Personal access tokens → Tokens (classic)")
    print("3. Generate new token (classic)")
    print("4. Select scopes: repo, workflow, write:packages")
    print("5. Copy the token")
    print()
    
    token = input("Enter your GitHub token: ").strip()
    username = input("Enter your GitHub username: ").strip()
    
    if not token or not username:
        print("❌ Token and username are required!")
        return False
    
    # Configure GitHub
    config_data = {
        "token": token,
        "username": username
    }
    
    try:
        response = requests.post("http://localhost:8000/git/configure", json=config_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GitHub configured successfully!")
            print(f"   User: {result.get('user', 'Unknown')}")
            print(f"   Repositories: {len(result.get('repositories', []))}")
            return True
        else:
            error = response.json()
            print(f"❌ Configuration failed: {error}")
            return False
    except Exception as e:
        print(f"❌ Error configuring GitHub: {e}")
        return False

if __name__ == "__main__":
    print("GitHub Integration Test")
    print("=" * 50)
    
    # Test current status
    test_github_integration()
    
    # Ask if user wants to configure
    print("\n" + "=" * 50)
    configure = input("Do you want to configure GitHub now? (y/n): ").strip().lower()
    
    if configure == 'y':
        configure_github_interactive()
        print("\n" + "=" * 50)
        print("Testing after configuration...")
        test_github_integration()
    else:
        print("Skipping configuration. Run this script again to configure GitHub.")

