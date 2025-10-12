#!/usr/bin/env python3
"""
Simple test script that won't crash
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("🧪 Simple GitHub Test")
print("=" * 60)

# Check current directory
print(f"\n📁 Current directory: {os.getcwd()}")

# Check if we're in the right place
if not Path("..").exists():
    print("❌ Can't find parent directory")
    sys.exit(1)

# Check git-integration folder
git_integration_path = Path("..") / "git-integration"
print(f"\n🔍 Git integration path: {git_integration_path}")
print(f"   Exists: {git_integration_path.exists()}")

if not git_integration_path.exists():
    print("❌ git-integration folder not found")
    sys.exit(1)

# Check github_service.py
github_service_file = git_integration_path / "github_service.py"
print(f"\n🔍 GitHub service file: {github_service_file}")
print(f"   Exists: {github_service_file.exists()}")

if not github_service_file.exists():
    print("❌ github_service.py not found")
    sys.exit(1)

# Add to path
if str(git_integration_path) not in sys.path:
    sys.path.insert(0, str(git_integration_path))
    print(f"✅ Added to Python path: {git_integration_path}")

# Try to import
print(f"\n🔍 Attempting import...")
try:
    from github_service import GitHubService
    print("✅ GitHubService imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nAvailable files in git-integration:")
    for item in git_integration_path.iterdir():
        print(f"  - {item.name}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Other error: {e}")
    sys.exit(1)

# Check environment variables
print(f"\n🔍 Checking environment variables...")
token = os.environ.get('GITHUB_TOKEN')
username = os.environ.get('GITHUB_USERNAME')

print(f"   GITHUB_TOKEN: {'Set' if token else 'Not set'}")
print(f"   GITHUB_USERNAME: {'Set' if username else 'Not set'}")

if not token or not username:
    print("❌ GitHub credentials not found in environment")
    print("💡 Make sure to run this from a service that loaded keys.txt")
    sys.exit(1)

if token == 'your_github_token_here':
    print("❌ GitHub token is still set to placeholder value")
    print("💡 Update your token in keys.txt")
    sys.exit(1)

print(f"✅ GitHub credentials found for user: {username}")

# Test initialization
print(f"\n🔍 Testing GitHub service initialization...")
try:
    service = GitHubService(token=token, username=username)
    print("✅ GitHub service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize service: {e}")
    sys.exit(1)

print(f"\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
print(f"\n💡 Your GitHub integration should work.")
print(f"   If upload still fails, check the service logs for specific errors.")
