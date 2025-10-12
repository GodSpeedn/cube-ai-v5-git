#!/usr/bin/env python3
"""
Test actual GitHub upload functionality
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

# Test the actual file_manager
print(f"\n[INFO] Testing actual file_manager GitHub upload...")
try:
    from file_manager import FileManager
    
    # Create a file manager instance
    fm = FileManager()
    print(f"[OK] FileManager created")
    print(f"   GitHub available: {fm.github_available}")
    
    if not fm.github_available:
        print("[ERROR] GitHub is not available in FileManager")
        sys.exit(1)
    
    # Create a test project
    print(f"\n[INFO] Creating test project...")
    result = fm.create_project("Test GitHub Upload", "test_conversation_123")
    print(f"[OK] Project created: {result}")
    
    project_dir = Path(result['project_dir'])
    print(f"   Project directory: {project_dir}")
    
    # Save some test code
    print(f"\n[INFO] Saving test code...")
    test_code = '''
def hello_world():
    """A simple test function"""
    return "Hello, GitHub Upload Test!"

if __name__ == "__main__":
    print(hello_world())
'''
    
    save_result = fm.save_code(
        code=test_code,
        filename="test_upload.py",
        task_description="Test GitHub upload functionality",
        conversation_id="test_conversation_123"
    )
    
    print(f"[OK] Code saved: {save_result}")
    
    # Check if GitHub upload was attempted
    if 'github' in save_result:
        print(f"[OK] GitHub upload result: {save_result['github']}")
    else:
        print("[WARN] No GitHub upload result found")
    
    print(f"\n[INFO] Test complete!")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
