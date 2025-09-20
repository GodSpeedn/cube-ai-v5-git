"""
Upload to Existing Repository
Uploads generated code to an existing GitHub repository
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from git_agent import git_agent

def list_available_repositories():
    """List available repositories for upload"""
    print("📁 Available repositories for upload:")
    print("=" * 40)
    
    result = git_agent.list_repositories()
    if result["success"]:
        for i, repo in enumerate(result["repositories"], 1):
            print(f"{i:2d}. {repo['name']} ({'private' if repo['private'] else 'public'})")
            print(f"    {repo['html_url']}")
        return result["repositories"]
    else:
        print(f"❌ Failed to list repositories: {result['error']}")
        return []

def upload_to_repository(repo_name: str):
    """Upload generated code to a specific repository"""
    print(f"📤 Uploading to repository: {repo_name}")
    print("=" * 40)
    
    # Generate commit message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"AI Generated Code Update - {timestamp}"
    
    # Upload to existing repository
    result = git_agent.extract_and_push_code(
        repo_name=repo_name,
        commit_message=commit_message,
        auto_create_repo=False  # Don't try to create, use existing
    )
    
    if result["success"]:
        print(f"✅ Upload successful!")
        print(f"   Repository: {result['repository_url']}")
        print(f"   Commit: {result['commit_sha'][:7]}")
        print(f"   Files: {result['files_pushed']} files")
        print(f"   Size: {result['extraction_stats']['total_size']:,} bytes")
        return True
    else:
        print(f"❌ Upload failed: {result['error']}")
        return False

def main():
    """Main function"""
    print("🚀 Upload Generated Code to Existing Repository")
    print("=" * 50)
    
    # Check if GitHub is configured
    if not git_agent.is_configured():
        print("❌ GitHub not configured")
        print("   Run: python configure_github.py")
        return
    
    # List available repositories
    repositories = list_available_repositories()
    if not repositories:
        return
    
    print(f"\n📝 Found {len(repositories)} repositories")
    print("\nOptions:")
    print("1. Enter repository name manually")
    print("2. Select from list by number")
    print("3. Use default repository (cube-ai-assign4)")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        repo_name = input("Enter repository name: ").strip()
        if repo_name:
            upload_to_repository(repo_name)
        else:
            print("❌ No repository name provided")
    
    elif choice == "2":
        try:
            repo_num = int(input(f"Enter repository number (1-{len(repositories)}): "))
            if 1 <= repo_num <= len(repositories):
                repo_name = repositories[repo_num - 1]["name"]
                upload_to_repository(repo_name)
            else:
                print("❌ Invalid repository number")
        except ValueError:
            print("❌ Invalid input")
    
    elif choice == "3":
        upload_to_repository("cube-ai-assign4")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
