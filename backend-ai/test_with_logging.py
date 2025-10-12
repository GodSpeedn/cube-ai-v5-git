#!/usr/bin/env python3
"""
Test with explicit logging configuration to see what's happening
"""

import logging
import sys

# Configure logging to show everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Load keys
try:
    from load_keys import load_keys_from_file
    load_keys_from_file()
    print("[OK] Keys loaded")
except:
    print("[WARN] Keys not loaded")

# Test file_manager GitHub availability
print("\n[INFO] Testing FileManager...")
try:
    from file_manager import get_file_manager
    fm = get_file_manager()
    print(f"[OK] FileManager created")
    print(f"   GitHub available: {fm.github_available}")
    
    # Check environment variables
    import os
    print(f"   GITHUB_TOKEN: {'Set' if os.environ.get('GITHUB_TOKEN') else 'Not set'}")
    print(f"   GITHUB_USERNAME: {'Set' if os.environ.get('GITHUB_USERNAME') else 'Not set'}")
    
except Exception as e:
    print(f"[ERROR] FileManager test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[INFO] Test complete!")

