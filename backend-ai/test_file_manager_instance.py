#!/usr/bin/env python3
"""
Test the file_manager instance vs creating a new FileManager
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

# Test 1: Create new FileManager instance (like our test)
print(f"\n[INFO] Test 1: Creating new FileManager instance...")
try:
    from file_manager import FileManager
    fm_new = FileManager()
    print(f"[OK] New FileManager created")
    print(f"   GitHub available: {fm_new.github_available}")
except Exception as e:
    print(f"[ERROR] Failed to create new FileManager: {e}")

# Test 2: Import the global file_manager instance (like online_agent_service does)
print(f"\n[INFO] Test 2: Importing global file_manager instance...")
try:
    from file_manager import file_manager
    print(f"[OK] Global file_manager imported")
    print(f"   GitHub available: {file_manager.github_available}")
except Exception as e:
    print(f"[ERROR] Failed to import global file_manager: {e}")

# Test 3: Check if they're the same
print(f"\n[INFO] Test 3: Comparing instances...")
try:
    print(f"   New instance GitHub available: {fm_new.github_available}")
    print(f"   Global instance GitHub available: {file_manager.github_available}")
    print(f"   Are they the same object: {fm_new is file_manager}")
except Exception as e:
    print(f"[ERROR] Comparison failed: {e}")

print(f"\n[INFO] Test complete!")
