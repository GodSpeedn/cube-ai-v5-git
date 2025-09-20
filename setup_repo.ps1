# PowerShell script to create and push to new GitHub repository

Write-Host "Setting up Git configuration..."
git config user.name "GodSpeedn"
git config user.email "GodSpeedn@users.noreply.github.com"

Write-Host "Updating remote URL..."
git remote set-url origin https://github.com/GodSpeedn/cube-ai-v5-git-integration.git

Write-Host "Adding all files..."
git add .

Write-Host "Committing changes..."
git commit -m "Initial commit: Cube AI v5 with Git Integration - Advanced AI Agent System"

Write-Host "Pushing to GitHub..."
git push -u origin main

Write-Host "Repository setup complete!"
