#!/usr/bin/env python3
"""
Simple test to verify GitHub upload fix
"""

import os
import sys
from pathlib import Path

# Load keys first
try:
    from load_keys import load_keys_from_file
    load_keys_from_file()
    print("[OK] Keys loaded from keys.txt")
except ImportError:
    print("[WARN] load_keys.py not found, using environment variables only")

# Check environment variables
print(f"\n[INFO] Environment variables:")
print(f"   GITHUB_TOKEN: {'Set' if os.environ.get('GITHUB_TOKEN') else 'Not set'}")
print(f"   GITHUB_USERNAME: {'Set' if os.environ.get('GITHUB_USERNAME') else 'Not set'}")

if os.environ.get('GITHUB_TOKEN'):
    token = os.environ.get('GITHUB_TOKEN')
    if token != 'your_github_token_here':
        print(f"   Token preview: {token[:10]}...")
    else:
        print("   [WARN] Token is still placeholder value")

# Test GitHub service import
print(f"\n[INFO] Testing GitHub service import...")
try:
    # Add git-integration to path
    git_integration_path = Path(__file__).parent.parent / "git-integration"
    if git_integration_path.exists() and str(git_integration_path) not in sys.path:
        sys.path.insert(0, str(git_integration_path))
        print(f"[OK] Added git-integration to path: {git_integration_path}")
    
    from github_service import GitHubService, GitHubRepository, GitHubFile
    print("[OK] GitHub service modules imported successfully")
    
    # Test initialization
    if os.environ.get('GITHUB_TOKEN') and os.environ.get('GITHUB_USERNAME'):
        token = os.environ.get('GITHUB_TOKEN')
        username = os.environ.get('GITHUB_USERNAME')
        
        if token != 'your_github_token_here':
            service = GitHubService(token=token, username=username)
            print("[OK] GitHub service initialized successfully")
            print(f"   Username: {username}")
            print("[OK] GitHub upload should work!")
        else:
            print("[ERROR] GitHub token is still placeholder value")
    else:
        print("[ERROR] GitHub credentials not found in environment")
        
except ImportError as e:
    print(f"[ERROR] GitHub service import failed: {e}")
    print("Available files in git-integration:")
    if git_integration_path.exists():
        for item in git_integration_path.iterdir():
            print(f"  - {item.name}")
    else:
        print("  git-integration folder not found")
except Exception as e:
    print(f"[ERROR] GitHub service initialization failed: {e}")

print(f"\n[INFO] Test complete!")
print(f"\n[INFO] If all tests passed, the GitHub upload should work.")
print(f"[INFO] The issue was that file_manager.py was trying to connect to port 8000")
print(f"[INFO] Now it loads GitHub credentials directly from environment variables.")
