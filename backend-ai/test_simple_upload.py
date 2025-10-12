#!/usr/bin/env python3
"""
Simple test for GitHub upload without file system issues
"""

import os
import sys
import time
from pathlib import Path

# Load keys first
try:
    from load_keys import load_keys_from_file
    load_keys_from_file()
    print("[OK] Keys loaded from keys.txt")
except ImportError:
    print("[WARN] load_keys.py not found, using environment variables only")

# Test direct GitHub upload
print(f"\n[INFO] Testing direct GitHub upload...")
try:
    # Add git-integration to path
    git_integration_path = Path(__file__).parent.parent / "git-integration"
    if git_integration_path.exists() and str(git_integration_path) not in sys.path:
        sys.path.insert(0, str(git_integration_path))
        print(f"[OK] Added git-integration to path")
    
    from github_service import GitHubService, GitHubRepository, GitHubFile
    
    # Get credentials
    token = os.environ.get('GITHUB_TOKEN')
    username = os.environ.get('GITHUB_USERNAME')
    
    if not token or not username:
        print("[ERROR] GitHub credentials not found")
        sys.exit(1)
    
    print(f"[OK] GitHub credentials found for user: {username}")
    
    # Initialize service
    service = GitHubService(token=token, username=username)
    print(f"[OK] GitHub service initialized")
    
    # Create a test repository
    repo_name = f"test-upload-{int(time.time())}"
    repo_description = "Test repository for GitHub upload functionality"
    
    print(f"\n[INFO] Creating test repository: {repo_name}")
    
    repo = GitHubRepository(
        name=repo_name,
        description=repo_description,
        private=False,
        auto_init=False
    )
    
    create_result = service.create_repository(repo)
    if not create_result["success"]:
        print(f"[ERROR] Failed to create repository: {create_result.get('error')}")
        sys.exit(1)
    
    repository_url = create_result['repository']['html_url']
    print(f"[OK] Repository created: {repository_url}")
    
    # Create test files
    test_files = [
        GitHubFile(
            path="test_file.py",
            content='''def hello_world():
    """A simple test function"""
    return "Hello, GitHub Upload Test!"

if __name__ == "__main__":
    print(hello_world())
''',
            message="Add test file"
        ),
        GitHubFile(
            path="README.md",
            content=f"""# {repo_name}

{repo_description}

This is a test repository created to verify GitHub upload functionality.

## Test File

The repository contains a simple Python test file.
""",
            message="Add README"
        )
    ]
    
    print(f"\n[INFO] Uploading {len(test_files)} files...")
    
    # Push files to GitHub
    push_result = service.push_files(
        repo_name=repo_name,
        files=test_files,
        commit_message="Test GitHub upload functionality"
    )
    
    if not push_result["success"]:
        print(f"[ERROR] Failed to push files: {push_result.get('error')}")
        sys.exit(1)
    
    print(f"[OK] Files uploaded successfully!")
    print(f"   Repository: {repository_url}")
    print(f"   Files pushed: {push_result['files_pushed']}")
    
    print(f"\n[SUCCESS] GitHub upload is working correctly!")
    print(f"   The issue might be in the file_manager.py file system operations")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
