"""
Test script for Git Integration System
Tests the integration without affecting the main system
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from git_agent import git_agent
from config import config

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    print(f"  GitHub configured: {config.is_github_configured()}")
    print(f"  Generated dir: {config.get_generated_dir()}")
    print(f"  Output dir: {config.get_output_dir()}")
    print(f"  Include patterns: {config.include_patterns}")
    print(f"  Exclude patterns: {config.exclude_patterns}")
    print()

def test_code_extraction():
    """Test code extraction from main system"""
    print("🔍 Testing Code Extraction...")
    
    # Check if generated directory exists
    generated_dir = config.get_generated_dir()
    if not generated_dir.exists():
        print(f"  ❌ Generated directory does not exist: {generated_dir}")
        return False
    
    # List files in generated directory
    files = list(generated_dir.glob("*"))
    print(f"  📁 Found {len(files)} files in generated directory")
    
    for file in files[:5]:  # Show first 5 files
        print(f"    - {file.name} ({file.stat().st_size} bytes)")
    
    if len(files) > 5:
        print(f"    ... and {len(files) - 5} more files")
    
    # Test extraction
    result = git_agent.preview_extractable_code()
    if result["success"]:
        print(f"  ✅ Extraction preview successful")
        print(f"    - {result['stats']['total_files']} files can be extracted")
        print(f"    - Total size: {result['stats']['total_size']:,} bytes")
        print(f"    - Languages: {', '.join(result['stats']['languages'])}")
        return True
    else:
        print(f"  ❌ Extraction preview failed: {result['error']}")
        return False

def test_github_configuration():
    """Test GitHub configuration"""
    print("🐙 Testing GitHub Configuration...")
    
    if not config.is_github_configured():
        print("  ⚠️ GitHub not configured")
        print("  To configure GitHub:")
        print("    1. Set GITHUB_TOKEN environment variable")
        print("    2. Set GITHUB_USERNAME environment variable")
        print("    3. Optionally set GITHUB_EMAIL environment variable")
        return False
    
    # Test token validation
    if git_agent.github_service:
        result = git_agent.github_service.validate_token()
        if result["success"]:
            print(f"  ✅ GitHub token valid")
            print(f"    - User: {result['user']['login']}")
            print(f"    - Name: {result['user']['name']}")
            return True
        else:
            print(f"  ❌ GitHub token invalid: {result['error']}")
            return False
    else:
        print("  ❌ GitHub service not initialized")
        return False

def test_repository_operations():
    """Test repository operations (read-only)"""
    print("📁 Testing Repository Operations...")
    
    if not git_agent.is_configured():
        print("  ⚠️ GitHub not configured, skipping repository tests")
        return False
    
    # List repositories
    result = git_agent.list_repositories()
    if result["success"]:
        print(f"  ✅ Repository listing successful")
        print(f"    - Found {result['count']} repositories")
        
        # Show first few repositories
        for repo in result["repositories"][:3]:
            print(f"    - {repo['name']} ({'private' if repo['private'] else 'public'})")
        
        if result["count"] > 3:
            print(f"    ... and {result['count'] - 3} more repositories")
        
        return True
    else:
        print(f"  ❌ Repository listing failed: {result['error']}")
        return False

def test_full_integration():
    """Test full integration (extract and push) - DRY RUN"""
    print("🚀 Testing Full Integration (DRY RUN)...")
    
    if not git_agent.is_configured():
        print("  ⚠️ GitHub not configured, skipping integration test")
        return False
    
    # Test extraction only (no push)
    result = git_agent.extract_latest_code(limit=5)
    if result["success"]:
        print(f"  ✅ Code extraction successful")
        print(f"    - Extracted {result['stats']['total_files']} files")
        print(f"    - Total size: {result['stats']['total_size']:,} bytes")
        
        # Show extracted files
        for file in result["files"]:
            print(f"    - {file.path} ({file.language}, {file.size} bytes)")
        
        print("  📝 To actually push to GitHub, run:")
        print("     git_agent.extract_and_push_code('test-repo-name')")
        return True
    else:
        print(f"  ❌ Code extraction failed: {result['error']}")
        return False

def main():
    """Run all tests"""
    print("🧪 Git Integration System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Code Extraction", test_code_extraction),
        ("GitHub Configuration", test_github_configuration),
        ("Repository Operations", test_repository_operations),
        ("Full Integration", test_full_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Git integration system is ready.")
    else:
        print("⚠️ Some tests failed. Check configuration and try again.")
    
    print("\n📝 Next Steps:")
    print("  1. Configure GitHub credentials if not already done")
    print("  2. Run: git_agent.extract_and_push_code('your-repo-name')")
    print("  3. Check your GitHub account for the new repository")

if __name__ == "__main__":
    main()
