#!/bin/bash
# Pre-commit hook to prevent direct commits to main branch

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "main" ]; then
    echo "❌ ERROR: Direct commits to main branch are not allowed!"
    echo "Please create a feature branch:"
    echo "  git checkout -b feature/your-feature-name"
    echo "  git add ."
    echo "  git commit -m 'your commit message'"
    echo ""
    echo "Then create a pull request to merge to main."
    exit 1
fi

exit 0
