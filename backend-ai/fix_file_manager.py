#!/usr/bin/env python3
"""
Fix the file_manager.py syntax issues
"""

import re

# Read the broken file
with open('file_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the indentation issue
# Replace the problematic section
old_section = '''                try:
                import requests
                    git_status_response = requests.get("http://localhost:8000/git/status", timeout=2)
                if git_status_response.status_code == 200:'''

new_section = '''                try:
                    import requests
                    git_status_response = requests.get("http://localhost:8000/git/status", timeout=2)
                    if git_status_response.status_code == 200:'''

# Replace the problematic section
content = content.replace(old_section, new_section)

# Write the fixed content
with open('file_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed file_manager.py syntax issues")
