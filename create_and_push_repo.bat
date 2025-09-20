@echo off
echo Creating new GitHub repository and pushing code...

REM Set Git credentials
git config user.name "GodSpeedn"
git config user.email "GodSpeedn@users.noreply.github.com"

REM Update remote URL to new repository
git remote set-url origin https://github.com/GodSpeedn/cube-ai-v5-git-integration.git

REM Add all files
git add .

REM Commit changes
git commit -m "Initial commit: Cube AI v5 with Git Integration - Advanced AI Agent System"

REM Push to new repository
git push -u origin main

echo Repository created and code pushed successfully!
pause
