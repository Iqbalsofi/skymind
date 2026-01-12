#!/bin/bash
# SkyMind - Complete Setup Script
# Run this after creating your GitHub repository

echo "🚀 SkyMind - Complete Setup"
echo "=============================="
echo ""

# Check if GitHub username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub username"
    echo "Usage: ./setup.sh YOUR_GITHUB_USERNAME"
    echo ""
    echo "Example: ./setup.sh john-doe"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="skymind"

echo "📋 Configuration:"
echo "   GitHub Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"
echo ""

# Step 1: Add GitHub remote
echo "📡 Step 1: Adding GitHub remote..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git
if [ $? -eq 0 ]; then
    echo "   ✅ Remote added successfully"
else
    echo "   ⚠️  Remote may already exist, continuing..."
    git remote set-url origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git
fi
echo ""

# Step 2: Update README with username
echo "📝 Step 2: Updating README with your username..."
sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" README.md
sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" CONTRIBUTING.md
rm -f README.md.bak CONTRIBUTING.md.bak
git add README.md CONTRIBUTING.md
git commit -m "Update GitHub username in documentation" || echo "   ℹ️  No changes to commit"
echo "   ✅ README updated"
echo ""

# Step 3: Push to GitHub
echo "🚀 Step 3: Pushing to GitHub..."
git branch -M main
git push -u origin main
if [ $? -eq 0 ]; then
    echo "   ✅ Code pushed successfully!"
    echo ""
    echo "🎉 Success! Your repository is live at:"
    echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
else
    echo "   ❌ Push failed. Make sure you've created the repository on GitHub first."
    echo "   Go to: https://github.com/new"
    exit 1
fi

# Step 4: Instructions for Render deployment
echo "📦 Next Step: Deploy to Render (FREE)"
echo "=============================="
echo ""
echo "1. Go to https://render.com and sign up/login"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub account"
echo "4. Select repository: $GITHUB_USERNAME/$REPO_NAME"
echo "5. Configure:"
echo "   - Name: skymind"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "   - Plan: FREE"
echo "6. Add Environment Variables:"
echo "   ENV=production"
echo "   CACHE_ENABLED=false"
echo "   ALLOWED_ORIGINS=*"
echo "7. Click 'Create Web Service'"
echo ""
echo "Your site will be live at: https://skymind.onrender.com"
echo ""
echo "✨ Complete! Check DEPLOY_FREE.md for more details."
