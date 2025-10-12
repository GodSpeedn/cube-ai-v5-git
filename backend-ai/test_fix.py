#!/usr/bin/env python3
"""
Test script to verify the GitHub upload fix
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

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

# Test FileManager initialization
print(f"\n[INFO] Testing FileManager initialization...")
try:
    from file_manager import FileManager
    
    # This should not try to connect to port 8000 anymore
    fm = FileManager()
    
    print(f"[OK] FileManager initialized successfully")
    print(f"   GitHub available: {fm.github_available}")
    
    if fm.github_available:
        print("[OK] GitHub service is available for auto-upload")
    else:
        print("[ERROR] GitHub service is not available")
        
except Exception as e:
    print(f"[ERROR] FileManager initialization failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n[INFO] Test complete!")
