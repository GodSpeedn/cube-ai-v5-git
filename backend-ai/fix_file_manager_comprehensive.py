#!/usr/bin/env python3
"""
Comprehensive fix for file_manager.py syntax issues
"""

import re

# Read the broken file
with open('file_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all indentation issues in the __init__ method
# Replace the entire problematic section
old_section = '''            else:
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
            logging.info("ℹ️ GitHub service modules not available")'''

new_section = '''            else:
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
            logging.info("ℹ️ GitHub service modules not available")'''

# Replace the problematic section
content = content.replace(old_section, new_section)

# Write the fixed content
with open('file_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed file_manager.py syntax issues comprehensively")
