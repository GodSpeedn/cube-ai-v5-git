#!/usr/bin/env python3
"""
Test script for improved code saving functionality
"""
import requests
import json
import time
from pathlib import Path

def test_code_saving():
    """Test the improved code saving functionality"""
    print("Testing Improved Code Saving Functionality")
    print("=" * 50)
    
    # Test data
    test_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    """Main function to demonstrate Fibonacci sequence"""
    print("Fibonacci Sequence Generator")
    print("=" * 30)
    
    for i in range(10):
        result = fibonacci(i)
        print(f"F({i}) = {result}")

if __name__ == "__main__":
    main()
'''
    
    test_request = {
        "task": "Create a Fibonacci sequence generator with proper documentation",
        "agents": [
            {
                "id": "coder",
                "name": "Python Developer",
                "role": "Code Generator",
                "model": "gpt-4",
                "system_prompt": "You are a Python developer. Generate clean, well-documented code.",
                "memory_enabled": True
            }
        ],
        "conversation_id": f"test_workflow_{int(time.time())}",
        "enable_streaming": False
    }
    
    print("1. Testing Online Workflow with Code Generation...")
    try:
        # Test the online workflow
        response = requests.post(
            "http://localhost:8001/run-workflow",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Workflow completed successfully")
            print(f"   Workflow ID: {result.get('workflow_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Total Messages: {result.get('total_messages')}")
            
            # Check if code was saved
            if result.get('conversation_id'):
                print(f"   Conversation ID: {result.get('conversation_id')}")
                
                # Check for generated files
                generated_dir = Path("generated")
                if generated_dir.exists():
                    projects = list(generated_dir.glob("projects/*"))
                    if projects:
                        latest_project = max(projects, key=lambda p: p.stat().st_mtime)
                        print(f"   Latest Project: {latest_project.name}")
                        
                        # Check project structure
                        src_files = list(latest_project.glob("src/*.py"))
                        test_files = list(latest_project.glob("tests/*.py"))
                        doc_files = list(latest_project.glob("docs/*.md"))
                        
                        print(f"   Source Files: {len(src_files)}")
                        print(f"   Test Files: {len(test_files)}")
                        print(f"   Documentation: {len(doc_files)}")
                        
                        # Show project structure
                        print(f"\nProject Structure:")
                        for file_path in latest_project.rglob("*"):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(latest_project)
                                print(f"   {rel_path}")
                    else:
                        print("   [WARNING] No projects found in generated directory")
                else:
                    print("   [WARNING] Generated directory not found")
        else:
            print(f"[ERROR] Workflow failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
    
    print("\n2. Testing Direct Code Saving...")
    try:
        # Test direct code saving through main service
        save_request = {
            "code": test_code,
            "filename": "fibonacci_generator.py",
            "file_type": "src",
            "task_description": "Fibonacci sequence generator with documentation",
            "conversation_id": f"test_direct_{int(time.time())}"
        }
        
        response = requests.post(
            "http://localhost:8000/projects/save-code",
            json=save_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Code saved successfully")
            print(f"   File: {result.get('filepath')}")
            print(f"   Project: {result.get('project_name')}")
            
            # Check GitHub upload
            github_result = result.get('github_result', {})
            if github_result.get('status') == 'success':
                print(f"   GitHub: {github_result.get('repo_url')}")
            elif github_result.get('status') == 'github_not_available':
                print(f"   GitHub: Not available (saved locally only)")
            else:
                print(f"   GitHub: {github_result.get('error', 'Unknown issue')}")
        else:
            print(f"[ERROR] Code saving failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Direct save test failed: {e}")
    
    print("\n3. Checking Generated Files...")
    try:
        generated_dir = Path("generated")
        if generated_dir.exists():
            print(f"Generated directory exists: {generated_dir.absolute()}")
            
            # List all projects
            projects = list(generated_dir.glob("projects/*"))
            print(f"   Projects found: {len(projects)}")
            
            for project in projects[-3:]:  # Show last 3 projects
                print(f"\n   Project: {project.name}")
                
                # Check project.json
                project_json = project / "project.json"
                if project_json.exists():
                    with open(project_json, 'r') as f:
                        metadata = json.load(f)
                    print(f"      Task: {metadata.get('task_description', 'N/A')}")
                    print(f"      Created: {metadata.get('created_at', 'N/A')}")
                    print(f"      GitHub: {metadata.get('github_repo', 'Not uploaded')}")
                
                # List files
                for file_type in ["src", "tests", "docs"]:
                    files = list(project.glob(f"{file_type}/*"))
                    if files:
                        print(f"      {file_type}: {len(files)} files")
                        for file_path in files:
                            print(f"         - {file_path.name}")
        else:
            print("[ERROR] Generated directory not found")
            
    except Exception as e:
        print(f"[ERROR] File checking failed: {e}")
    
    print("\n" + "=" * 50)
    print("Code Saving Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_code_saving()