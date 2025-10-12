#!/usr/bin/env python3
"""
Test script to verify GitHub repository creation functionality
"""

import requests
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_github_creation():
    """Test GitHub repository creation"""
    print("🧪 Testing GitHub Repository Creation")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if GitHub is configured
    print("\n1. Checking GitHub configuration...")
    try:
        response = requests.get(f"{base_url}/git/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Git Status: {status}")
            
            if not status.get('configured', False):
                print("❌ GitHub is NOT configured!")
                print("   You need to configure GitHub first.")
                return False
            else:
                print("✅ GitHub is configured!")
        else:
            print(f"❌ Failed to get Git status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking Git status: {e}")
        return False
    
    # Test 2: Test repository creation
    print("\n2. Testing repository creation...")
    try:
        # Create a test repository
        repo_data = {
            "name": "test-ai-repo-creation",
            "description": "Test repository creation from AI system",
            "private": False
        }
        
        # This should create a new repository
        response = requests.post(f"{base_url}/git/create-repo", json=repo_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Repository creation successful!")
            print(f"   Repository: {result.get('repository_url', 'Unknown')}")
            print(f"   Name: {result.get('name', 'Unknown')}")
        else:
            error = response.json()
            print(f"❌ Repository creation failed: {error}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {error.get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error testing repository creation: {e}")
    
    # Test 3: Test auto-upload with new repository
    print("\n3. Testing auto-upload with new repository...")
    try:
        # This should create a new repository and upload files
        upload_data = {
            "project_name": "test-auto-upload",
            "task_description": "Test auto-upload functionality",
            "create_new_repo": True
        }
        
        response = requests.post(f"{base_url}/projects/auto-upload", json=upload_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Auto-upload successful!")
            print(f"   Repository: {result.get('repository_url', 'Unknown')}")
            print(f"   Files: {result.get('files_uploaded', 0)}")
        else:
            error = response.json()
            print(f"❌ Auto-upload failed: {error}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {error.get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error testing auto-upload: {e}")
    
    print("\n" + "=" * 50)
    print("GitHub creation test completed!")
    return True

def diagnose_upload_issue():
    """Diagnose why uploads are failing"""
    print("\n🔍 Diagnosing Upload Issue")
    print("=" * 40)
    
    print("The issue might be:")
    print("1. ❌ GitHub not configured")
    print("2. ❌ Repository creation failing")
    print("3. ❌ File upload failing")
    print("4. ❌ Permission issues")
    print("5. ❌ Network issues")
    print()
    
    print("Let's check each step:")
    
    # Check configuration
    try:
        response = requests.get("http://localhost:8000/git/status")
        status = response.json()
        
        if not status.get('configured'):
            print("❌ Issue 1: GitHub not configured")
            print("   Solution: Configure GitHub with token and username")
            return
        else:
            print("✅ GitHub is configured")
    except Exception as e:
        print(f"❌ Cannot check configuration: {e}")
        return
    
    # Check if we can list repositories
    try:
        response = requests.get("http://localhost:8000/git/repositories")
        repos = response.json()
        print(f"✅ Can access GitHub: {len(repos.get('repositories', []))} repositories")
    except Exception as e:
        print(f"❌ Cannot access GitHub: {e}")
        return
    
    print("\n🎯 The issue is likely:")
    print("   The system is trying to push to existing repositories")
    print("   instead of creating new ones for auto-upload.")
    print()
    print("🔧 Solution:")
    print("   We need to fix the auto-upload logic to create new repositories")

if __name__ == "__main__":
    print("GitHub Repository Creation Test")
    print("=" * 50)
    
    # Test current functionality
    test_github_creation()
    
    # Diagnose issues
    diagnose_upload_issue()

