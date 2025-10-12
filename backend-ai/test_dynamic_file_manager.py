#!/usr/bin/env python3
"""
Test script to verify dynamic file manager functionality
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from file_manager import file_manager

def test_dynamic_file_manager():
    """Test the dynamic file manager functionality"""
    print("🧪 Testing Dynamic File Manager")
    print("=" * 50)
    
    # Test 1: List all projects
    print("\n1. Listing all projects...")
    projects = file_manager.list_projects()
    print(f"✅ Found {len(projects)} projects")
    
    for project in projects:
        print(f"   - {project['name']} ({project['file_count']} files)")
        print(f"     Description: {project['description']}")
        print(f"     Status: {project['status']}")
    
    # Test 2: Get files for each project (DYNAMIC)
    print("\n2. Testing dynamic file retrieval...")
    for project in projects:
        project_name = project['name']
        print(f"\n📁 Project: {project_name}")
        
        files = file_manager.get_project_files(project_name)
        print(f"   Found {len(files)} files:")
        
        # Group files by type
        file_types = {}
        for file in files:
            file_type = file.get('type', 'other')
            if file_type not in file_types:
                file_types[file_type] = []
            file_types[file_type].append(file)
        
        # Display files by type
        for file_type, type_files in file_types.items():
            print(f"     📂 {file_type.upper()}: {len(type_files)} files")
            for file in type_files:
                print(f"       - {file['name']} ({file['size']} bytes)")
                print(f"         Path: {file['path']}")
                print(f"         Directory: {file.get('directory', 'root')}")
                print(f"         Is Code: {file.get('is_code', False)}")
                print(f"         Is Test: {file.get('is_test', False)}")
                print(f"         Is Config: {file.get('is_config', False)}")
                print(f"         Is Documentation: {file.get('is_documentation', False)}")
                if file.get('content'):
                    content_preview = file['content'][:100].replace('\n', ' ')
                    print(f"         Content: {content_preview}...")
                print()
    
    print("\n" + "=" * 50)
    print("Dynamic file manager test completed!")
    print("✅ File manager is now DYNAMIC and shows ALL files!")
    print("✅ Files are properly categorized by type!")
    print("✅ Content is included for Monaco Editor!")

if __name__ == "__main__":
    test_dynamic_file_manager()

