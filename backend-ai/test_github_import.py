#!/usr/bin/env python3
"""
Test GitHub service import
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add git-integration to path
git_integration_path = current_dir.parent / "git-integration"
print(f"Git integration path: {git_integration_path}")
print(f"Git integration exists: {git_integration_path.exists()}")

if git_integration_path.exists():
    if str(git_integration_path) not in sys.path:
        sys.path.insert(0, str(git_integration_path))
        print(f"✅ Added to path: {git_integration_path}")
    
    # List files in git-integration
    print(f"\nFiles in git-integration:")
    for item in git_integration_path.iterdir():
        print(f"  - {item.name}")
    
    # Try to import
    print(f"\n🔍 Attempting import...")
    try:
        from github_service import GitHubService, GitHubRepository, GitHubFile
        print("✅ Import successful!")
        print(f"   GitHubService: {GitHubService}")
        print(f"   GitHubRepository: {GitHubRepository}")
        print(f"   GitHubFile: {GitHubFile}")
        
        # Test initialization
        print(f"\n🔍 Testing GitHub service initialization...")
        token = os.environ.get('GITHUB_TOKEN')
        username = os.environ.get('GITHUB_USERNAME')
        
        if token and username and token != 'your_github_token_here':
            print(f"✅ Found credentials for: {username}")
            try:
                service = GitHubService(token=token, username=username)
                print(f"✅ GitHub service initialized successfully")
                
                # Test token validation
                result = service.validate_token()
                if result.get('success'):
                    print(f"✅ Token is valid!")
                    user = result.get('user', {})
                    print(f"   User: {user.get('login', 'Unknown')}")
                    print(f"   Public repos: {user.get('public_repos', 0)}")
                else:
                    print(f"❌ Token validation failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Failed to initialize service: {e}")
        else:
            print(f"⚠️ No GitHub credentials found in environment")
            print(f"   GITHUB_TOKEN: {'Set' if token else 'Not set'}")
            print(f"   GITHUB_USERNAME: {'Set' if username else 'Not set'}")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print(f"\nPython path:")
        for p in sys.path:
            print(f"  - {p}")
else:
    print(f"❌ git-integration folder not found at: {git_integration_path}")
