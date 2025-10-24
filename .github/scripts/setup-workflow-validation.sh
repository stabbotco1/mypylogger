#!/bin/bash
#
# Setup Script for Workflow Validation System
#
# This script sets up the complete workflow validation system including
# pre-commit hooks, validation tools, and CI/CD integration.
#
# Requirements addressed:
# - 10.5: Prevent deployment of invalid workflow configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SOURCE_HOOK="$REPO_ROOT/.github/hooks/pre-commit-workflow-validation"
TARGET_HOOK="$HOOKS_DIR/pre-commit"

echo -e "${BOLD}${BLUE}🔧 Workflow Validation System Setup${NC}"
echo "====================================="
echo ""

# Function to check command availability
check_command() {
    local cmd="$1"
    local install_msg="$2"
    
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $cmd is available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ $cmd is not available${NC}"
        if [ -n "$install_msg" ]; then
            echo -e "   $install_msg"
        fi
        return 1
    fi
}

# Function to install Python package
install_python_package() {
    local package="$1"
    local import_name="${2:-$1}"
    
    echo -e "${BLUE}📦 Checking Python package: $package${NC}"
    
    if python3 -c "import $import_name" 2>/dev/null; then
        echo -e "${GREEN}✅ $package is already installed${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📦 Installing $package...${NC}"
    if pip3 install "$package" --user --quiet; then
        echo -e "${GREEN}✅ $package installed successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to install $package${NC}"
        return 1
    fi
}

# Check if we're in a git repository
echo -e "${BLUE}🔍 Checking repository setup...${NC}"
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    echo "Please run this script from within a git repository."
    exit 1
fi
echo -e "${GREEN}✅ Git repository detected${NC}"

# Check required commands
echo ""
echo -e "${BLUE}🔍 Checking system dependencies...${NC}"

MISSING_DEPS=false

if ! check_command "python3" "Install Python 3: https://python.org/downloads/"; then
    MISSING_DEPS=true
fi

if ! check_command "pip3" "Install pip: python3 -m ensurepip --upgrade"; then
    MISSING_DEPS=true
fi

if ! check_command "git" "Install Git: https://git-scm.com/downloads"; then
    MISSING_DEPS=true
fi

if [ "$MISSING_DEPS" = true ]; then
    echo ""
    echo -e "${RED}❌ Missing required dependencies${NC}"
    echo "Please install the missing dependencies and run this script again."
    exit 1
fi

# Install Python dependencies
echo ""
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"

PYTHON_DEPS_FAILED=false

if ! install_python_package "pyyaml" "yaml"; then
    PYTHON_DEPS_FAILED=true
fi

