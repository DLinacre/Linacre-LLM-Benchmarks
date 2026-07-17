#!/bin/bash

# A script to automatically approve and merge all open Dependabot PRs 
# across your specified GitHub repositories.
# Requires GitHub CLI (gh) to be installed and authenticated.

REPOS=(
  "LIN4CRE/smart-mail"
  "LIN4CRE/LinacreUninstaller"
  "LIN4CRE/Linacre-LLM-Benchmarks"
  "LIN4CRE/KushCloud"
)

echo "Starting Dependabot PR merge script..."

for REPO in "${REPOS[@]}"; do
  echo "----------------------------------------"
  echo "Checking $REPO for Dependabot PRs..."
  
  # Fetch all open PRs authored by dependabot
  PRS=$(gh pr list --repo "$REPO" --author "app/dependabot" --state open --json number --jq '.[].number')
  
  if [ -z "$PRS" ]; then
    echo "No open Dependabot PRs found in $REPO."
    continue
  fi

  for PR in $PRS; do
    echo "Processing PR #$PR in $REPO..."
    
    # Optional: Approve the PR before merging
    gh pr review "$PR" --repo "$REPO" --approve -b "Auto-approved via script" 2>/dev/null
    
    # Merge the PR (squash merge by default, you can change to --merge or --rebase)
    gh pr merge "$PR" --repo "$REPO" --squash --auto --delete-branch
    
    if [ $? -eq 0 ]; then
      echo "✅ Successfully merged PR #$PR"
    else
      echo "❌ Failed to merge PR #$PR"
    fi
  done
done

echo "----------------------------------------"
echo "All done!"