#!/usr/bin/env bash
# ==============================================================================
# Bidhya Portfolio — Staging Deployment Script (Decoupled Pipeline Layout)
# ==============================================================================
# This script automates Option B:
# 1. Verifies you are on the 'dev' branch to protect the production system.
# 2. Runs 'python sync_docs.py' to import & sanitize engineering files.
# 3. Commits any changes to 'dev' and always pushes 'dev' to origin, so
#    commits made by hand before running this script reach origin too.
# 4. Runs 'mkdocs gh-deploy' to compile and push directly to staging branch.
# ==============================================================================

set -e # Abort script immediately on any command failure

# 1. Robust Branch Check
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "dev" ]; then
    echo "❌ Error: You are currently on branch '$CURRENT_BRANCH'."
    echo "   Staging deployment is restricted to the 'dev' branch only."
    echo "   Please checkout 'dev' before running: git checkout dev"
    exit 1
fi

echo "============================================================"
echo "🚀 STARTING LOCAL SYNC AND COMPILE TO REMOTE STAGING"
echo "============================================================"

# 2. Sync private research directories
echo "🔄 Importing and sanitizing source document indices..."
python sync_docs.py

# 3. Check for unstaged source modifications
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Staging changes and committing code changes to 'dev' branch..."
    git add .
    COMMIT_MSG=${1:-"sync: update assets and guides $(date '+%Y-%m-%d %H:%M:%S')"}
    git commit -m "$COMMIT_MSG"
else
    echo "✅ No new changes to commit on 'dev'."
fi

# Push unconditionally so commits made by hand before this script also reach origin; a no-op when up to date
git push origin dev

# 4. Compile and push static html layout directly to 'gh-pages-dev' staging branch
echo "🏗️  Locally compiling static files and pushing directly to 'gh-pages-dev' branch..."
mkdocs gh-deploy --remote-branch gh-pages-dev --force

echo "============================================================"
echo "🎉 SUCCESS! Compiled HTML assets pushed to tracking state 'gh-pages-dev'."
echo "   Cloudflare Pages is now assembling your private preview from gh-pages-dev."
echo "============================================================"
