#!/usr/bin/env python3
"""
Fix all indentation issues in file_manager.py
"""

import re

# Read the broken file
with open('file_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all indentation issues
# Pattern 1: Fix the first occurrence in __init__ method
content = re.sub(
    r'(\s+)if git_status_response\.status_code == 200:\n(\s+)git_status = git_status_response\.json\(\)',
    r'\1if git_status_response.status_code == 200:\n\1    git_status = git_status_response.json()',
    content
)

# Pattern 2: Fix the second occurrence in _auto_upload_to_github method
content = re.sub(
    r'(\s+)if git_status_response\.status_code == 200:\n(\s+)git_status = git_status_response\.json\(\)',
    r'\1if git_status_response.status_code == 200:\n\1    git_status = git_status_response.json()',
    content
)

# Pattern 3: Fix any remaining indentation issues with if statements
content = re.sub(
    r'(\s+)if git_status\.get\("configured", False\):\n(\s+)github_configured = True',
    r'\1if git_status.get("configured", False):\n\1    github_configured = True',
    content
)

# Pattern 4: Fix any remaining indentation issues with else statements
content = re.sub(
    r'(\s+)else:\n(\s+)logging\.info\("ℹ️ Main backend service not responding"\)',
    r'\1else:\n\1    logging.info("ℹ️ Main backend service not responding")',
    content
)

# Write the fixed content
with open('file_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all indentation issues in file_manager.py")
