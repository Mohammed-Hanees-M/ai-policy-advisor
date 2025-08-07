#!/bin/bash

# Purpose: Deploys the application to Streamlit Cloud.
# Usage: ./scripts/deploy.sh

# --- Pre-deployment Validation ---

# 1. Check for GEMINI_API_KEY
# The deployment requires the API key to be set as an environment variable.
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY environment variable is not set."
    echo "Please set it before deploying: export GEMINI_API_KEY='your_key_here'"
    exit 1
fi

# 2. Check if inside a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ Error: This is not a git repository. Cannot deploy."
    exit 1
fi


# --- Deployment Steps ---

echo "🚀 Preparing to deploy to Streamlit Cloud..."

# 1. Create/update the secrets.toml for Streamlit Cloud
# This securely passes the API key to the deployed application.
echo "🔑 Writing GEMINI_API_KEY to .streamlit/secrets.toml..."
echo "GEMINI_API_KEY = \"$GEMINI_API_KEY\"" > .streamlit/secrets.toml
echo "Secrets file updated."

# 2. Add all changes to git staging
echo "📦 Staging changes for commit..."
git add .

# 3. Commit the changes with a timestamp
# This creates a clear record of the deployment version.
echo "📝 Committing changes..."
COMMIT_MSG="Deploy update $(date +'%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# 4. Push the changes to the 'main' branch to trigger deployment
# Streamlit Cloud typically deploys from the main branch.
echo "☁️ Pushing to remote to trigger deployment..."
git push origin main

echo "✅ Deployment triggered successfully!"
echo "🌐 Check your Streamlit Cloud dashboard to monitor the status."
