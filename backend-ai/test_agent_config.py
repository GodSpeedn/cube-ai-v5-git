#!/usr/bin/env python3
"""
Test agent configuration to see if roles are set correctly
"""

import requests
import json

# Test agent configuration
print("[INFO] Testing agent configuration...")

# Check if service is running
try:
    response = requests.get("http://localhost:8001/health", timeout=5)
    if response.status_code == 200:
        print("[OK] Online agent service is running")
    else:
        print(f"[ERROR] Service returned status {response.status_code}")
        exit(1)
except Exception as e:
    print(f"[ERROR] Cannot connect to service: {e}")
    exit(1)

# Test with a simple workflow that should trigger code saving
print("\n[INFO] Running simple workflow to test agent configuration...")
workflow_data = {
    "task": "Write a simple hello world function in Python",
    "agents": [
        {"id": "coder", "role": "coder", "name": "Python Coder", "model": "gpt-4"}
    ],
    "conversation_id": ""  # Empty string to create DB conversation
}

try:
    response = requests.post("http://localhost:8001/run-workflow", json=workflow_data, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Workflow completed: {result.get('status')}")
        
        # Check the message history to see what the agent actually said
        if 'message_history' in result:
            print(f"\n[DEBUG] Message history:")
            for i, msg in enumerate(result['message_history']):
                print(f"  Message {i+1}:")
                print(f"    From: {msg.get('from_agent')}")
                print(f"    To: {msg.get('to_agent')}")
                print(f"    Type: {msg.get('message_type')}")
                print(f"    Content: {msg.get('content', '')[:200]}...")
                print()
        
        # Check if files were created
        if 'files' in result:
            print(f"   Files created: {len(result['files'])}")
            for file_info in result['files']:
                print(f"     - {file_info.get('filename')}: {file_info.get('filepath')}")
        else:
            print("   No files found in result")
        
        # Check if GitHub upload happened
        if 'github_upload' in result:
            github_upload = result['github_upload']
            if github_upload.get('uploaded'):
                print(f"   GitHub repository: {github_upload.get('repo_url')}")
                print(f"   Files uploaded: {github_upload.get('files_uploaded')}")
            else:
                print("   GitHub upload: Not uploaded")
        elif 'github_repo' in result:
            print(f"   GitHub repository: {result['github_repo']}")
        else:
            print("   No GitHub upload information found")
            
    else:
        print(f"[ERROR] Failed to run workflow: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"[ERROR] Failed to run workflow: {e}")
    exit(1)

print(f"\n[INFO] Test complete!")
