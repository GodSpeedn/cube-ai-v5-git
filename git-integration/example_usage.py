"""
Example usage of Git Integration System
Shows how to use the system to extract and push code to GitHub
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from git_agent import git_agent

def example_configure_github():
    """Example: Configure GitHub integration"""
    print("🔧 Configuring GitHub...")
    
    # You can set these as environment variables or pass them directly
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME")
    email = os.getenv("GITHUB_EMAIL")
    
    if not token or not username:
        print("❌ Please set GITHUB_TOKEN and GITHUB_USERNAME environment variables")
        print("   Example:")
        print("   export GITHUB_TOKEN=ghp_your_token_here")
        print("   export GITHUB_USERNAME=your_username")
        return False
    
    result = git_agent.configure_github(token, username, email)
    if result["success"]:
        print(f"✅ GitHub configured successfully for user: {result['user']['login']}")
        return True
    else:
        print(f"❌ GitHub configuration failed: {result['error']}")
        return False

def example_preview_code():
    """Example: Preview extractable code"""
    print("🔍 Previewing extractable code...")
    
    result = git_agent.preview_extractable_code()
    if result["success"]:
        print(f"✅ Found {result['stats']['total_files']} files to extract")
        print(f"   Total size: {result['stats']['total_size']:,} bytes")
        print(f"   Languages: {', '.join(result['stats']['languages'])}")
        
        print("\n📁 Files that will be extracted:")
        for file in result["files"][:10]:  # Show first 10 files
            print(f"   - {file['path']} ({file['language']}, {file['size']} bytes)")
        
        if len(result["files"]) > 10:
            print(f"   ... and {len(result['files']) - 10} more files")
        
        return True
    else:
        print(f"❌ Preview failed: {result['error']}")
        return False

def example_extract_latest():
    """Example: Extract latest code files"""
    print("📦 Extracting latest code files...")
    
    result = git_agent.extract_latest_code(limit=5)
    if result["success"]:
        print(f"✅ Extracted {result['stats']['total_files']} latest files")
        
        for file in result["files"]:
            print(f"   - {file.path} ({file.language}, {file.size} bytes)")
        
        return True
    else:
        print(f"❌ Extraction failed: {result['error']}")
        return False

def example_list_repositories():
    """Example: List GitHub repositories"""
    print("📁 Listing GitHub repositories...")
    
    result = git_agent.list_repositories()
    if result["success"]:
        print(f"✅ Found {result['count']} repositories")
        
        for repo in result["repositories"][:5]:  # Show first 5
            print(f"   - {repo['name']} ({'private' if repo['private'] else 'public'})")
            print(f"     {repo['html_url']}")
        
        if result["count"] > 5:
            print(f"   ... and {result['count'] - 5} more repositories")
        
        return True
    else:
        print(f"❌ Repository listing failed: {result['error']}")
        return False

def example_extract_and_push():
    """Example: Extract and push code to GitHub"""
    print("🚀 Extracting and pushing code to GitHub...")
    
    # Generate a unique repository name
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    repo_name = f"ai-generated-{timestamp}"
    
    print(f"📁 Repository name: {repo_name}")
    
    result = git_agent.extract_and_push_code(
        repo_name=repo_name,
        commit_message=f"AI Generated Code - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        auto_create_repo=True
    )
    
    if result["success"]:
        print(f"✅ Successfully pushed code to GitHub!")
        print(f"   Repository: {result['repository_url']}")
        print(f"   Commit: {result['commit_sha'][:7]}")
        print(f"   Files: {result['files_pushed']} files pushed")
        print(f"   Size: {result['extraction_stats']['total_size']:,} bytes")
        return True
    else:
        print(f"❌ Push failed: {result['error']}")
        return False

def main():
    """Run example usage"""
    print("📚 Git Integration System - Example Usage")
    print("=" * 50)
    
    # Check if GitHub is configured
    if not git_agent.is_configured():
        print("⚠️ GitHub not configured. Running configuration example...")
        if not example_configure_github():
            print("\n❌ Cannot proceed without GitHub configuration")
            return
    
    print("\n1. Previewing extractable code...")
    example_preview_code()
    
    print("\n2. Extracting latest code files...")
    example_extract_latest()
    
    print("\n3. Listing repositories...")
    example_list_repositories()
    
    print("\n4. Extracting and pushing to GitHub...")
    print("   (This will create a new repository and push code)")
    
    # Ask for confirmation
    response = input("\n   Do you want to proceed with pushing to GitHub? (y/N): ")
    if response.lower() in ['y', 'yes']:
        example_extract_and_push()
    else:
        print("   Skipping push to GitHub")
    
    print("\n🎉 Example usage completed!")
    print("\n📝 To use this system in your own code:")
    print("   from git_agent import git_agent")
    print("   result = git_agent.extract_and_push_code('my-repo-name')")

if __name__ == "__main__":
    main()
