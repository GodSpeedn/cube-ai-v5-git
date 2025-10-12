#!/usr/bin/env python3
"""
Fix all Unicode emoji characters in Python files
"""

import re
from pathlib import Path

# Files to fix
files_to_fix = [
    'file_manager.py',
    'online_agent_service.py',
    'main.py'
]

# Emoji to text replacements
replacements = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARN]',
    'ℹ️': '[INFO]',
    '🔍': '[SEARCH]',
    '📁': '[DIR]',
    '📝': '[NOTE]',
    '📂': '[FOLDER]',
    '💬': '[CHAT]',
    '💾': '[SAVE]',
    '🐙': '[GITHUB]',
    '📊': '[STATS]',
    '⏰': '[TIME]',
    '💡': '[TIP]',
    '🚀': '[START]',
    '🔧': '[CONFIG]',
    '🔑': '[KEY]',
    '📤': '[UPLOAD]',
    '🎯': '[TARGET]'
}

for filename in files_to_fix:
    filepath = Path(filename)
    if not filepath.exists():
        print("[WARN] " + filename + " not found, skipping")
        continue
    
    print("[INFO] Processing " + filename + "...")
    
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all emojis
        changes = 0
        for emoji, text in replacements.items():
            if emoji in content:
                count = content.count(emoji)
                content = content.replace(emoji, text)
                changes += count
                print("  Replaced " + str(count) + " instances of emoji with " + text)
        
        # Write the fixed content
        if changes > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print("[OK] Fixed " + str(changes) + " emoji characters in " + filename)
        else:
            print("[OK] No emojis found in " + filename)
            
    except Exception as e:
        print("[ERROR] Failed to fix " + filename + ": " + str(e))

print("\n[OK] All files processed!")

