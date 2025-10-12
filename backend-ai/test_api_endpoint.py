#!/usr/bin/env python3
"""
Test the API endpoint directly
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import _create_folder_structure

def test_folder_structure():
    """Test the folder structure creation"""
    print("🧪 Testing Folder Structure Creation")
    print("=" * 50)
    
    # Mock files data
    mock_files = [
        {
            "name": "test_hello.py",
            "path": "src/test_hello.py",
            "type": "src",
            "size": 500,
            "modified": "2025-01-01T12:00:00",
            "content": "def hello(): print('Hello')",
            "is_test": False,
            "extension": ".py"
        },
        {
            "name": "test_sum.py",
            "path": "tests/test_sum.py", 
            "type": "tests",
            "size": 300,
            "modified": "2025-01-01T12:00:00",
            "content": "def test_sum(): assert True",
            "is_test": True,
            "extension": ".py"
        }
    ]
    
    # Test folder structure creation
    folder_structure = _create_folder_structure(mock_files)
    
    print(f"✅ Created folder structure with {len(folder_structure)} folders:")
    for folder in folder_structure:
        print(f"   - {folder['name']}: {len(folder['children'])} files")
        for file in folder['children']:
            print(f"     - {file['name']} ({file['type']})")
    
    print("\n" + "=" * 50)
    print("Folder structure test completed!")

if __name__ == "__main__":
    test_folder_structure()

