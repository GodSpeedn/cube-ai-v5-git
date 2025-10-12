#!/usr/bin/env python3
"""
Test script to verify code saving functionality
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from online_agent_service import OnlineAgent, OnlineWorkflowRequest, OnlineWorkflowManager
from file_manager import file_manager

async def test_code_saving():
    """Test the code saving functionality"""
    print("🧪 Testing Code Saving Functionality")
    print("=" * 50)
    
    # Test 1: Direct file manager save
    print("\n1. Testing direct file manager save...")
    test_code = '''
def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
    
    result = file_manager.save_code(
        code=test_code,
        filename="test_hello.py",
        file_type="src",
        conversation_id="test_conversation",
        task_description="Test code saving functionality"
    )
    
    if result.get("success"):
        print(f"✅ Code saved successfully!")
        print(f"   File: {result.get('filepath')}")
        print(f"   Project: {result.get('project_name')}")
        github_result = result.get("github_result", {})
        if github_result.get("status") == "success":
            print(f"   GitHub: {github_result.get('repo_url')}")
        else:
            print(f"   GitHub: {github_result.get('status')} - {github_result.get('message', 'No message')}")
    else:
        print(f"❌ Failed to save code: {result.get('error')}")
    
    # Test 2: Online agent workflow
    print("\n2. Testing online agent workflow...")
    
    # Create a coder agent
    coder_agent = OnlineAgent(
        id="test_coder",
        name="Test Coder",
        role="coder",
        model="gemini-pro",
        system_prompt="You are a Python developer. Write clean, working Python code."
    )
    
    # Create workflow request
    workflow_request = OnlineWorkflowRequest(
        task="Create a simple calculator function that adds two numbers",
        agents=[coder_agent],
        conversation_id="test_workflow"
    )
    
    # Create workflow manager
    workflow_manager = OnlineWorkflowManager()
    
    try:
        response = await workflow_manager.run_workflow(workflow_request)
        print(f"✅ Workflow completed!")
        print(f"   Status: {response.status}")
        print(f"   Messages: {response.total_messages}")
        print(f"   Conversation ID: {response.conversation_id}")
        
        # Check if files were created
        generated_dir = Path("generated")
        if generated_dir.exists():
            projects_dir = generated_dir / "projects"
            if projects_dir.exists():
                project_dirs = list(projects_dir.iterdir())
                print(f"   Projects created: {len(project_dirs)}")
                for project_dir in project_dirs:
                    if project_dir.is_dir():
                        print(f"     - {project_dir.name}")
                        src_dir = project_dir / "src"
                        if src_dir.exists():
                            src_files = list(src_dir.glob("*.py"))
                            print(f"       Python files: {len(src_files)}")
                            for file in src_files:
                                print(f"         - {file.name}")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_code_saving())
