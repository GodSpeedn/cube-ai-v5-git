"""
Configuration management for Git Integration System
Separate from main system to avoid conflicts
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitIntegrationConfig(BaseModel):
    """Configuration for Git Integration System"""
    
    # GitHub Configuration
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    github_email: Optional[str] = None
    
    # Paths (relative to this git-integration directory)
    main_system_path: str = "../backend-ai"
    generated_dir: str = "../backend-ai/generated"
    output_dir: str = "./extracted"
    
    # File Patterns
    include_patterns: list = [
        "*.py", "*.js", "*.ts", "*.tsx", "*.jsx", 
        "*.html", "*.css", "*.json", "*.md", "*.txt"
    ]
    exclude_patterns: list = [
        "__pycache__", "*.log", "*.tmp", ".DS_Store", 
        "node_modules", ".git", "*.pyc"
    ]
    
    # GitHub Repository Settings
    default_private: bool = False
    auto_init: bool = True
    gitignore_template: str = "Python"
    
    @validator('github_token', 'github_username')
    def validate_github_config(cls, v):
        if v is None:
            return None
        return v.strip() if isinstance(v, str) else v
    
    def is_github_configured(self) -> bool:
        """Check if GitHub is properly configured"""
        return bool(self.github_token and self.github_username)
    
    def get_main_system_path(self) -> Path:
        """Get the main system path as Path object"""
        return Path(self.main_system_path).resolve()
    
    def get_generated_dir(self) -> Path:
        """Get the generated directory path as Path object"""
        return Path(self.generated_dir).resolve()
    
    def get_output_dir(self) -> Path:
        """Get the output directory path as Path object"""
        output_path = Path(self.output_dir).resolve()
        output_path.mkdir(exist_ok=True)
        return output_path

def load_config() -> GitIntegrationConfig:
    """Load configuration from environment variables and defaults"""
    
    # Load from environment variables
    config_data = {
        "github_token": os.getenv("GITHUB_TOKEN"),
        "github_username": os.getenv("GITHUB_USERNAME"),
        "github_email": os.getenv("GITHUB_EMAIL"),
    }
    
    # Remove None values
    config_data = {k: v for k, v in config_data.items() if v is not None}
    
    return GitIntegrationConfig(**config_data)

# Global config instance
config = load_config()
