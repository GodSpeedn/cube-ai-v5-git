"""
Main Git Integration Agent
Combines code extraction and GitHub operations
Separate from main system to avoid conflicts
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from config import config
from code_extractor import CodeExtractor, ExtractedFile
from github_service import GitHubService, GitHubFile, GitHubRepository

class GitIntegrationAgent:
    """Main agent for Git integration operations"""
    
    def __init__(self):
        self.config = config
        self.github_service = None
        self.code_extractor = None
        
        # Initialize services if configured
        if self.config.is_github_configured():
            self.github_service = GitHubService(
                token=self.config.github_token,
                username=self.config.github_username
            )
        
        # Initialize code extractor
        self.code_extractor = CodeExtractor(
            generated_dir=self.config.get_generated_dir(),
            output_dir=self.config.get_output_dir()
        )
    
    def is_configured(self) -> bool:
        """Check if the agent is properly configured"""
        return self.config.is_github_configured()
    
    def configure_github(self, token: str, username: str, email: str = None) -> Dict[str, Any]:
        """Configure GitHub integration"""
        try:
            # Create temporary service to validate
            temp_service = GitHubService(token, username)
            validation_result = temp_service.validate_token()
            
            if validation_result["success"]:
                # Update config
                self.config.github_token = token
                self.config.github_username = username
                if email:
                    self.config.github_email = email
                
                # Initialize service
                self.github_service = temp_service
                
                return {
                    "success": True,
                    "message": "GitHub configured successfully",
                    "user": validation_result["user"]
                }
            else:
                return validation_result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Configuration failed: {str(e)}"
            }
    
    def extract_and_push_code(self, repo_name: str, commit_message: str = None,
                             auto_create_repo: bool = True, 
                             include_patterns: List[str] = None,
                             exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Extract code from main system and push to GitHub
        
        Args:
            repo_name: Name of the repository
            commit_message: Commit message
            auto_create_repo: Whether to create repository if it doesn't exist
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            
        Returns:
            Result of the operation
        """
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "GitHub not configured. Please configure GitHub first."
                }
            
            # Step 1: Extract code
            print(f"🔍 Extracting code from {self.config.get_generated_dir()}")
            extraction_result = self.code_extractor.extract_all_files(
                include_patterns, exclude_patterns
            )
            
            if not extraction_result["success"]:
                return extraction_result
            
            extracted_files = extraction_result["files"]
            print(f"✅ Extracted {len(extracted_files)} files")
            
            # Step 2: Create README
            readme_content = self.code_extractor.create_readme(extracted_files, repo_name)
            readme_file = ExtractedFile(
                path="README.md",
                content=readme_content,
                language="markdown",
                size=len(readme_content),
                created_at=datetime.now().isoformat(),
                source_file="generated"
            )
            extracted_files.append(readme_file)
            
            # Step 3: Convert to GitHub files
            github_files = []
            for file in extracted_files:
                github_file = GitHubFile(
                    path=file.path,
                    content=file.content,
                    message=f"Add {file.path}"
                )
                github_files.append(github_file)
            
            # Step 4: Create repository if needed
            if auto_create_repo:
                print(f"📁 Creating repository: {repo_name}")
                repo = GitHubRepository(
                    name=repo_name,
                    description=f"AI Generated Project - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    private=self.config.default_private,
                    auto_init=self.config.auto_init,
                    gitignore_template=self.config.gitignore_template
                )
                
                create_result = self.github_service.create_repository(repo)
                if not create_result["success"]:
                    # Repository might already exist, continue with push
                    print(f"⚠️ Repository creation failed (might already exist): {create_result.get('error')}")
                else:
                    print(f"✅ Repository created: {create_result['repository']['html_url']}")
            
            # Step 5: Push files
            print(f"🚀 Pushing {len(github_files)} files to GitHub")
            push_result = self.github_service.push_files(
                repo_name=repo_name,
                files=github_files,
                commit_message=commit_message
            )
            
            if push_result["success"]:
                return {
                    "success": True,
                    "repository_url": push_result["repository_url"],
                    "commit_sha": push_result["commit_sha"],
                    "files_pushed": push_result["files_pushed"],
                    "extraction_stats": extraction_result["stats"],
                    "message": f"Successfully pushed {push_result['files_pushed']} files to {repo_name}"
                }
            else:
                return push_result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Extract and push failed: {str(e)}"
            }
    
    def extract_latest_code(self, limit: int = 10) -> Dict[str, Any]:
        """Extract only the latest generated code files"""
        try:
            result = self.code_extractor.extract_latest_files(limit)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Latest code extraction failed: {str(e)}"
            }
    
    def preview_extractable_code(self) -> Dict[str, Any]:
        """Preview what code can be extracted without actually extracting"""
        try:
            result = self.code_extractor.extract_all_files()
            if result["success"]:
                # Return summary without full content
                files_summary = []
                for file in result["files"]:
                    files_summary.append({
                        "path": file.path,
                        "language": file.language,
                        "size": file.size,
                        "created_at": file.created_at
                    })
                
                return {
                    "success": True,
                    "files": files_summary,
                    "stats": result["stats"]
                }
            else:
                return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Preview failed: {str(e)}"
            }
    
    def list_repositories(self) -> Dict[str, Any]:
        """List all GitHub repositories"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "GitHub not configured"
                }
            
            return self.github_service.list_repositories()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list repositories: {str(e)}"
            }
    
    def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """Get information about a specific repository"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "GitHub not configured"
                }
            
            return self.github_service.get_repository(repo_name)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get repository info: {str(e)}"
            }
    
    def quick_extract_and_push(self, repo_name: str = None) -> Dict[str, Any]:
        """Quick extract and push with automatic naming"""
        try:
            if not repo_name:
                # Generate automatic name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                repo_name = f"ai-generated-{timestamp}"
            
            return self.extract_and_push_code(
                repo_name=repo_name,
                commit_message=f"AI Generated Code - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                auto_create_repo=True
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Quick extract and push failed: {str(e)}"
            }

# Global agent instance
git_agent = GitIntegrationAgent()
