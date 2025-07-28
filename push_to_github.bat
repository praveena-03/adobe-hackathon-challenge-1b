@echo off
echo ========================================
echo Adobe Hackathon Challenge 1b - GitHub Push
echo ========================================
echo.

echo Please enter your GitHub username:
set /p GITHUB_USERNAME=

echo.
echo Adding remote repository...
git remote add origin https://github.com/%GITHUB_USERNAME%/adobe-hackathon-challenge-1b.git

echo.
echo Renaming branch to main...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Repository URL: https://github.com/%GITHUB_USERNAME%/adobe-hackathon-challenge-1b
echo ========================================
echo.
echo Your repository is now live on GitHub!
echo You can submit this URL for Adobe Hackathon Challenge 1b.
echo.
pause 