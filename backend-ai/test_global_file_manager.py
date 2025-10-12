#!/usr/bin/env python3
"""
Test the global file_manager instance directly
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

# Test the global file_manager instance (like online_agent_service uses)
print(f"\n[INFO] Testing global file_manager instance...")
try:
    from file_manager import file_manager
    
    print(f"[OK] Global file_manager imported")
    print(f"   GitHub available: {file_manager.github_available}")
    
    if not file_manager.github_available:
        print("[ERROR] GitHub is not available in global file_manager")
        sys.exit(1)
    
    # Create a test project
    print(f"\n[INFO] Creating test project...")
    result = file_manager.create_project("Test Global FileManager", "test_global_123")
    print(f"[OK] Project created: {result}")
    
    project_dir = Path(result['project_dir'])
    print(f"   Project directory: {project_dir}")
    
    # Save some test code
    print(f"\n[INFO] Saving test code...")
    test_code = '''
def test_global_file_manager():
    """Test function for global file_manager"""
    return "Global file_manager test successful!"

if __name__ == "__main__":
    print(test_global_file_manager())
'''
    
    save_result = file_manager.save_code(
        code=test_code,
        filename="test_global.py",
        task_description="Test global file_manager GitHub upload",
        conversation_id="test_global_123"
    )
    
    print(f"[OK] Code saved: {save_result}")
    
    # Check if GitHub upload was attempted
    if 'github_result' in save_result:
        github_result = save_result['github_result']
        print(f"[OK] GitHub upload result: {github_result}")
        
        if github_result.get('status') == 'success':
            print(f"[SUCCESS] GitHub upload successful!")
            print(f"   Repository: {github_result.get('repo_url')}")
            print(f"   Files uploaded: {github_result.get('files_uploaded')}")
        else:
            print(f"[ERROR] GitHub upload failed: {github_result.get('error')}")
    else:
        print("[WARN] No GitHub upload result found")
    
    print(f"\n[INFO] Test complete!")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
