#!/usr/bin/env python3
"""
Detailed test to see what's happening in the workflow
"""

import requests
import json

print("[INFO] Running detailed workflow test...")

# Test with a coder agent that should trigger code saving
workflow_data = {
    "task": "Write a Python function to add two numbers",
    "agents": [
        {"id": "coder1", "role": "coder", "name": "Python Coder", "model": "gpt-3.5-turbo"}
    ],
    "conversation_id": ""
}

print(f"[INFO] Sending workflow request...")
print(f"   Task: {workflow_data['task']}")
print(f"   Agents: {len(workflow_data['agents'])}")

try:
    response = requests.post("http://localhost:8001/run-workflow", json=workflow_data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[OK] Workflow completed!")
        print(f"   Status: {result.get('status')}")
        print(f"   Workflow ID: {result.get('workflow_id')}")
        print(f"   Total messages: {result.get('total_messages')}")
        
        # Check GitHub upload status
        if 'github_upload' in result:
            github_upload = result['github_upload']
            print(f"\n[INFO] GitHub Upload Status:")
            print(f"   Uploaded: {github_upload.get('uploaded')}")
            if github_upload.get('uploaded'):
                print(f"   Repository URL: {github_upload.get('repo_url')}")
                print(f"   Files uploaded: {github_upload.get('files_uploaded')}")
                print(f"\n[SUCCESS] GitHub auto-upload is working!")
            else:
                print(f"   Repo URL: {github_upload.get('repo_url')}")
                print(f"\n[WARN] GitHub upload did not happen")
                print(f"[INFO] This means _save_generated_code was not called or failed")
        else:
            print(f"\n[ERROR] No github_upload field in response")
        
        # Check messages
        print(f"\n[INFO] Messages:")
        for i, msg in enumerate(result.get('message_history', [])):
            print(f"  {i+1}. {msg['from_agent']} -> {msg['to_agent']}")
            print(f"     Content preview: {msg['content'][:100]}...")
            if 'CODE COMPLETE' in msg['content']:
                print(f"     [INFO] Contains CODE COMPLETE signal")
            if '```python' in msg['content']:
                print(f"     [INFO] Contains Python code block")
                
    else:
        print(f"[ERROR] Request failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n[INFO] Test complete!")

