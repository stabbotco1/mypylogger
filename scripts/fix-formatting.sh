#!/bin/bash
# Fix all formatting issues in the mypylogger project
# This script ensures consistent formatting and prevents formatting loops

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔧 Fixing all formatting issues..."

# Auto-activate virtual environment if not active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Virtual environment not active, attempting auto-activation...${NC}"
    
    # Try common virtual environment locations
    local venv_paths=("venv/bin/activate" ".venv/bin/activate" "env/bin/activate")
    local venv_activated=false
    
    for venv_path in "${venv_paths[@]}"; do
        if [[ -f "$venv_path" ]]; then
            echo "Found virtual environment at $venv_path"
            source "$venv_path"
            if [[ -n "$VIRTUAL_ENV" ]]; then
                echo -e "${GREEN}✅ Virtual environment activated: $VIRTUAL_ENV${NC}"
                venv_activated=true
                break
            fi
        fi
    done
    
    if [[ "$venv_activated" == "false" ]]; then
        echo -e "${RED}❌ No virtual environment found${NC}"
        echo "Please activate your virtual environment first:"
        echo "  source venv/bin/activate"
        exit 1
    fi
fi

# Verify tools are available
for tool in black isort; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo -e "${RED}❌ $tool not found${NC}"
        echo "Installing development dependencies..."
        pip install -e ".[dev]"
        break
    fi
done

echo -e "${BLUE}Step 1: Running Black formatter...${NC}"
black .

echo -e "${BLUE}Step 2: Running isort import sorter...${NC}"
isort .

echo -e "${BLUE}Step 3: Verifying formatting is correct...${NC}"

# Check Black
if black --check --diff . >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Black formatting: PASSED${NC}"
else
    echo "❌ Black formatting: FAILED"
    echo "Running Black one more time..."
    black .
fi

# Check isort
if isort --check-only --diff . >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Import sorting: PASSED${NC}"
else
    echo "❌ Import sorting: FAILED"
    echo "Running isort one more time..."
    isort .
fi

echo -e "${GREEN}🎉 All formatting issues fixed!${NC}"
echo ""
echo "You can now run the test suite:"
echo "  ./scripts/run-complete-test-suite.sh --fast"