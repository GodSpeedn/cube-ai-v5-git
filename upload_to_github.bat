@echo off
echo Creating GitHub repository and uploading code...

REM Configure Git
git config user.name "GodSpeedn"
git config user.email "GodSpeedn@users.noreply.github.com"

REM Create repository using GitHub API (requires GitHub CLI or manual creation)
REM curl -X POST -H "Authorization: token YOUR_GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/user/repos -d "{\"name\":\"cube-ai-v5-git-integration\",\"description\":\"Advanced AI Agent System with Git Integration and Frontend Interface\",\"private\":false}"

REM Set remote URL (replace YOUR_GITHUB_TOKEN with your actual token)
REM git remote set-url origin https://YOUR_GITHUB_TOKEN@github.com/GodSpeedn/cube-ai-v5-git-integration.git

REM Add all files
git add .

REM Commit
git commit -m "Initial commit: Cube AI v5 with Git Integration - Advanced AI Agent System"

REM Push to GitHub
git push -u origin main

echo Upload complete! Repository: https://github.com/GodSpeedn/cube-ai-v5-git-integration
pause

