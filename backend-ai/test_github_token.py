#!/usr/bin/env python3
"""
Test GitHub token permissions
"""

import os
import sys
from pathlib import Path

# Load keys
try:
    from load_keys import load_keys_from_file
    load_keys_from_file()
    print("[OK] Keys loaded")
except:
    pass

# Get credentials
token = os.environ.get('GITHUB_TOKEN')
username = os.environ.get('GITHUB_USERNAME')

if not token or not username:
    print("[ERROR] GitHub credentials not found")
    sys.exit(1)

print(f"[OK] Testing GitHub token for user: {username}")
print(f"   Token preview: {token[:10]}...")

# Test token by making a simple API request
import requests

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Test 1: Check authentication
print(f"\n[TEST 1] Checking authentication...")
try:
    response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"   [OK] Authenticated as: {user_data.get('login')}")
    elif response.status_code == 401:
        print(f"   [ERROR] Authentication failed (401)")
        print(f"   Your token might be expired or invalid")
        print(f"   Generate a new token at: https://github.com/settings/tokens")
    else:
        print(f"   [WARN] Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Request failed: {e}")

# Test 2: Check token scopes
print(f"\n[TEST 2] Checking token permissions...")
try:
    response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    
    if response.status_code == 200:
        scopes = response.headers.get('X-OAuth-Scopes', '')
        print(f"   Token scopes: {scopes}")
        
        required_scopes = ['repo', 'public_repo']
        has_required = any(scope in scopes for scope in required_scopes)
        
        if has_required:
            print(f"   [OK] Token has repository access")
        else:
            print(f"   [ERROR] Token missing repository access")
            print(f"   Required scopes: repo or public_repo")
            print(f"   Current scopes: {scopes}")
    else:
        print(f"   [SKIP] Cannot check scopes (auth failed)")
except Exception as e:
    print(f"   [ERROR] Request failed: {e}")

# Test 3: Try to create a test repository
print(f"\n[TEST 3] Testing repository creation...")
try:
    repo_data = {
        "name": f"test-token-permissions-{int(time.time())}",
        "description": "Test repository for token validation",
        "private": False,
        "auto_init": False
    }
    
    import time
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=repo_data, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        repo = response.json()
        print(f"   [OK] Repository created: {repo['html_url']}")
        print(f"   [INFO] Your token works perfectly!")
        
        # Clean up - delete the test repo
        print(f"   [INFO] Cleaning up test repository...")
        delete_response = requests.delete(f"https://api.github.com/repos/{username}/{repo_data['name']}", headers=headers, timeout=10)
        if delete_response.status_code == 204:
            print(f"   [OK] Test repository deleted")
    elif response.status_code == 401:
        print(f"   [ERROR] Authentication failed - token invalid or expired")
    elif response.status_code == 403:
        print(f"   [ERROR] Forbidden - token lacks repository creation permission")
        print(f"   Generate new token with 'repo' scope at: https://github.com/settings/tokens")
    elif response.status_code == 422:
        error_data = response.json()
        print(f"   [ERROR] Validation error: {error_data}")
    else:
        print(f"   [ERROR] Unexpected status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   [ERROR] Request failed: {e}")

print(f"\n[INFO] Test complete!")
print(f"\nIf all tests passed, your GitHub token is working correctly.")
print(f"If tests failed, generate a new token at: https://github.com/settings/tokens")
print(f"Required scopes: repo, workflow, write:packages")


