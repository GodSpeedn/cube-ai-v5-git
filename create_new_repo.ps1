# PowerShell script to create new GitHub repository and upload code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    GitHub Repository Creation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
try {
    $ghVersion = gh --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "GitHub CLI found! Using automated method..." -ForegroundColor Green
        Write-Host ""
        
        # Get repository name from user
        $repoName = Read-Host "Enter repository name"
        if ([string]::IsNullOrWhiteSpace($repoName)) {
            Write-Host "Repository name cannot be empty!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        # Get repository description
        $repoDesc = Read-Host "Enter repository description (optional)"
        
        # Get visibility preference
        Write-Host ""
        Write-Host "Repository visibility:" -ForegroundColor Yellow
        Write-Host "1. Public (visible to everyone)"
        Write-Host "2. Private (visible only to you)"
        $visibility = Read-Host "Choose (1 or 2)"
        
        $visibilityFlag = if ($visibility -eq "2") { "--private" } else { "--public" }
        
        Write-Host ""
        Write-Host "Creating repository: $repoName" -ForegroundColor Yellow
        Write-Host ""
        
        # Create repository using GitHub CLI
        gh repo create $repoName --description $repoDesc $visibilityFlag
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to create repository. Please check your GitHub CLI authentication." -ForegroundColor Red
            Write-Host "Run: gh auth login" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Write-Host "Repository created successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Configure Git
        Write-Host "Configuring Git..." -ForegroundColor Yellow
        git config user.name "GodSpeedn"
        git config user.email "GodSpeedn@users.noreply.github.com"
        
        # Set remote URL
        Write-Host "Setting up remote..." -ForegroundColor Yellow
        git remote set-url origin "https://github.com/GodSpeedn/$repoName.git"
        
        # Add all files
        Write-Host "Adding files..." -ForegroundColor Yellow
        git add .
        
        # Commit changes
        Write-Host "Committing changes..." -ForegroundColor Yellow
        git commit -m "Initial commit: $repoDesc"
        
        # Push to GitHub
        Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
        git push -u origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "    SUCCESS!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "Repository created and uploaded successfully!" -ForegroundColor Green
            Write-Host "Repository URL: https://github.com/GodSpeedn/$repoName" -ForegroundColor Cyan
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Red
            Write-Host "    ERROR!" -ForegroundColor Red
            Write-Host "========================================" -ForegroundColor Red
            Write-Host "Failed to push to GitHub. Please check your connection and try again." -ForegroundColor Red
            Write-Host ""
        }
    }
} catch {
    Write-Host "GitHub CLI not found. Using manual method..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    Manual Repository Creation" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Go to https://github.com/new" -ForegroundColor White
    Write-Host "2. Create a new repository with your desired name" -ForegroundColor White
    Write-Host "3. Copy the repository URL" -ForegroundColor White
    Write-Host "4. Run the following commands in this terminal:" -ForegroundColor White
    Write-Host ""
    Write-Host "   git config user.name `"GodSpeedn`"" -ForegroundColor Green
    Write-Host "   git config user.email `"GodSpeedn@users.noreply.github.com`"" -ForegroundColor Green
    Write-Host "   git remote set-url origin YOUR_REPO_URL_HERE" -ForegroundColor Green
    Write-Host "   git add ." -ForegroundColor Green
    Write-Host "   git commit -m `"Initial commit`"" -ForegroundColor Green
    Write-Host "   git push -u origin main" -ForegroundColor Green
    Write-Host ""
}

Read-Host "Press Enter to exit"
