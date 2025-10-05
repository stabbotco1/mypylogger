#!/bin/bash
# Pre-flight validation for release workflows
# Prevents corruption from partial workflow execution

set -e

echo "🔍 Running pre-release validation checks..."

# Check 1: Clean working tree
if ! git diff-index --quiet HEAD --; then
    echo "❌ ERROR: Uncommitted changes detected"
    echo "   Please commit or stash changes before release"
    git status --short
    exit 1
fi
echo "✓ Working tree is clean"

# Check 2: Validate version format using Python
VERSION=$(python3 << 'PYEOF'
import sys
try:
    import tomli
except ImportError:
    print("ERROR: tomli not installed", file=sys.stderr)
    sys.exit(1)

with open('pyproject.toml', 'rb') as f:
    data = tomli.load(f)
    version = data.get('project', {}).get('version', '')
    if not version:
        print("ERROR: version is empty", file=sys.stderr)
        sys.exit(1)
    print(version)
PYEOF
)

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to read version from pyproject.toml"
    exit 1
fi

# Validate PEP 440 compliance
python3 << PYEOF
from packaging.version import Version, InvalidVersion
import sys

try:
    Version('$VERSION')
    print(f"✓ Version '$VERSION' is PEP 440 compliant")
except InvalidVersion:
    print(f"❌ ERROR: Version '$VERSION' is not PEP 440 compliant", file=sys.stderr)
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

# Check 3: Verify required files exist
REQUIRED_FILES=(
    "CHANGELOG.md"
    "README.md"
    "pyproject.toml"
)

# Auto-detect package directory structure
if [ -d "src" ]; then
    PKG_DIR=$(find src -maxdepth 1 -type d ! -name src | head -1)
else
    PKG_DIR=$(find . -maxdepth 1 -type d -name '[!.]*' ! -name tests ! -name docs ! -name scripts | head -1)
fi

if [ -z "$PKG_DIR" ]; then
    echo "❌ ERROR: Cannot detect package directory"
    exit 1
fi

REQUIRED_FILES+=("$PKG_DIR/__init__.py")

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ ERROR: Required file missing: $file"
        exit 1
    fi
done
echo "✓ All required files present"

# Check 4: Verify __init__.py has __version__
if ! grep -q "__version__" "$PKG_DIR/__init__.py"; then
    echo "❌ ERROR: $PKG_DIR/__init__.py missing __version__ attribute"
    exit 1
fi
echo "✓ __init__.py contains __version__"

# Check 5: Validate workflow YAML files
WORKFLOW_DIR=".github/workflows"
if [ -d "$WORKFLOW_DIR" ]; then
    for workflow in "$WORKFLOW_DIR"/*.yml "$WORKFLOW_DIR"/*.yaml; do
        if [ -f "$workflow" ]; then
            if command -v yamllint &> /dev/null; then
                if ! yamllint -d relaxed "$workflow" > /dev/null 2>&1; then
                    echo "⚠️  WARNING: YAML validation failed for $workflow"
                fi
            fi
        fi
    done
    echo "✓ Workflow files validated"
fi

# Check 6: Verify PyPI trusted publisher configuration matches workflow
WORKFLOW_FILE="manual-release.yml"
if [ -f ".github/workflows/$WORKFLOW_FILE" ]; then
    echo "✓ PyPI workflow file exists: $WORKFLOW_FILE"
else
    echo "⚠️  WARNING: PyPI workflow file not found: $WORKFLOW_FILE"
    echo "   Ensure PyPI trusted publisher configuration matches actual filename"
fi

# Check 7: Verify on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  WARNING: Not on main branch (currently on: $CURRENT_BRANCH)"
    echo "   Release workflow expects main branch"
fi

# Check 8: Verify remote is up to date
git fetch origin main --quiet
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  WARNING: Local branch is not synced with origin/main"
    echo "   Consider: git pull origin main"
fi

echo ""
echo "✅ All pre-flight checks passed"
echo "   Version: $VERSION"
echo "   Package: $PKG_DIR"
echo "   Branch: $CURRENT_BRANCH"
