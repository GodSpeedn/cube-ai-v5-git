#!/usr/bin/env python3
"""
Test script to verify frontend integration with file manager
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from file_manager import file_manager

async def test_frontend_integration():
    """Test the frontend integration"""
    print("🧪 Testing Frontend Integration")
    print("=" * 50)
    
    # Test 1: Create a test project with files
    print("\n1. Creating test project...")
    test_code = '''
def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
    
    # Save code to create a project
    result = file_manager.save_code(
        code=test_code,
        filename="test_hello.py",
        file_type="src",
        conversation_id="test_frontend_integration",
        task_description="Test frontend integration"
    )
    
    if result.get("success"):
        print(f"✅ Test project created: {result.get('project_name')}")
        project_name = result.get('project_name')
    else:
        print(f"❌ Failed to create test project: {result.get('error')}")
        return
    
    # Test 2: List projects (simulating frontend call)
    print("\n2. Testing project listing...")
    projects = file_manager.list_projects()
    print(f"✅ Found {len(projects)} projects")
    
    # Find our test project
    test_project = None
    for project in projects:
        if project['name'] == project_name:
            test_project = project
            break
    
    if not test_project:
        print(f"❌ Test project not found in list")
        return
    
    print(f"✅ Test project found: {test_project['name']}")
    
    # Test 3: Get project files (simulating frontend call)
    print("\n3. Testing file retrieval...")
    files = file_manager.get_project_files(project_name)
    print(f"✅ Found {len(files)} files in project")
    
    for file in files:
        print(f"   - {file['name']} ({file['type']}) - {file['size']} bytes")
        if file.get('content'):
            content_preview = file['content'][:50].replace('\n', ' ')
            print(f"     Content preview: {content_preview}...")
    
    # Test 4: Check project structure
    print("\n4. Checking project structure...")
    project_dir = Path("generated/projects") / project_name
    if project_dir.exists():
        print(f"✅ Project directory exists: {project_dir}")
        
        # Check subdirectories
        for subdir in ["src", "tests", "docs"]:
            subdir_path = project_dir / subdir
            if subdir_path.exists():
                files_in_subdir = list(subdir_path.glob("*"))
                print(f"   - {subdir}/: {len(files_in_subdir)} files")
                for file in files_in_subdir:
                    if file.is_file():
                        print(f"     - {file.name}")
            else:
                print(f"   - {subdir}/: (not found)")
    else:
        print(f"❌ Project directory not found: {project_dir}")
    
    print("\n" + "=" * 50)
    print("Frontend integration test completed!")
    print(f"Test project: {project_name}")
    print("You can now test the frontend with this project.")

if __name__ == "__main__":
    asyncio.run(test_frontend_integration())

