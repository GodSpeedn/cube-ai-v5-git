#!/usr/bin/env python3
"""
Test script to verify file manager functionality
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from file_manager import file_manager

def test_file_manager():
    """Test the file manager functionality"""
    print("🧪 Testing File Manager Functionality")
    print("=" * 50)
    
    # Test 1: List projects
    print("\n1. Testing project listing...")
    projects = file_manager.list_projects()
    print(f"✅ Found {len(projects)} projects:")
    for project in projects:
        print(f"   - {project['name']} ({project['file_count']} files)")
        print(f"     Description: {project['description']}")
        print(f"     Status: {project['status']}")
        if project.get('github_repo'):
            print(f"     GitHub: {project['github_repo']}")
    
    # Test 2: Get files for each project
    print("\n2. Testing file retrieval for each project...")
    for project in projects:
        project_name = project['name']
        print(f"\n📁 Project: {project_name}")
        
        files = file_manager.get_project_files(project_name)
        print(f"   Found {len(files)} files:")
        
        for file in files:
            print(f"     - {file['name']} ({file['type']}) - {file['size']} bytes")
            if file.get('content'):
                content_preview = file['content'][:100].replace('\n', ' ')
                print(f"       Preview: {content_preview}...")
    
    print("\n" + "=" * 50)
    print("File manager test completed!")

if __name__ == "__main__":
    test_file_manager()

