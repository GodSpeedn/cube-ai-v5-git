#!/usr/bin/env python3
"""
Test GitHub auto-upload functionality
"""
import requests
import json
import time
from pathlib import Path

def test_github_auto_upload():
    """Test the GitHub auto-upload functionality"""
    print("Testing GitHub Auto-Upload Functionality")
    print("=" * 50)
    
    # Test 1: Generate code and save it
    print("1. Generating and saving code...")
    test_code = '''
def data_analyzer():
    """Advanced data analysis tool"""
    import pandas as pd
    import numpy as np
    
    def analyze_data(data):
        """Analyze data and return insights"""
        if isinstance(data, list):
            data = pd.Series(data)
        
        analysis = {
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'count': len(data)
        }
        return analysis
    
    def generate_report(data, title="Data Analysis Report"):
        """Generate a comprehensive analysis report"""
        analysis = analyze_data(data)
        
        report = f"""
# {title}

## Summary Statistics
- **Count**: {analysis['count']}
- **Mean**: {analysis['mean']:.2f}
- **Median**: {analysis['median']:.2f}
- **Standard Deviation**: {analysis['std']:.2f}
- **Range**: {analysis['min']:.2f} to {analysis['max']:.2f}

## Data Quality
- **Completeness**: {100 - (data.isnull().sum() / len(data) * 100):.1f}%
- **Outliers**: {len(data[(data < analysis['mean'] - 2*analysis['std']) | (data > analysis['mean'] + 2*analysis['std'])])} detected

## Recommendations
1. Review outliers for data quality issues
2. Consider data transformation if distribution is skewed
3. Validate data collection process
        """
        return report.strip()
    
    return analyze_data, generate_report

if __name__ == "__main__":
    analyzer, reporter = data_analyzer()
    
    # Example usage
    sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 100]
    result = analyzer(sample_data)
    report = reporter(sample_data, "Sample Data Analysis")
    
    print("Analysis Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("\nGenerated Report:")
    print(report)
'''
    
    # Save code through the main service
    save_request = {
        "code": test_code,
        "filename": "data_analyzer.py",
        "file_type": "src",
        "task_description": "Advanced data analysis tool with comprehensive reporting",
        "conversation_id": f"test_github_upload_{int(time.time())}"
    }
    
    try:
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
            
            # Check GitHub upload result
            github_result = result.get('github_result', {})
            if github_result.get('status') == 'success':
                print(f"   GitHub: {github_result.get('repo_url')}")
                print(f"   Repository: {github_result.get('repository_name')}")
                print(f"   Files uploaded: {github_result.get('files_uploaded', 0)}")
            elif github_result.get('status') == 'github_not_available':
                print(f"   GitHub: Not available (saved locally only)")
            else:
                print(f"   GitHub: {github_result.get('error', 'Unknown issue')}")
                
            # Now test manual auto-upload
            print(f"\n2. Testing manual auto-upload...")
            project_name = result.get('project_name')
            if project_name:
                auto_upload_request = {
                    "project_name": project_name,
                    "task_description": "Advanced data analysis tool with comprehensive reporting",
                    "create_new_repo": True
                }
                
                upload_response = requests.post(
                    "http://localhost:8000/git/auto-upload",
                    json=auto_upload_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if upload_response.status_code == 200:
                    upload_result = upload_response.json()
                    if upload_result.get('success'):
                        print(f"[SUCCESS] Manual auto-upload completed")
                        print(f"   Repository: {upload_result.get('repository_url')}")
                        print(f"   Files pushed: {upload_result.get('files_pushed', 0)}")
                        print(f"   Commit SHA: {upload_result.get('commit_sha')}")
                    else:
                        print(f"[ERROR] Manual auto-upload failed: {upload_result.get('error')}")
                else:
                    print(f"[ERROR] Manual auto-upload failed: {upload_response.status_code}")
                    print(f"   Error: {upload_response.text}")
        else:
            print(f"[ERROR] Code saving failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
    
    print("\n3. Checking GitHub repositories...")
    try:
        # Check recent repositories
        git_status_response = requests.get("http://localhost:8000/git/status")
        if git_status_response.status_code == 200:
            git_status = git_status_response.json()
            repositories = git_status.get('repositories', [])
            
            # Find AI-generated repositories
            ai_repos = [repo for repo in repositories if 'ai-generated' in repo.get('name', '').lower()]
            print(f"   Total repositories: {len(repositories)}")
            print(f"   AI-generated repositories: {len(ai_repos)}")
            
            if ai_repos:
                print(f"\n   Recent AI-generated repositories:")
                for repo in ai_repos[-3:]:  # Show last 3
                    print(f"      - {repo['name']}")
                    print(f"        URL: {repo['html_url']}")
                    print(f"        Created: {repo['created_at']}")
                    print(f"        Description: {repo.get('description', 'No description')}")
        else:
            print(f"[ERROR] Could not check GitHub status: {git_status_response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] GitHub check failed: {e}")
    
    print("\n" + "=" * 50)
    print("GitHub Auto-Upload Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_github_auto_upload()


