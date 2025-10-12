#!/usr/bin/env python3
"""
Test script to verify new repository creation functionality
"""

import requests
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_new_repo_creation():
    """Test creating new repositories for auto-upload"""
    print("🧪 Testing New Repository Creation")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check GitHub configuration
    print("\n1. Checking GitHub configuration...")
    try:
        response = requests.get(f"{base_url}/git/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Git Status: {status}")
            
            if not status.get('configured', False):
                print("❌ GitHub is NOT configured!")
                print("   You need to configure GitHub first.")
                print("   Run: python configure_github_simple.py")
                return False
            else:
                print("✅ GitHub is configured!")
        else:
            print(f"❌ Failed to get Git status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking Git status: {e}")
        return False
    
    # Test 2: Test new repository creation
    print("\n2. Testing new repository creation...")
    try:
        # Test auto-upload with new repository
        upload_data = {
            "project_name": "test-new-repo-creation",
            "task_description": "Test creating a new repository for AI-generated code",
            "create_new_repo": True
        }
        
        print(f"🚀 Testing auto-upload with data: {upload_data}")
        response = requests.post(f"{base_url}/git/auto-upload", json=upload_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Auto-upload successful!")
            print(f"   Repository: {result.get('repository_url', 'Unknown')}")
            print(f"   Files: {result.get('files_uploaded', 0)}")
            print(f"   Commit: {result.get('commit_sha', 'Unknown')}")
            print(f"   Message: {result.get('message', 'Unknown')}")
            return True
        else:
            error = response.json()
            print(f"❌ Auto-upload failed: {error}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {error.get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing auto-upload: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("New repository creation test completed!")
    return True

def test_existing_project_upload():
    """Test uploading an existing project"""
    print("\n🧪 Testing Existing Project Upload")
    print("=" * 40)
    
    # Find an existing project
    try:
        response = requests.get("http://localhost:8000/projects")
        if response.status_code == 200:
            projects = response.json()
            project_list = projects.get('projects', [])
            
            if not project_list:
                print("❌ No existing projects found")
                return False
            
            # Use the first project
            project = project_list[0]
            project_name = project['name']
            print(f"📁 Using existing project: {project_name}")
            
            # Test auto-upload
            upload_data = {
                "project_name": project_name,
                "task_description": f"Upload existing project: {project_name}",
                "create_new_repo": True
            }
            
            print(f"🚀 Testing auto-upload for existing project...")
            response = requests.post("http://localhost:8000/git/auto-upload", json=upload_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Existing project upload successful!")
                print(f"   Repository: {result.get('repository_url', 'Unknown')}")
                print(f"   Files: {result.get('files_uploaded', 0)}")
                return True
            else:
                error = response.json()
                print(f"❌ Existing project upload failed: {error}")
                return False
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing existing project upload: {e}")
        return False

def main():
    """Main test function"""
    print("GitHub New Repository Creation Test")
    print("=" * 50)
    
    # Test 1: New repository creation
    success1 = test_new_repo_creation()
    
    # Test 2: Existing project upload
    success2 = test_existing_project_upload()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"✅ New repository creation: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Existing project upload: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! GitHub auto-upload is working correctly!")
        print("   The system now creates NEW repositories instead of trying to push to existing ones.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        print("   Make sure GitHub is configured and you have the necessary permissions.")

if __name__ == "__main__":
    main()

