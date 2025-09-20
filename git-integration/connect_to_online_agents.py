"""
Connect Online Manual Agents to GitHub Upload
Shows how to integrate the online manual agents with GitHub upload
"""

import os
import sys
import asyncio
import requests
from pathlib import Path
from typing import Dict, Any

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from online_agent_github_integration import online_agent_github

def test_online_agent_connection():
    """Test connection to online manual agents"""
    print("🔗 Testing connection to online manual agents...")
    
    try:
        # Test connection to main backend
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Main backend is running")
            return True
        else:
            print(f"❌ Main backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to main backend: {e}")
        print("   Make sure the main backend is running on http://localhost:8000")
        return False

def test_github_integration():
    """Test GitHub integration"""
    print("🐙 Testing GitHub integration...")
    
    if not online_agent_github.is_configured():
        print("❌ GitHub not configured")
        print("   Run: python configure_github.py")
        return False
    
    print("✅ GitHub is configured")
    return True

async def upload_latest_workflow():
    """Upload the latest workflow results to GitHub"""
    print("📤 Uploading latest workflow results to GitHub...")
    
    try:
        result = await online_agent_github.upload_latest_generated_code()
        
        if result["success"]:
            print(f"✅ Upload successful!")
            print(f"   Repository: {result['repository_url']}")
            print(f"   Commit: {result['commit_sha'][:7]}")
            print(f"   Files: {result['files_pushed']} files")
            return True
        else:
            print(f"❌ Upload failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def show_integration_flow():
    """Show how the integration works"""
    print("🔄 Online Manual Agents → GitHub Upload Flow:")
    print("=" * 50)
    print("1. 🌐 Online Manual Agents generate code")
    print("   - Code is saved to: backend-ai/generated/")
    print("   - Files like: code_*.py, test_*.py")
    print()
    print("2. 🔍 Git Integration System reads generated files")
    print("   - Scans: backend-ai/generated/ directory")
    print("   - Filters: Python files, excludes cache/temp files")
    print("   - Creates: README.md automatically")
    print()
    print("3. 🐙 GitHub Upload")
    print("   - Creates: New repository on GitHub")
    print("   - Pushes: All generated files")
    print("   - Returns: Repository URL and commit info")
    print()
    print("4. 🎯 Result")
    print("   - Your code is now on GitHub!")
    print("   - Shareable repository with README")
    print("   - Version controlled and backed up")

def show_usage_examples():
    """Show usage examples"""
    print("📝 Usage Examples:")
    print("=" * 30)
    print()
    print("1. 🔧 Configure GitHub:")
    print("   python configure_github.py")
    print()
    print("2. 🧪 Test the system:")
    print("   python test_integration.py")
    print()
    print("3. 📤 Upload latest code:")
    print("   python connect_to_online_agents.py")
    print()
    print("4. 🌐 Use from online agents:")
    print("   # In your online agent workflow:")
    print("   import requests")
    print("   response = requests.post('http://localhost:8002/upload')")
    print("   print(response.json())")

async def main():
    """Main function"""
    print("🚀 Online Manual Agents → GitHub Integration")
    print("=" * 50)
    
    # Show integration flow
    show_integration_flow()
    print()
    
    # Test connections
    print("🧪 Testing connections...")
    backend_ok = test_online_agent_connection()
    github_ok = test_github_integration()
    
    if not backend_ok:
        print("\n❌ Cannot proceed without main backend")
        print("   Start the main backend: cd ../backend-ai && python main.py")
        return
    
    if not github_ok:
        print("\n❌ Cannot proceed without GitHub configuration")
        print("   Configure GitHub: python configure_github.py")
        return
    
    # Upload latest code
    print("\n📤 Uploading latest generated code...")
    success = await upload_latest_workflow()
    
    if success:
        print("\n🎉 Integration successful!")
        print("   Your online manual agents can now upload to GitHub!")
    else:
        print("\n⚠️ Upload failed, but integration is ready")
        print("   Check your GitHub configuration and try again")
    
    # Show usage examples
    print("\n" + "=" * 50)
    show_usage_examples()

if __name__ == "__main__":
    asyncio.run(main())
