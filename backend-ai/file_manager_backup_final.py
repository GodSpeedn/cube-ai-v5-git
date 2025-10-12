"""
Advanced File Management System for AI-Generated Code
Handles automatic file saving, GitHub integration, and project organization
"""

import os
import re
import json
import uuid
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Import Git integration if available
try:
    import sys
    from pathlib import Path as PathLib
    
    # Add git-integration to Python path
    git_integration_path = PathLib(__file__).parent.parent / "git-integration"
    if git_integration_path.exists() and str(git_integration_path) not in sys.path:
        sys.path.insert(0, str(git_integration_path))
        logging.info(f"✅ Added git-integration to path: {git_integration_path}")
    
    from github_service import GitHubService, GitHubRepository, GitHubFile
    GIT_AVAILABLE = True
    logging.info("✅ GitHub service modules imported successfully")
except ImportError as e:
    logging.warning(f"⚠️ GitHub service not available: {e}")
    GIT_AVAILABLE = False
    GitHubService = None
    GitHubRepository = None
    GitHubFile = None

class FileManager:
    """Advanced file management for AI-generated code with automatic Git integration"""
    
    def __init__(self, base_dir: str = "generated"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Initialize GitHub service if available
        self.github_service = None
        self.github_available = False
        
        if GIT_AVAILABLE:
            # Check for GitHub credentials in environment variables first
            github_token = os.environ.get("GITHUB_TOKEN")
            github_username = os.environ.get("GITHUB_USERNAME")
            
            if github_token and github_username and github_token != "your_github_token_here":
                self.github_available = True
                logging.info("✅ GitHub credentials found in environment variables")
                logging.info(f"   Username: {github_username}")
                logging.info("   GitHub service will be available for auto-upload")
            else:
                # Fallback: Try to get GitHub config from main backend service (if running)
                try:
                    import requests
                    git_status_response = requests.get("http://localhost:8000/git/status", timeout=2)
                    if git_status_response.status_code == 200:

                        git_status = git_status_response.json()
                        if git_status.get("configured", False):
                            self.github_available = True
                            logging.info("✅ GitHub configured via main backend service")
                        else:
                            logging.info("ℹ️ Main backend service available but GitHub not configured")
                    else:

                        logging.info("ℹ️ Main backend service not responding")
                except Exception as e:
                    logging.info(f"ℹ️ Main backend service not available: {str(e)[:100]}")
                    logging.info("💡 This is OK if you're only running the online service")
                
                if not self.github_available:
                    logging.info("ℹ️ GitHub not configured - code will be saved locally only")
        else:
            logging.info("ℹ️ GitHub service modules not available")
        
        # Project tracking
        self.active_projects = {}
        
    def create_project(self, task_description: str, conversation_id: str = None) -> Dict[str, str]:
        """Create a new project with organized folder structure"""
        try:
            # Generate project name from task description
            project_name = self._generate_project_name(task_description)
            project_id = str(uuid.uuid4())[:8]
            full_project_name = f"{project_name}_{project_id}"
            
            # Create project directory structure
            project_dir = self.base_dir / "projects" / full_project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "tests").mkdir(exist_ok=True)
            (project_dir / "docs").mkdir(exist_ok=True)
            
            # Create project metadata
            metadata = {
                "project_id": project_id,
                "project_name": full_project_name,
                "task_description": task_description,
                "conversation_id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "files": {
                    "src": [],
                    "tests": [],
                    "docs": []
                },
                "github_repo": None,
                "status": "active"
            }
            
            # Save metadata
            with open(project_dir / "project.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Track active project
            self.active_projects[conversation_id or "default"] = {
                "project_dir": project_dir,
                "metadata": metadata
            }
            
            logging.info(f"📁 Created project: {full_project_name}")
            return {
                "project_name": full_project_name,
                "project_dir": str(project_dir),
                "project_id": project_id
            }
            
        except Exception as e:
            logging.error(f"❌ Failed to create project: {e}")
            return {}
    
    def save_code(self, code: str, filename: str = None, file_type: str = "src", 
                  conversation_id: str = None, task_description: str = None) -> Dict[str, str]:
        """Save generated code with automatic project management and enhanced error handling"""
        try:
            # Validate inputs
            if not code or not code.strip():
                return {"error": "Code content cannot be empty"}
            
            if file_type not in ["src", "tests", "docs"]:
                return {"error": f"Invalid file_type '{file_type}'. Must be 'src', 'tests', or 'docs'"}
            
            # Initialize syntax validation variables
            syntax_valid = True
            syntax_error = ""
            
            # Validate code syntax for Python files
            if filename and filename.endswith('.py'):
                syntax_valid, syntax_error = self._validate_python_syntax(code)
                if not syntax_valid:
                    logging.warning(f"⚠️ Python syntax warning: {syntax_error}")
                    # Continue saving but log the warning
            
            # Get or create project
            if conversation_id and conversation_id in self.active_projects:
                project_info = self.active_projects[conversation_id]
                project_dir = project_info["project_dir"]
                metadata = project_info["metadata"]
            else:
                # Create new project
                project_info = self.create_project(task_description or "AI Generated Code", conversation_id)
                if not project_info:
                    return {"error": "Failed to create project"}
                project_dir = Path(project_info["project_dir"])
                metadata = self._load_project_metadata(project_dir)
            
            # Generate filename if not provided
            if not filename:
                filename = self._generate_filename(code, file_type)
            
            # Validate filename
            if not self._is_valid_filename(filename):
                return {"error": f"Invalid filename: {filename}"}
            
            # Determine file type and directory
            file_dir = project_dir / file_type
            filepath = file_dir / filename
            
            # Ensure directory exists
            file_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if file already exists and create backup
            if filepath.exists():
                backup_path = filepath.with_suffix(f"{filepath.suffix}.backup_{int(datetime.now().timestamp())}")
                filepath.rename(backup_path)
                logging.info(f"📋 Created backup: {backup_path}")
            
            # Save code to file with atomic write
            temp_path = filepath.with_suffix(f"{filepath.suffix}.tmp")
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                # Atomic move
                temp_path.rename(filepath)
                
            except Exception as write_error:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise write_error
            
            # Update metadata
            file_info = {
                "filename": filename,
                "filepath": str(filepath),
                "created_at": datetime.now().isoformat(),
                "size": len(code),
                "lines": len(code.splitlines()),
                "encoding": "utf-8"
            }
            
            # Add syntax validation info for Python files
            if filename.endswith('.py'):
                file_info["syntax_valid"] = syntax_valid
                if not syntax_valid:
                    file_info["syntax_error"] = syntax_error
            
            metadata["files"][file_type].append(file_info)
            
            # Save updated metadata with atomic write
            metadata_temp = project_dir / "project.json.tmp"
            metadata_file = project_dir / "project.json"
            
            # Use a unique temp file name to avoid conflicts
            import time
            unique_temp = project_dir / f"project.json.tmp.{int(time.time() * 1000)}"
            
            with open(unique_temp, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Atomic rename
            unique_temp.rename(metadata_file)
            
            logging.info(f"💾 Code saved to: {filepath} ({len(code)} chars, {file_info['lines']} lines)")
            
            # Auto-upload to GitHub if available (async, don't block)
            github_result = self._auto_upload_to_github(project_dir, metadata)
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "project_name": metadata["project_name"],
                "file_info": file_info,
                "github_result": github_result
            }
            
        except PermissionError as e:
            logging.error(f"❌ Permission denied saving file: {e}")
            return {"error": f"Permission denied: {str(e)}"}
        except OSError as e:
            logging.error(f"❌ File system error saving file: {e}")
            return {"error": f"File system error: {str(e)}"}
        except Exception as e:
            logging.error(f"❌ Failed to save code: {e}")
            return {"error": str(e)}
    
    def _generate_project_name(self, task_description: str) -> str:
        """Generate a sensible project name from task description"""
        # Clean and normalize the description
        clean_desc = re.sub(r'[^\w\s-]', '', task_description.lower())
        clean_desc = re.sub(r'\s+', '_', clean_desc.strip())
        
        # Limit length and add meaningful suffix
        if len(clean_desc) > 30:
            clean_desc = clean_desc[:30]
        
        # Add descriptive suffix based on content
        if any(word in clean_desc for word in ['sum', 'add', 'calculate', 'math']):
            clean_desc += "_calculator"
        elif any(word in clean_desc for word in ['app', 'application', 'program']):
            clean_desc += "_app"
        elif any(word in clean_desc for word in ['api', 'service', 'server']):
            clean_desc += "_api"
        else:
            clean_desc += "_project"
        
        return clean_desc
    
    def _generate_filename(self, code: str, file_type: str) -> str:
        """Generate a sensible filename based on code content"""
        # Extract function/class names
        function_match = re.search(r'def\s+(\w+)', code)
        class_match = re.search(r'class\s+(\w+)', code)
        
        if file_type == "tests":
            # For test files, always prefix with test_
            if class_match:
                # If it's a test class, extract the base name
                class_name = class_match.group(1)
                # Remove "Test" prefix/suffix if present
                base_name = class_name.replace("Test", "").replace("test", "").lower()
                if not base_name:
                    base_name = "module"
            elif function_match:
                # If it's a test function, extract the base name
                func_name = function_match.group(1)
                # Remove "test_" prefix if present
                base_name = func_name.replace("test_", "").lower()
                if not base_name:
                    base_name = "module"
            else:
                base_name = "module"
            return f"test_{base_name}.py"
        elif class_match:
            base_name = class_match.group(1)
        elif function_match:
            base_name = function_match.group(1)
        else:
            base_name = "main"
        
        # Add appropriate extension
        if file_type == "docs":
            return f"{base_name}_documentation.md"
        else:
            return f"{base_name}.py"
    
    def _auto_upload_to_github(self, project_dir: Path, metadata: Dict) -> Dict[str, str]:
        """Automatically upload project to GitHub by creating a NEW repository"""
        try:
            import requests
            import os
            
            logging.info("=" * 60)
            logging.info("🚀 STARTING GITHUB AUTO-UPLOAD")
            logging.info(f"📁 Project: {metadata.get('project_name', 'Unknown')}")
            logging.info(f"📝 Description: {metadata.get('task_description', 'Unknown')}")
            logging.info(f"📂 Directory: {project_dir}")
            logging.info("=" * 60)
            
            # Method 1: Try to get GitHub config from environment variables (direct access)
            github_token = os.environ.get("GITHUB_TOKEN")
            github_username = os.environ.get("GITHUB_USERNAME")
            github_configured = False
            config_source = None
            
            if github_token and github_username and github_token != "your_github_token_here":
                logging.info("✅ Found GitHub credentials in environment variables")
                logging.info(f"   Username: {github_username}")
                github_configured = True
                config_source = "environment"
            else:
                # Method 2: Try to get GitHub config from main backend service (if running)
                logging.info("🔍 GitHub credentials not in environment, checking main backend service...")
                git_status = None
                try:
                    git_status_response = requests.get("http://localhost:8000/git/status", timeout=2)
                    if git_status_response.status_code == 200:

                        git_status = git_status_response.json()
                        if git_status.get("configured", False):

                            github_configured = True
                            config_source = "backend_service"
                            # Extract credentials if available
                            user_info = git_status.get("user", {})
                            if isinstance(user_info, dict):
                                github_username = user_info.get("login", "Unknown")
                            logging.info(f"✅ GitHub configured via main backend service")
                            logging.info(f"   User: {github_username}")
                        else:
                            logging.warning("⚠️ Main backend service available but GitHub not configured")
                    else:
                        logging.info(f"ℹ️ Main backend service returned status {git_status_response.status_code}")
                except requests.exceptions.RequestException as e:
                    logging.info(f"ℹ️ Main backend service not available: {str(e)[:100]}")
                    logging.info("💡 This is OK if you're only running the online service")
            
            if not github_configured:
                logging.warning("=" * 60)
                logging.warning("⚠️ GitHub NOT CONFIGURED")
                logging.warning("📌 Code saved locally only (no GitHub upload)")
                logging.warning("")
                logging.warning("To enable GitHub auto-upload:")
                logging.warning("1. Edit backend-ai/keys.txt")
                logging.warning("2. Add your GITHUB_TOKEN and GITHUB_USERNAME")
                logging.warning("3. Get token from: https://github.com/settings/tokens")
                logging.warning("4. Restart the service")
                logging.warning("=" * 60)
                return {"status": "github_not_available", "error": "GitHub not configured"}
            
            logging.info(f"🐙 GitHub configuration loaded from: {config_source}")
            
            # If we got credentials from backend service but not environment, we need to get the token
            if config_source == "backend_service":
                # Backend service doesn't expose the token, so we can't upload
                # User needs to add credentials to environment
                logging.warning("⚠️ GitHub credentials in backend service but not accessible for upload")
                logging.warning("💡 Add GITHUB_TOKEN to backend-ai/keys.txt for auto-upload to work")
                return {"status": "github_not_available", "error": "GitHub token not accessible"}
            
            logging.info(f"📤 Preparing to upload to GitHub...")
            logging.info(f"   Project: {metadata['project_name']}")
            logging.info(f"   Description: {metadata['task_description'][:50]}...")
            
            # If we have direct credentials from environment, use GitHub API directly
            if config_source == "environment":
                logging.info("🔧 Using direct GitHub API with environment credentials")
                
                # Check if GitHub service is available
                if not GIT_AVAILABLE:
                    logging.error("❌ GitHub service modules not available")
                    logging.error("💡 Make sure git-integration folder exists with github_service.py")
                    return {"status": "error", "error": "GitHub service modules not imported"}
                
                try:
                    # Initialize GitHub service (modules already imported at top)
                    github_service = GitHubService(token=github_token, username=github_username)
                    
                    # Create repository name
                    repo_name = metadata["project_name"].replace(" ", "-").replace("_", "-").lower()
                    repo_description = f"AI Generated: {metadata['task_description'][:100]}"
                    
                    logging.info(f"📁 Creating repository: {repo_name}")
                    
                    # Create repository
                    repo = GitHubRepository(
                        name=repo_name,
                        description=repo_description,
                        private=False,
                        auto_init=False
                    )
                    
                    create_result = github_service.create_repository(repo)
                    if not create_result["success"]:
                        # Repository might already exist, try with timestamp
                        import time
                        timestamp = int(time.time())
                        repo_name = f"{repo_name}-{timestamp}"
                        repo.name = repo_name
                        create_result = github_service.create_repository(repo)
                        if not create_result["success"]:
                            raise Exception(f"Failed to create repository: {create_result.get('error')}")
                    
                    repository_url = create_result['repository']['html_url']
                    logging.info(f"✅ Repository created: {repository_url}")
                    
                    # Collect all files from project directory
                    github_files = []
                    for file_path in project_dir.rglob("*"):
                        if file_path.is_file() and not file_path.name.startswith('.'):
                            try:
                                content = file_path.read_text(encoding='utf-8')
                                rel_path = file_path.relative_to(project_dir)
                                
                                # Determine GitHub path based on file location
                                if "test" in str(rel_path).lower():
                                    github_path = f"tests/{rel_path.name}"
                                elif rel_path.parent.name == "src":
                                    github_path = f"src/{rel_path.name}"
                                elif rel_path.parent.name == "docs":
                                    github_path = f"docs/{rel_path.name}"
                                else:
                                    github_path = str(rel_path).replace("\\", "/")
                                
                                github_files.append(GitHubFile(
                                    path=github_path,
                                    content=content,
                                    message=f"Add {file_path.name}"
                                ))
                            except Exception as e:
                                logging.warning(f"⚠️ Could not read file {file_path}: {e}")
                    
                    # Add README
                    readme_content = f"""# {metadata['project_name']}

{metadata['task_description']}

## Generated Files

This repository contains AI-generated code.

## Generation Details
- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Project: {metadata['project_name']}

## Files
{chr(10).join(f"- `{f.path}`" for f in github_files)}
"""
                    github_files.append(GitHubFile(
                        path="README.md",
                        content=readme_content,
                        message="Add README"
                    ))
                    
                    # Push files to GitHub
                    logging.info(f"📤 Uploading {len(github_files)} files...")
                    push_result = github_service.push_files(
                        repo_name=repo_name,
                        files=github_files,
                        commit_message=f"AI Generated Code - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    
                    if not push_result["success"]:
                        raise Exception(f"Failed to push files: {push_result.get('error')}")
                    
                    # Update metadata and return success
                    metadata["github_repo"] = repository_url
                    metadata["status"] = "uploaded"
                    metadata["last_upload"] = datetime.now().isoformat()
                    
                    # Save updated metadata
                    metadata_file = project_dir / "project.json"
                    import time
                    unique_temp = project_dir / f"project.json.tmp.{int(time.time() * 1000)}"
                    with open(unique_temp, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    unique_temp.rename(metadata_file)
                    
                    logging.info("=" * 60)
                    logging.info("✅ GITHUB UPLOAD SUCCESSFUL!")
                    logging.info(f"🐙 Repository URL: {repository_url}")
                    logging.info(f"📊 Files uploaded: {push_result['files_pushed']}")
                    logging.info(f"⏰ Upload time: {metadata['last_upload']}")
                    logging.info("=" * 60)
                    
                    return {
                        "status": "success",
                        "repo_url": repository_url,
                        "files_uploaded": push_result['files_pushed'],
                        "upload_time": metadata["last_upload"]
                    }
                    
                except ImportError as e:
                    logging.error(f"❌ GitHub service not available: {e}")
                    logging.error("💡 Make sure git-integration module is in the path")
                    return {"status": "error", "error": "GitHub service module not available"}
                except Exception as e:
                    logging.error(f"❌ Direct GitHub upload failed: {e}")
                    return {"status": "error", "error": str(e)}
            
            # Otherwise, use the backend service endpoint
            upload_data = {
                "project_name": metadata["project_name"],
                "task_description": metadata["task_description"],
                "create_new_repo": True
            }
            
            # Call the auto-upload endpoint with retry logic
            response = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post("http://localhost:8000/git/auto-upload", json=upload_data, timeout=30)
                    if response.status_code == 200:
                        break
                    else:
                        logging.warning(f"⚠️ GitHub upload failed (attempt {attempt + 1}): {response.status_code}")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)  # Wait 2 seconds before retry
                            continue
                except requests.exceptions.RequestException as e:
                    logging.warning(f"⚠️ GitHub upload request failed (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)
                        continue
            
            if response and response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Update metadata
                    metadata["github_repo"] = result["repository_url"]
                    metadata["status"] = "uploaded"
                    metadata["last_upload"] = datetime.now().isoformat()
                    
                    # Save metadata atomically
                    metadata_file = project_dir / "project.json"
                    
                    # Use a unique temp file name to avoid conflicts
                    import time
                    unique_temp = project_dir / f"project.json.tmp.{int(time.time() * 1000)}"
                    
                    with open(unique_temp, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    # Atomic rename
                    unique_temp.rename(metadata_file)
                    
                    logging.info("=" * 60)
                    logging.info("✅ GITHUB UPLOAD SUCCESSFUL!")
                    logging.info(f"🐙 Repository URL: {result['repository_url']}")
                    logging.info(f"📊 Files uploaded: {result.get('files_uploaded', 0)}")
                    logging.info(f"⏰ Upload time: {metadata['last_upload']}")
                    logging.info("=" * 60)
                    return {
                        "status": "success",
                        "repo_url": result["repository_url"],
                        "files_uploaded": result.get("files_uploaded", 0),
                        "upload_time": metadata["last_upload"]
                    }
                else:
                    error_msg = result.get("message", "Unknown error")
                    logging.error("=" * 60)
                    logging.error("❌ GITHUB UPLOAD FAILED")
                    logging.error(f"Error: {error_msg}")
                    logging.error("=" * 60)
                    return {"status": "failed", "error": error_msg}
            else:
                if response:
                    try:
                error = response.json()
                        error_msg = error.get('detail', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}: {response.text[:200]}'
                else:
                    error_msg = "No response from GitHub service"
                logging.error("=" * 60)
                logging.error("❌ GITHUB UPLOAD FAILED")
                logging.error(f"Error: {error_msg}")
                logging.error(f"Response status: {response.status_code if response else 'None'}")
                logging.error("=" * 60)
                return {"status": "failed", "error": error_msg}
                
        except Exception as e:
            logging.error("=" * 60)
            logging.error("❌ GITHUB AUTO-UPLOAD EXCEPTION")
            logging.error(f"Exception: {str(e)}")
            logging.error(f"Exception type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            logging.error("=" * 60)
            return {"status": "error", "error": str(e)}
    
    def _upload_project_files(self, project_dir: Path, repo_name: str) -> Dict:
        """Upload all project files to GitHub"""
        try:
            files_uploaded = 0
            
            # Upload files from each directory
            for subdir in ["src", "tests", "docs"]:
                subdir_path = project_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.iterdir():
                        if file_path.is_file():
                            # Read file content
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Upload to GitHub
                            github_path = f"{subdir}/{file_path.name}"
                            upload_result = self.github_service.push_file(
                                repo_name=repo_name,
                                file_path=github_path,
                                content=content,
                                commit_message=f"Add {file_path.name}"
                            )
                            
                            if upload_result.get("success"):
                                files_uploaded += 1
                            else:
                                logging.warning(f"Failed to upload {file_path.name}: {upload_result.get('error')}")
            
            # Upload project metadata
            metadata_path = project_dir / "project.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                upload_result = self.github_service.push_file(
                    repo_name=repo_name,
                    file_path="project.json",
                    content=content,
                    commit_message="Add project metadata"
                )
                
                if upload_result.get("success"):
                    files_uploaded += 1
            
            return {
                "success": True,
                "files_uploaded": files_uploaded
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_project_metadata(self, project_dir: Path) -> Dict:
        """Load project metadata from file"""
        metadata_path = project_dir / "project.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python syntax and return (is_valid, error_message)"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"
    
    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename is valid for the filesystem"""
        if not filename or not filename.strip():
            return False
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in filename for char in invalid_chars):
            return False
        
        # Check for reserved names on Windows
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        if filename.upper().split('.')[0] in reserved_names:
            return False
        
        # Check length
        if len(filename) > 255:
            return False
        
        return True
    
    def _sanitize_repo_name(self, name: str) -> str:
        """Sanitize repository name for GitHub"""
        # Remove invalid characters and replace with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '-', name)
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        # Ensure it starts with a letter or number
        if not re.match(r'^[a-zA-Z0-9]', sanitized):
            sanitized = 'repo-' + sanitized
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized
    
    def _create_repository_with_retry(self, repo_name: str, description: str, max_retries: int = 3) -> Dict:
        """Create GitHub repository with retry logic"""
        for attempt in range(max_retries):
            try:
                result = self.github_service.create_repository(
                    name=repo_name,
                    description=description,
                    private=False
                )
                
                if result.get("success"):
                    return result
                
                # If repo already exists, try with a different name
                if "already exists" in str(result.get("error", "")).lower():
                    repo_name = f"{repo_name}-{int(datetime.now().timestamp())}"
                    continue
                
                # For other errors, wait and retry
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                return result
                
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def _upload_project_files_with_retry(self, project_dir: Path, repo_name: str, max_retries: int = 3) -> Dict:
        """Upload project files with retry logic"""
        for attempt in range(max_retries):
            try:
                result = self._upload_project_files(project_dir, repo_name)
                if result.get("success"):
                    return result
                
                # Wait and retry on failure
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                
                return result
                
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def get_project_files(self, project_name: str) -> List[Dict]:
        """Get all files in a project - DYNAMIC: Shows ALL files recursively"""
        project_dir = self.base_dir / "projects" / project_name
        if not project_dir.exists():
            return []
        
        files = []
        
        # DYNAMIC: Get ALL files recursively from the entire project directory
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Get relative path from project root
                rel_path = file_path.relative_to(project_dir)
                
                # Determine file type based on path and name
                file_type = "other"
                if "test" in str(rel_path).lower() or "test" in file_path.name.lower():
                    file_type = "tests"
                elif "doc" in str(rel_path).lower() or file_path.suffix in ['.md', '.txt', '.rst']:
                    file_type = "docs"
                elif file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs']:
                    file_type = "src"
                elif file_path.suffix in ['.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg']:
                    file_type = "config"
                elif file_path.suffix in ['.css', '.scss', '.sass', '.less']:
                    file_type = "styles"
                elif file_path.suffix in ['.html', '.htm']:
                    file_type = "templates"
                
                # Try to read content
                content = ""
                try:
                    content = file_path.read_text(encoding='utf-8')
                except Exception as e:
                    content = f"Error reading file: {str(e)}"
                
                # Get file info
                stat = file_path.stat()
                
                files.append({
                    "name": file_path.name,
                    "path": str(rel_path),
                    "full_path": str(file_path),
                    "type": file_type,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "content": content,
                    "extension": file_path.suffix,
                    "is_test": "test" in file_path.name.lower(),
                    "is_code": file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.html', '.css', '.scss', '.sass', '.less'],
                    "is_config": file_path.suffix in ['.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg'],
                    "is_documentation": file_path.suffix in ['.md', '.txt', '.rst', '.doc', '.docx'],
                    "directory": str(rel_path.parent) if rel_path.parent != Path('.') else "root"
                })
        
        # Sort files: directories first, then by type, then by name
        files.sort(key=lambda x: (
            x['directory'] != "root",  # Root files first
            x['type'] != "src",        # Source files first
            x['name'].lower()          # Alphabetical
        ))
        
        return files
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        projects = []
        projects_dir = self.base_dir / "projects"
        
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    metadata = self._load_project_metadata(project_dir)
                    if metadata:
                        projects.append({
                            "name": metadata["project_name"],
                            "description": metadata["task_description"],
                            "created_at": metadata["created_at"],
                            "status": metadata["status"],
                            "github_repo": metadata.get("github_repo"),
                            "file_count": sum(len(files) for files in metadata["files"].values())
                        })
        
        return projects

# Global file manager instance
file_manager = FileManager()

