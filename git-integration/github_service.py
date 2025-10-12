"""
GitHub API service for Git Integration System
Separate from main system to avoid conflicts
"""

import base64
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class GitHubFile(BaseModel):
    """Represents a file to be uploaded to GitHub"""
    path: str
    content: str
    message: str = "Add file"

class GitHubRepository(BaseModel):
    """Represents a GitHub repository"""
    name: str
    description: str = ""
    private: bool = False
    auto_init: bool = True
    gitignore_template: str = "Python"

class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Assistant-Git-Integration"
        }
    
    def validate_token(self) -> Dict[str, Any]:
        """Validate the GitHub token and get user info"""
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "user": {
                        "login": user_data.get("login"),
                        "name": user_data.get("name"),
                        "email": user_data.get("email")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Token validation failed: {str(e)}"
            }
    
    def create_repository(self, repo: GitHubRepository) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        try:
            payload = {
                "name": repo.name,
                "description": repo.description,
                "private": repo.private,
                "auto_init": repo.auto_init,
                "gitignore_template": repo.gitignore_template
            }
            
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                return {
                    "success": True,
                    "repository": {
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "html_url": repo_data["html_url"],
                        "clone_url": repo_data["clone_url"],
                        "ssh_url": repo_data["ssh_url"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Repository creation failed: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Repository creation failed: {str(e)}"
            }
    
    def list_repositories(self) -> Dict[str, Any]:
        """List all repositories for the authenticated user"""
        try:
            response = requests.get(f"{self.base_url}/user/repos", headers=self.headers)
            
            if response.status_code == 200:
                repos_data = response.json()
                repositories = []
                
                for repo in repos_data:
                    repositories.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "description": repo["description"],
                        "private": repo["private"],
                        "html_url": repo["html_url"],
                        "created_at": repo["created_at"],
                        "updated_at": repo["updated_at"]
                    })
                
                return {
                    "success": True,
                    "repositories": repositories,
                    "count": len(repositories)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to list repositories: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list repositories: {str(e)}"
            }
    
    def get_repository(self, repo_name: str) -> Dict[str, Any]:
        """Get information about a specific repository"""
        try:
            url = f"{self.base_url}/repos/{self.username}/{repo_name}"
            print(f"[GITHUB_SERVICE] get_repository URL: {url}")
            response = requests.get(url, headers=self.headers)
            print(f"[GITHUB_SERVICE] get_repository status: {response.status_code}")
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "success": True,
                    "repository": {
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "description": repo_data["description"],
                        "private": repo_data["private"],
                        "html_url": repo_data["html_url"],
                        "clone_url": repo_data["clone_url"],
                        "ssh_url": repo_data["ssh_url"],
                        "created_at": repo_data["created_at"],
                        "updated_at": repo_data["updated_at"],
                        "default_branch": repo_data["default_branch"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Repository not found: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get repository: {str(e)}"
            }
    
    def push_files(self, repo_name: str, files: List[GitHubFile], 
                   commit_message: str = None) -> Dict[str, Any]:
        """Push files to a GitHub repository using Git Tree API"""
        try:
            print(f"[GITHUB_SERVICE] push_files called with repo_name: {repo_name}")
            print(f"[GITHUB_SERVICE] Number of files: {len(files)}")
            
            if not commit_message:
                commit_message = f"AI Generated: {len(files)} files - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Get repository info
            print(f"[GITHUB_SERVICE] Getting repository info for: {repo_name}")
            repo_info = self.get_repository(repo_name)
            print(f"[GITHUB_SERVICE] get_repository success: {repo_info.get('success')}")
            if not repo_info["success"]:
                print(f"[GITHUB_SERVICE] get_repository failed: {repo_info.get('error')}")
                return repo_info
            
            default_branch = repo_info["repository"]["default_branch"]
            
            # Get the latest commit
            ref_response = requests.get(
                f"{self.base_url}/repos/{self.username}/{repo_name}/git/refs/heads/{default_branch}",
                headers=self.headers
            )
            
            if ref_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get branch reference: {ref_response.status_code}",
                    "details": ref_response.text
                }
            
            latest_commit_sha = ref_response.json()["object"]["sha"]
            
            # Get the commit details
            commit_response = requests.get(
                f"{self.base_url}/repos/{self.username}/{repo_name}/git/commits/{latest_commit_sha}",
                headers=self.headers
            )
            
            if commit_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get commit details: {commit_response.status_code}",
                    "details": commit_response.text
                }
            
            base_tree_sha = commit_response.json()["tree"]["sha"]
            
            # Create blobs for each file
            tree_items = []
            for file in files:
                # Create blob
                blob_payload = {
                    "content": base64.b64encode(file.content.encode('utf-8')).decode('utf-8'),
                    "encoding": "base64"
                }
                
                blob_response = requests.post(
                    f"{self.base_url}/repos/{self.username}/{repo_name}/git/blobs",
                    headers=self.headers,
                    json=blob_payload
                )
                
                if blob_response.status_code == 201:
                    blob_sha = blob_response.json()["sha"]
                    tree_items.append({
                        "path": file.path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_sha
                    })
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create blob for {file.path}: {blob_response.status_code}",
                        "details": blob_response.text
                    }
            
            # Create new tree
            tree_payload = {
                "base_tree": base_tree_sha,
                "tree": tree_items
            }
            
            tree_response = requests.post(
                f"{self.base_url}/repos/{self.username}/{repo_name}/git/trees",
                headers=self.headers,
                json=tree_payload
            )
            
            if tree_response.status_code != 201:
                return {
                    "success": False,
                    "error": f"Failed to create tree: {tree_response.status_code}",
                    "details": tree_response.text
                }
            
            new_tree_sha = tree_response.json()["sha"]
            
            # Create new commit
            commit_payload = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [latest_commit_sha]
            }
            
            commit_response = requests.post(
                f"{self.base_url}/repos/{self.username}/{repo_name}/git/commits",
                headers=self.headers,
                json=commit_payload
            )
            
            if commit_response.status_code != 201:
                return {
                    "success": False,
                    "error": f"Failed to create commit: {commit_response.status_code}",
                    "details": commit_response.text
                }
            
            new_commit_sha = commit_response.json()["sha"]
            
            # Update branch reference
            ref_payload = {"sha": new_commit_sha}
            ref_response = requests.patch(
                f"{self.base_url}/repos/{self.username}/{repo_name}/git/refs/heads/{default_branch}",
                headers=self.headers,
                json=ref_payload
            )
            
            if ref_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to update branch reference: {ref_response.status_code}",
                    "details": ref_response.text
                }
            
            return {
                "success": True,
                "commit_sha": new_commit_sha,
                "tree_sha": new_tree_sha,
                "files_pushed": len(files),
                "repository_url": f"https://github.com/{self.username}/{repo_name}",
                "commit_message": commit_message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to push files: {str(e)}"
            }
    
    def delete_repository(self, repo_name: str) -> Dict[str, Any]:
        """Delete a repository (use with caution!)"""
        try:
            response = requests.delete(
                f"{self.base_url}/repos/{self.username}/{repo_name}",
                headers=self.headers
            )
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": f"Repository '{repo_name}' deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to delete repository: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete repository: {str(e)}"
            }
