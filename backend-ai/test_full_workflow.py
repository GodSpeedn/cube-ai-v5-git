#!/usr/bin/env python3
"""
Test the full workflow by calling the online agent service API
"""

import requests
import json
import time

# Test the full workflow
print("[INFO] Testing full online agent workflow...")

# Step 1: Check if service is running
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

# Step 2: Run the workflow directly
print("\n[INFO] Running test workflow...")
workflow_data = {
    "task": "Create a simple Python function that calculates the factorial of a number",
    "agents": [
        {"id": "coder", "role": "coder", "name": "Python Coder"},
        {"id": "tester", "role": "tester", "name": "Test Generator"}
    ],
    "conversation_id": ""  # Empty string to create DB conversation
}

try:
    response = requests.post("http://localhost:8001/run-workflow", json=workflow_data, timeout=60)
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Workflow completed: {result.get('status')}")
        
        # Print the full result to see what we got
        print(f"\n[DEBUG] Full workflow result:")
        print(json.dumps(result, indent=2))
        
        # Check if files were created
        if 'files' in result:
            print(f"\n   Files created: {len(result['files'])}")
            for file_info in result['files']:
                print(f"     - {file_info.get('filename')}: {file_info.get('filepath')}")
        else:
            print("\n   No files found in result")
        
        # Check if GitHub upload happened
        if 'github_repo' in result:
            print(f"\n   GitHub repository: {result['github_repo']}")
        else:
            print("\n   No GitHub repository found")
            
        # Check workflow details
        if 'workflow_id' in result:
            print(f"\n   Workflow ID: {result['workflow_id']}")
            
    else:
        print(f"[ERROR] Failed to run workflow: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"[ERROR] Failed to run workflow: {e}")
    exit(1)

print(f"\n[INFO] Test complete!")
