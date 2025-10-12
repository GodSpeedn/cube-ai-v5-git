#!/usr/bin/env python3
"""
Load environment variables from keys.txt file
This ensures all services can access API keys and GitHub credentials
"""

import os
from pathlib import Path

def load_keys_from_file(keys_file_path: str = None):
    """
    Load environment variables from keys.txt file
    
    Args:
        keys_file_path: Path to keys.txt file. If None, uses default location.
    """
    if keys_file_path is None:
        # Default to keys.txt in the same directory as this script
        script_dir = Path(__file__).parent
        keys_file_path = script_dir / "keys.txt"
    
    keys_file = Path(keys_file_path)
    
    if not keys_file.exists():
        print(f"[WARN] Warning: {keys_file} not found")
        return False
    
    print(f"Loading environment variables from {keys_file}")
    
    loaded_count = 0
    with open(keys_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip if key is empty
                if not key:
                    continue
                
                # Set environment variable if not already set
                if key not in os.environ:
                    os.environ[key] = value
                    loaded_count += 1
                    print(f"   [OK] {key} = {value[:20]}{'...' if len(value) > 20 else ''}")
                else:
                    print(f"   [INFO] {key} already set in environment")
            else:
                print(f"   [WARN] Invalid format on line {line_num}: {line}")
    
    print(f"[OK] Loaded {loaded_count} environment variables")
    return True

def get_github_config():
    """
    Get GitHub configuration from environment variables
    
    Returns:
        dict: GitHub configuration with 'token' and 'username' keys
    """
    token = os.environ.get('GITHUB_TOKEN')
    username = os.environ.get('GITHUB_USERNAME')
    
    if not token or not username:
        return None
    
    if token == 'your_github_token_here':
        return None
    
    return {
        'token': token,
        'username': username
    }

def check_github_config():
    """
    Check if GitHub configuration is available and valid
    
    Returns:
        bool: True if GitHub is configured, False otherwise
    """
    config = get_github_config()
    if config:
        print(f"[OK] GitHub configured for user: {config['username']}")
        return True
    else:
        print("[WARN] GitHub not configured")
        return False

if __name__ == "__main__":
    # Load keys when script is run directly
    load_keys_from_file()
    check_github_config()
