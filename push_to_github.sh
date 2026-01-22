#!/bin/bash

# Script to push MongoDB Error Predictive Analysis to GitHub
# Usage: ./push_to_github.sh <your-github-username>

if [ -z "$1" ]; then
    echo "Usage: ./push_to_github.sh <your-github-username>"
    echo "Example: ./push_to_github.sh princekumarsingh"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="mongodb_error_predictive_analysis"

echo "=========================================="
echo "Pushing to GitHub Repository"
echo "=========================================="
echo ""
echo "Repository name: $REPO_NAME"
echo "GitHub username: $GITHUB_USERNAME"
echo ""
echo "NOTE: Make sure you've created the repository on GitHub first!"
echo "Visit: https://github.com/new"
echo "Repository name: $REPO_NAME"
echo "Visibility: Choose Public or Private"
echo ""
read -p "Press Enter after creating the repository on GitHub..."

# Add remote
echo ""
echo "Adding GitHub remote..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" 2>/dev/null || \
git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Push to GitHub
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Successfully pushed to GitHub!"
    echo "=========================================="
    echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
else
    echo ""
    echo "=========================================="
    echo "❌ Push failed. Please check:"
    echo "1. Repository exists on GitHub"
    echo "2. You have push access"
    echo "3. Your GitHub credentials are configured"
    echo "=========================================="
fi