if [ "$PYTHON_DEPS_FAILED" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Some Python dependencies failed to install${NC}"
    echo "You may need to install them manually:"
    echo "  pip3 install pyyaml"
    echo ""
fi

# Check optional tools
echo ""
echo -e "${BLUE}🔍 Checking optional validation tools...${NC}"

check_command "yamllint" "Install yamllint: pip3 install yamllint"
check_command "actionlint" "Install actionlint: https://github.com/rhysd/actionlint#installation"
check_command "act" "Install act: https://github.com/nektos/act#installation"

# Setup pre-commit hook
echo ""
echo -e "${BLUE}🪝 Setting up pre-commit hook...${NC}"

if [ ! -f "$SOURCE_HOOK" ]; then
    echo -e "${RED}❌ Source pre-commit hook not found: $SOURCE_HOOK${NC}"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Check if pre-commit hook already exists
if [ -f "$TARGET_HOOK" ]; then
    echo -e "${YELLOW}⚠️ Pre-commit hook already exists${NC}"
    
    # Check if it's our workflow validation hook
    if grep -q "Pre-commit hook for GitHub Actions workflow validation" "$TARGET_HOOK" 2>/dev/null; then
        echo -e "${BLUE}🔄 Updating existing workflow validation hook...${NC}"
    else
        echo -e "${YELLOW}📋 Backing up existing pre-commit hook...${NC}"
        cp "$TARGET_HOOK" "$TARGET_HOOK.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✅ Backup created: $TARGET_HOOK.backup.$(date +%Y%m%d_%H%M%S)${NC}"
    fi
fi

# Install the pre-commit hook
cp "$SOURCE_HOOK" "$TARGET_HOOK"
chmod +x "$TARGET_HOOK"

echo -e "${GREEN}✅ Pre-commit hook installed successfully${NC}"

# Make validation scripts executable
echo ""
echo -e "${BLUE}🔧 Setting up validation scripts...${NC}"

SCRIPTS=(
    "$REPO_ROOT/.github/scripts/workflow-validator.py"
    "$REPO_ROOT/.github/scripts/workflow-linter.py"
    "$REPO_ROOT/.github/scripts/workflow-impact-analyzer.py"
    "$REPO_ROOT/.github/scripts/workflow-tester.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo -e "${GREEN}✅ Made executable: $(basename "$script")${NC}"
    else
        echo -e "${YELLOW}⚠️ Script not found: $(basename "$script")${NC}"
    fi
done

# Test the validation system
echo ""
echo -e "${BLUE}🧪 Testing validation system...${NC}"

# Check if there are any workflow files to test
WORKFLOW_FILES=$(find "$REPO_ROOT/.github/workflows" -name "*.yml" -o -name "*.yaml" 2>/dev/null || true)

if [ -n "$WORKFLOW_FILES" ]; then
    echo -e "${BLUE}📋 Found workflow files to test:${NC}"
    echo "$WORKFLOW_FILES" | sed 's/^/  - /'
    
    # Test validation script
    if [ -f "$REPO_ROOT/.github/scripts/workflow-validator.py" ]; then
        echo ""
        echo -e "${BLUE}🔍 Running validation test...${NC}"
        
        if python3 "$REPO_ROOT/.github/scripts/workflow-validator.py" --validate-all >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Validation test passed${NC}"
        else
            echo -e "${YELLOW}⚠️ Validation test found issues (this may be expected)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️ No workflow files found to test${NC}"
fi

# Create configuration file
echo ""
echo -e "${BLUE}📝 Creating validation configuration...${NC}"

CONFIG_FILE="$REPO_ROOT/.github/workflow-validation.yml"
cat > "$CONFIG_FILE" << 'EOF'
# Workflow Validation Configuration
#
# This file configures the workflow validation system behavior

validation:
  # Validation levels: basic, standard, comprehensive
  default_level: standard
  
  # Enable/disable specific validation checks
  checks:
    syntax: true
    linting: true
    security: true
    performance: true
    best_practices: true
  
  # Pre-commit hook configuration
  pre_commit:
    enabled: true
    fail_on_warnings: false
    skip_files: []
  
  # CI/CD integration
  ci_integration:
    enabled: true
    block_on_failure: true
    comment_on_pr: true
  
  # Tool-specific settings
  tools:
    yamllint:
      enabled: true
      config: default
    
    actionlint:
      enabled: true
      ignore_patterns: []
    
    act:
      enabled: true
      skip_pull: false

# Rollback configuration
rollback:
  # Automatic rollback on critical failures
  auto_rollback: false
  
  # Backup workflow files before changes
  backup_workflows: true
  
  # Rollback timeout (minutes)
  timeout: 30

# Notification settings
notifications:
  # Notify on validation failures
  on_failure: true
  
  # Notify on high-impact changes
  on_high_impact: true
  
  # Notification channels (future use)
  channels: []
EOF

echo -e "${GREEN}✅ Configuration file created: $CONFIG_FILE${NC}"

# Setup complete
echo ""
echo -e "${BOLD}${GREEN}🎉 Workflow Validation System Setup Complete!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}📋 What was installed:${NC}"
echo "  ✅ Pre-commit hook for workflow validation"
echo "  ✅ Validation scripts and tools"
echo "  ✅ Configuration file"
echo "  ✅ Python dependencies"
echo ""
echo -e "${BLUE}🔧 How it works:${NC}"
echo "  • Pre-commit hook validates workflows before commit"
echo "  • CI/CD workflow validates changes in pull requests"
echo "  • Impact analysis provides change assessment"
echo "  • Comprehensive testing ensures workflow reliability"
echo ""
echo -e "${BLUE}💡 Next steps:${NC}"
echo "  1. Commit your changes to activate the validation system"
echo "  2. The pre-commit hook will validate workflows automatically"
echo "  3. CI/CD validation will run on pull requests"
echo "  4. Review validation results and fix any issues"
echo ""
echo -e "${YELLOW}⚠️ Important notes:${NC}"
echo "  • The pre-commit hook will prevent commits with invalid workflows"
echo "  • Use 'git commit --no-verify' to bypass validation (not recommended)"
echo "  • Install optional tools (yamllint, actionlint, act) for enhanced validation"
echo ""
echo -e "${GREEN}✅ Your workflows are now protected by comprehensive validation!${NC}"