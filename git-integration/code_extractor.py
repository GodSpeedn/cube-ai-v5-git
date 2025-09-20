"""
Code extraction from the main system's generated files
Separate from main system to avoid conflicts
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

class ExtractedFile(BaseModel):
    """Represents an extracted file"""
    path: str
    content: str
    language: str
    size: int
    created_at: str
    source_file: str

class CodeExtractor:
    """Extracts code from the main system's generated files"""
    
    def __init__(self, generated_dir: Path, output_dir: Path):
        self.generated_dir = generated_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_all_files(self, include_patterns: List[str] = None, 
                         exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Extract all files from the generated directory
        
        Args:
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            
        Returns:
            Extraction result with files and statistics
        """
        try:
            if not self.generated_dir.exists():
                return {
                    "success": False,
                    "error": f"Generated directory does not exist: {self.generated_dir}"
                }
            
            # Default patterns
            if include_patterns is None:
                include_patterns = ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", 
                                  "*.html", "*.css", "*.json", "*.md", "*.txt"]
            
            if exclude_patterns is None:
                exclude_patterns = ["__pycache__", "*.log", "*.tmp", ".DS_Store", 
                                  "node_modules", ".git", "*.pyc"]
            
            extracted_files = []
            total_size = 0
            
            # Walk through the generated directory
            for file_path in self.generated_dir.rglob("*"):
                if file_path.is_file():
                    # Check if file should be included
                    should_include = any(file_path.match(pattern) for pattern in include_patterns)
                    should_exclude = any(file_path.match(pattern) for pattern in exclude_patterns)
                    
                    if should_include and not should_exclude:
                        try:
                            # Read file content
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Determine language from extension
                            language = self._get_language_from_extension(file_path.suffix)
                            
                            # Create relative path
                            relative_path = str(file_path.relative_to(self.generated_dir))
                            
                            # Get file stats
                            file_stats = file_path.stat()
                            created_at = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                            
                            # Create extracted file
                            extracted_file = ExtractedFile(
                                path=relative_path,
                                content=content,
                                language=language,
                                size=len(content),
                                created_at=created_at,
                                source_file=str(file_path)
                            )
                            
                            extracted_files.append(extracted_file)
                            total_size += len(content)
                            
                        except Exception as e:
                            print(f"Warning: Could not read file {file_path}: {e}")
                            continue
            
            if not extracted_files:
                return {
                    "success": False,
                    "error": "No files found to extract"
                }
            
            # Sort files by creation time (newest first)
            extracted_files.sort(key=lambda x: x.created_at, reverse=True)
            
            return {
                "success": True,
                "files": extracted_files,
                "stats": {
                    "total_files": len(extracted_files),
                    "total_size": total_size,
                    "languages": list(set(f.language for f in extracted_files)),
                    "extraction_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Extraction failed: {str(e)}"
            }
    
    def extract_latest_files(self, limit: int = 10) -> Dict[str, Any]:
        """
        Extract only the latest files (by creation time)
        
        Args:
            limit: Maximum number of files to extract
            
        Returns:
            Extraction result with latest files
        """
        result = self.extract_all_files()
        
        if not result["success"]:
            return result
        
        # Get the latest files
        files = result["files"][:limit]
        
        return {
            "success": True,
            "files": files,
            "stats": {
                "total_files": len(files),
                "total_size": sum(f.size for f in files),
                "languages": list(set(f.language for f in files)),
                "extraction_time": datetime.now().isoformat(),
                "limited_to": limit
            }
        }
    
    def extract_code_files_only(self) -> Dict[str, Any]:
        """
        Extract only code files (Python, JavaScript, TypeScript, etc.)
        
        Returns:
            Extraction result with code files only
        """
        code_patterns = ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.java", "*.cpp", "*.c", "*.cs"]
        exclude_patterns = ["__pycache__", "*.log", "*.tmp", ".DS_Store", "node_modules", ".git", "*.pyc"]
        
        return self.extract_all_files(code_patterns, exclude_patterns)
    
    def create_readme(self, files: List[ExtractedFile], project_name: str = "AI Generated Project") -> str:
        """
        Create a README file for the extracted files
        
        Args:
            files: List of extracted files
            project_name: Name of the project
            
        Returns:
            README content
        """
        readme = f"""# {project_name}

Generated by AI Assistant on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files

"""
        
        # Group files by language
        files_by_language = {}
        for file in files:
            if file.language not in files_by_language:
                files_by_language[file.language] = []
            files_by_language[file.language].append(file)
        
        # Add files by language
        for language, lang_files in files_by_language.items():
            readme += f"### {language.upper()} Files\n\n"
            for file in lang_files:
                readme += f"- `{file.path}` - {file.size} bytes\n"
            readme += "\n"
        
        # Add statistics
        total_files = len(files)
        total_size = sum(f.size for f in files)
        languages = list(set(f.language for f in files))
        
        readme += f"""## Statistics

- **Total Files**: {total_files}
- **Total Size**: {total_size:,} bytes
- **Languages**: {', '.join(languages)}
- **Extracted**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Usage

Run the files to see the generated code in action. Each file contains complete, runnable code generated by the AI assistant.

## Notes

This project was automatically generated and uploaded to GitHub by the AI Assistant's Git Integration System.
"""
        
        return readme
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Get language name from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell'
        }
        
        return language_map.get(extension.lower(), 'text')
