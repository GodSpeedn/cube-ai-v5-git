@echo off
echo ========================================
echo    GitHub Repository Creation Script
echo ========================================
echo.

REM Check if GitHub CLI is installed
where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo GitHub CLI (gh) is not installed.
    echo Please install it from: https://cli.github.com/
    echo Or use the manual method below.
    echo.
    goto :manual_method
)

echo GitHub CLI found! Using automated method...
echo.

REM Get repository name from user
set /p repo_name="Enter repository name: "
if "%repo_name%"=="" (
    echo Repository name cannot be empty!
    pause
    exit /b 1
)

REM Get repository description
set /p repo_desc="Enter repository description (optional): "

REM Get visibility preference
echo.
echo Repository visibility:
echo 1. Public (visible to everyone)
echo 2. Private (visible only to you)
set /p visibility="Choose (1 or 2): "

if "%visibility%"=="1" (
    set visibility_flag="--public"
) else if "%visibility%"=="2" (
    set visibility_flag="--private"
) else (
    echo Invalid choice. Defaulting to public.
    set visibility_flag="--public"
)

echo.
echo Creating repository: %repo_name%
echo.

REM Create repository using GitHub CLI
gh repo create %repo_name% --description "%repo_desc%" %visibility_flag%

if %errorlevel% neq 0 (
    echo Failed to create repository. Please check your GitHub CLI authentication.
    echo Run: gh auth login
    pause
    exit /b 1
)

echo Repository created successfully!
echo.

REM Configure Git
echo Configuring Git...
git config user.name "GodSpeedn"
git config user.email "GodSpeedn@users.noreply.github.com"

REM Set remote URL
echo Setting up remote...
git remote set-url origin https://github.com/GodSpeedn/%repo_name%.git

REM Add all files
echo Adding files...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Initial commit: %repo_desc%"

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    SUCCESS!
    echo ========================================
    echo Repository created and uploaded successfully!
    echo Repository URL: https://github.com/GodSpeedn/%repo_name%
    echo.
) else (
    echo.
    echo ========================================
    echo    ERROR!
    echo ========================================
    echo Failed to push to GitHub. Please check your connection and try again.
    echo.
)

goto :end

:manual_method
echo ========================================
echo    Manual Repository Creation
echo ========================================
echo.
echo Please follow these steps:
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository with your desired name
echo 3. Copy the repository URL
echo 4. Run the following commands in this terminal:
echo.
echo    git config user.name "GodSpeedn"
echo    git config user.email "GodSpeedn@users.noreply.github.com"
echo    git remote set-url origin YOUR_REPO_URL_HERE
echo    git add .
echo    git commit -m "Initial commit"
echo    git push -u origin main
echo.

:end
pause
