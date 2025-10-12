#!/usr/bin/env python3
"""
Test script to verify auto-upload functionality
"""

import requests
import json

def test_auto_upload():
    """Test the auto-upload functionality"""
    
    # Test data
    test_data = {
        "code": 'print("Hello World")\nprint("This is a test")\nprint("Auto-upload test")',
        "task_description": "Test Auto-Upload Functionality",
        "filename": "test_auto_upload.py"
    }
    
    print("🧪 Testing auto-upload functionality...")
    print(f"📝 Test data: {test_data['task_description']}")
    
    try:
        # Test the save-code endpoint
        response = requests.post('http://localhost:8000/projects/save-code', json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code saved successfully!")
            print(f"📁 Project: {result.get('result', {}).get('project_name', 'Unknown')}")
            print(f"📄 File: {result.get('result', {}).get('filepath', 'Unknown')}")
            
            # Print full result for debugging
            print(f"🔍 Full result: {json.dumps(result, indent=2)}")
            
            # Check GitHub result
            github_result = result.get('result', {}).get('github_result', {})
            if github_result.get('status') == 'success':
                print(f"🐙 GitHub Upload: SUCCESS")
                print(f"🔗 Repository: {github_result.get('repo_url', 'Unknown')}")
                print(f"📊 Files uploaded: {github_result.get('files_uploaded', 0)}")
            elif github_result.get('status') == 'github_not_available':
                print("ℹ️ GitHub not available - code saved locally only")
            else:
                print(f"⚠️ GitHub upload issue: {github_result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_auto_upload()
