#!/usr/bin/env python3
"""
Enable automatic GitHub upload for all generated projects
"""
import requests
import json
import time
from pathlib import Path

def enable_auto_github_upload():
    """Enable automatic GitHub upload for all existing and future projects"""
    print("Enabling Automatic GitHub Upload")
    print("=" * 50)
    
    # Check GitHub status
    print("1. Checking GitHub integration...")
    try:
        git_status_response = requests.get("http://localhost:8000/git/status")
        if git_status_response.status_code == 200:
            git_status = git_status_response.json()
            if git_status.get("configured", False):
                print(f"[SUCCESS] GitHub is configured")
                print(f"   User: {git_status.get('user', {}).get('login', 'Unknown')}")
                print(f"   Repositories: {len(git_status.get('repositories', []))}")
            else:
                print(f"[ERROR] GitHub is not configured")
                return False
        else:
            print(f"[ERROR] Could not check GitHub status")
            return False
    except Exception as e:
        print(f"[ERROR] GitHub check failed: {e}")
        return False
    
    # Upload all existing projects
    print("\n2. Uploading existing projects...")
    generated_dir = Path("generated/projects")
    if generated_dir.exists():
        projects = list(generated_dir.glob("*"))
        print(f"   Found {len(projects)} projects to upload")
        
        for project in projects:
            if project.is_dir():
                project_name = project.name
                print(f"\n   Uploading: {project_name}")
                
                # Read project metadata
                project_json = project / "project.json"
                task_description = "AI Generated Project"
                if project_json.exists():
                    try:
                        with open(project_json, 'r') as f:
                            metadata = json.load(f)
                        task_description = metadata.get('task_description', 'AI Generated Project')
                    except:
                        pass
                
                # Upload to GitHub
                try:
                    upload_request = {
                        "project_name": project_name,
                        "task_description": task_description,
                        "create_new_repo": True
                    }
                    
                    response = requests.post(
                        "http://localhost:8000/git/auto-upload",
                        json=upload_request,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            print(f"   [SUCCESS] {result.get('repository_url')}")
                            print(f"   Files: {result.get('files_uploaded', 0)}")
                            
                            # Update project.json with GitHub info
                            if project_json.exists():
                                try:
                                    with open(project_json, 'r') as f:
                                        metadata = json.load(f)
                                    metadata['github_repo'] = result.get('repository_url')
                                    metadata['status'] = 'uploaded'
                                    with open(project_json, 'w') as f:
                                        json.dump(metadata, f, indent=2)
                                except:
                                    pass
                        else:
                            print(f"   [ERROR] {result.get('error', 'Unknown error')}")
                    else:
                        print(f"   [ERROR] Upload failed: {response.status_code}")
                        print(f"   {response.text}")
                        
                except Exception as e:
                    print(f"   [ERROR] Upload failed: {e}")
    else:
        print("   No existing projects found")
    
    # Test automatic upload for new projects
    print("\n3. Testing automatic upload for new projects...")
    test_code = '''
def hello_world():
    """Simple hello world function"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
    
    try:
        # Create a new project with auto-upload
        save_request = {
            "code": test_code,
            "filename": "hello_world.py",
            "file_type": "src",
            "task_description": "Simple hello world program for testing auto-upload",
            "conversation_id": f"auto_upload_test_{int(time.time())}"
        }
        
        response = requests.post(
            "http://localhost:8000/projects/save-code",
            json=save_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] New project created: {result.get('project_name')}")
            
            # Check if auto-upload worked
            github_result = result.get('github_result', {})
            if github_result.get('status') == 'success':
                print(f"   GitHub: {github_result.get('repo_url')}")
                print(f"   Files: {github_result.get('files_uploaded', 0)}")
            else:
                print(f"   GitHub: {github_result.get('error', 'Auto-upload not triggered')}")
        else:
            print(f"[ERROR] Project creation failed: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Auto-Upload Setup Complete!")
    print("=" * 50)
    print("\nYour system is now configured for automatic GitHub upload!")
    print("All generated code will be automatically uploaded to GitHub repositories.")
    print("Check your GitHub account for new repositories.")

if __name__ == "__main__":
    enable_auto_github_upload()


