"""
Dependency validator for checking system dependencies and configuration.
"""
import asyncio
import subprocess
import os
import json
import logging
from typing import List, Dict, Set
from pathlib import Path

from .models import DependencyStatus, ValidationResult

logger = logging.getLogger(__name__)


class DependencyValidator:
    """Validates system dependencies and configuration."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.frontend_dir = self.base_dir.parent / "offline-ai-frontend"
    
    async def validate_all_dependencies(self) -> ValidationResult:
        """Validate all system dependencies."""
        logger.info("Validating all system dependencies")
        
        # Check Python dependencies
        python_status = await self.check_python_deps()
        
        # Check Node.js dependencies
        node_status = await self.check_node_deps()
        
        # Check API keys
        api_keys_status = await self.check_api_keys()
        
        # Combine results
        all_success = (python_status.python_deps_ok and 
                      node_status.node_deps_ok and 
                      api_keys_status.api_keys_configured)
        
        missing_deps = []
        missing_deps.extend(python_status.missing_python_deps)
        missing_deps.extend(node_status.missing_node_deps)
        missing_deps.extend(api_keys_status.missing_api_keys)
        
        installation_commands = []
        if python_status.missing_python_deps:
            installation_commands.append("pip install -r requirements.txt")
        if node_status.missing_node_deps:
            installation_commands.append("npm install")
        
        message = "All dependencies validated successfully" if all_success else f"Missing dependencies: {', '.join(missing_deps)}"
        
        return ValidationResult(
            success=all_success,
            message=message,
            missing_dependencies=missing_deps,
            installation_commands=installation_commands
        )
    
    async def check_python_deps(self) -> DependencyStatus:
        """Check Python dependencies."""
        logger.info("Checking Python dependencies")
        
        try:
            # Read requirements.txt
            requirements_file = self.base_dir / "requirements.txt"
            if not requirements_file.exists():
                return DependencyStatus(
                    python_deps_ok=False,
                    missing_python_deps=["requirements.txt not found"]
                )
            
            # Get installed packages
            result = await self._run_command(["pip", "list", "--format=json"])
            if not result.success:
                return DependencyStatus(
                    python_deps_ok=False,
                    missing_python_deps=["Failed to get installed packages"]
                )
            
            installed_packages = {pkg["name"].lower(): pkg["version"] for pkg in json.loads(result.output)}
            
            # Check required packages
            missing_deps = []
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name (ignore version specifiers for now)
                        package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                        if package_name.lower() not in installed_packages:
                            missing_deps.append(package_name)
            
            return DependencyStatus(
                python_deps_ok=len(missing_deps) == 0,
                missing_python_deps=missing_deps
            )
            
        except Exception as e:
            logger.error(f"Error checking Python dependencies: {str(e)}")
            return DependencyStatus(
                python_deps_ok=False,
                missing_python_deps=[f"Error checking dependencies: {str(e)}"]
            )
    
    async def check_node_deps(self) -> DependencyStatus:
        """Check Node.js dependencies."""
        logger.info("Checking Node.js dependencies")
        
        try:
            # Check if package.json exists
            package_json = self.frontend_dir / "package.json"
            if not package_json.exists():
                return DependencyStatus(
                    node_deps_ok=False,
                    missing_node_deps=["package.json not found"]
                )
            
            # Check if node_modules exists
            node_modules = self.frontend_dir / "node_modules"
            if not node_modules.exists():
                return DependencyStatus(
                    node_deps_ok=False,
                    missing_node_deps=["node_modules not found - run npm install"]
                )
            
            # Check if npm is available
            result = await self._run_command(["npm", "--version"])
            if not result.success:
                return DependencyStatus(
                    node_deps_ok=False,
                    missing_node_deps=["npm not available"]
                )
            
            # Check for missing dependencies by running npm list
            result = await self._run_command(["npm", "list", "--depth=0", "--json"], cwd=self.frontend_dir)
            if not result.success:
                return DependencyStatus(
                    node_deps_ok=False,
                    missing_node_deps=["Failed to check npm dependencies"]
                )
            
            # For now, assume dependencies are OK if node_modules exists and npm works
            return DependencyStatus(node_deps_ok=True)
            
        except Exception as e:
            logger.error(f"Error checking Node.js dependencies: {str(e)}")
            return DependencyStatus(
                node_deps_ok=False,
                missing_node_deps=[f"Error checking dependencies: {str(e)}"]
            )
    
    async def check_api_keys(self) -> DependencyStatus:
        """Check API key configuration."""
        logger.info("Checking API key configuration")
        
        # Import API key manager
        from .api_key_manager import APIKeyManager, APIProvider
        
        api_key_manager = APIKeyManager()
        
        # Check for available API keys (at least one should be configured)
        available_providers = []
        missing_providers = []
        
        for provider in [APIProvider.OPENAI, APIProvider.MISTRAL, APIProvider.GEMINI, APIProvider.ANTHROPIC]:
            key_info = api_key_manager.get_key_info(provider)
            if key_info and key_info.is_valid:
                available_providers.append(provider.value)
            else:
                missing_providers.append(provider.value)
        
        # At least one API key should be available
        if not available_providers:
            return DependencyStatus(
                api_keys_ok=False,
                missing_api_keys=[f"No valid API keys found. Please configure at least one API key in the Health Monitor."]
            )
        
        return DependencyStatus(
            api_keys_ok=True,
            missing_api_keys=[],
            api_keys_configured=True
        )
    
    async def _run_command(self, cmd: List[str], cwd: Path = None) -> ValidationResult:
        """Run a command and return the result."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            return ValidationResult(
                success=process.returncode == 0,
                message=stderr.decode() if process.returncode != 0 else "Command executed successfully",
                output=stdout.decode()
            )
            
        except Exception as e:
            return ValidationResult(
                success=False,
                message=f"Command failed: {str(e)}"
            )