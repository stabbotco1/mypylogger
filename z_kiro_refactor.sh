#!/bin/bash
# kiro-refactor.sh
# Refactors .kiro directory structure to separate core from infrastructure
# and eliminate namespace confusion between specs/steering and .kiro/steering

set -euo pipefail

KIRO_DIR=".kiro"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Kiro Directory Refactoring ===${NC}"
echo ""

# Verify we're in project root
if [[ ! -d "$KIRO_DIR" ]]; then
    echo -e "${RED}ERROR: $KIRO_DIR directory not found${NC}"
    echo "Run this script from project root"
    exit 1
fi

# Create backup
BACKUP_DIR=".kiro.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}Creating backup: $BACKUP_DIR${NC}"
cp -r "$KIRO_DIR" "$BACKUP_DIR"
echo -e "${GREEN}✓ Backup created${NC}"
echo ""

# Create new directory structure
echo -e "${YELLOW}Creating new directory structure...${NC}"
mkdir -p "$KIRO_DIR/specs/core"
mkdir -p "$KIRO_DIR/specs/infrastructure"
mkdir -p "$KIRO_DIR/steering/language"
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Move core specs
echo -e "${YELLOW}Moving core library specs...${NC}"
mv "$KIRO_DIR/specs/requirements.md" "$KIRO_DIR/specs/core/requirements.md"
mv "$KIRO_DIR/specs/design.md" "$KIRO_DIR/specs/core/design.md"
mv "$KIRO_DIR/specs/tasks.md" "$KIRO_DIR/specs/core/tasks.md"
mv "$KIRO_DIR/specs/steering/logging-standards.md" "$KIRO_DIR/specs/core/standards.md"
echo -e "${GREEN}✓ Core specs moved${NC}"
echo ""

# Move infrastructure specs
echo -e "${YELLOW}Moving infrastructure specs...${NC}"
mv "$KIRO_DIR/specs/project-maturation/requirements.md" "$KIRO_DIR/specs/infrastructure/requirements.md"
mv "$KIRO_DIR/specs/project-maturation/design.md" "$KIRO_DIR/specs/infrastructure/design.md"
mv "$KIRO_DIR/specs/project-maturation/tasks.md" "$KIRO_DIR/specs/infrastructure/tasks.md"
echo -e "${GREEN}✓ Infrastructure specs moved${NC}"
echo ""

# Remove empty directories
echo -e "${YELLOW}Cleaning up empty directories...${NC}"
rmdir "$KIRO_DIR/specs/steering"
rmdir "$KIRO_DIR/specs/project-maturation"
echo -e "${GREEN}✓ Empty directories removed${NC}"
echo ""

# Rename steering documents with numbered prefixes
echo -e "${YELLOW}Renaming steering documents...${NC}"
mv "$KIRO_DIR/steering/kiro-workflow-patterns.md" "$KIRO_DIR/steering/01-kiro-workflow.md"
mv "$KIRO_DIR/steering/git-workflow-standards.md" "$KIRO_DIR/steering/02-git-workflow.md"
mv "$KIRO_DIR/steering/development-standards.md" "$KIRO_DIR/steering/03-development.md"
mv "$KIRO_DIR/steering/ci-cd-standards.md" "$KIRO_DIR/steering/04-ci-cd.md"
mv "$KIRO_DIR/steering/project-governance.md" "$KIRO_DIR/steering/05-governance.md"
mv "$KIRO_DIR/steering/task-completion-verification.md" "$KIRO_DIR/steering/06-task-verification.md"
mv "$KIRO_DIR/steering/kiro-learning-objectives.md" "$KIRO_DIR/steering/07-learning.md"
echo -e "${GREEN}✓ Steering documents renamed${NC}"
echo ""

# Create MANIFEST.md
echo -e "${YELLOW}Creating specs/MANIFEST.md...${NC}"
cat > "$KIRO_DIR/specs/MANIFEST.md" << 'EOF'
# Kiro Specs Manifest

## Purpose
This manifest defines the execution order and dependencies between specification documents for the mypylogger project.

## Active Specifications

### Core Library (Phase 1 - Completed)
Foundation library functionality built in ~6 hours with clean TDD approach.

**Execution Order:**
1. `core/requirements.md` - Library functionality requirements (EARS format)
2. `core/design.md` - Architecture and implementation design
3. `core/standards.md` - Product standards (JSON format, naming conventions, behavior)
4. `core/tasks.md` - Implementation task breakdown

**Status:** ✅ Complete
**Dependencies:** None - this is the foundation

### Infrastructure (Phase 2 - In Progress)
Production-readiness features retrofitted over ~14 hours.

**Execution Order:**
1. `infrastructure/requirements.md` - CI/CD, security, packaging requirements
2. `infrastructure/design.md` - Pipeline architecture and deployment strategy
3. `infrastructure/tasks.md` - Infrastructure implementation tasks

**Status:** 🔄 In Progress (Tasks 1-8 complete, 9-16 remaining)
**Dependencies:** Requires core library completion

## Specification Dependencies

```
core/requirements.md (no dependencies)
    ↓
core/design.md (depends on: core/requirements.md)
    ↓
core/standards.md (depends on: core/design.md)
    ↓
core/tasks.md (depends on: core/design.md, core/standards.md)
    ↓
    [CORE COMPLETE]
    ↓
infrastructure/requirements.md (depends on: core completion)
    ↓
infrastructure/design.md (depends on: infrastructure/requirements.md)
    ↓
infrastructure/tasks.md (depends on: infrastructure/design.md)
```

## Task Execution Rules

1. **Sequential Execution**: Complete core specs before infrastructure specs
2. **Single Source of Truth**: Task checkboxes exist ONLY in tasks.md files
3. **Verification Required**: Run `make test-complete-fast` after each task
4. **No Parallel Work**: Complete one spec layer before moving to next

## Meta-Notes on Spec Organization

This two-phase separation emerged from retrospective analysis:
- **Core library** was built cleanly using spec-first TDD
- **Infrastructure** was retrofitted, causing significant churn
- **Future projects** should plan both phases from Day 1
- This separation prevents scope creep from masquerading as "maturity"

## Related Documentation

**Steering Documents** (process guidance):
- `.kiro/steering/01-kiro-workflow.md` - Spec-driven development workflow
- `.kiro/steering/02-git-workflow.md` - Version control standards
- `.kiro/steering/03-development.md` - Local development practices
- `.kiro/steering/04-ci-cd.md` - CI/CD pipeline standards
- `.kiro/steering/05-governance.md` - Quality and compliance standards
- `.kiro/steering/06-task-verification.md` - Task completion verification
- `.kiro/steering/07-learning.md` - Meta-learning and knowledge extraction

**Language-Specific Standards**:
- `.kiro/steering/language/python-standards.md` - Python development conventions

---

Last Updated: [Date of refactoring]
Status: Active development on infrastructure phase
EOF
echo -e "${GREEN}✓ MANIFEST.md created${NC}"
echo ""

# Create language-specific steering placeholder
echo -e "${YELLOW}Creating language-specific steering structure...${NC}"
cat > "$KIRO_DIR/steering/language/python-standards.md" << 'EOF'
# Python Development Standards

## Purpose
Python-specific development conventions, tools, and best practices for this project.

## Standards

### Code Style
- **Black**: Line length 88, Python 3.8+ target
- **isort**: Profile "black", multi-line output 3
- **flake8**: Max line length 88, extend-ignore for Black compatibility
- **mypy**: Python 3.8, strict optional, warn on unused configs

### Project Structure
- Package in `mypylogger/` directory
- Tests in `tests/` directory
- Build artifacts in `build/`, `dist/`
- Virtual environment in `venv/`

### Dependencies
- Core: `python-json-logger>=2.0.0`
- Dev: pytest, black, isort, flake8, mypy, bandit, safety

### Testing
- Minimum coverage: 90%
- Test naming: `test_*.py` files, `Test*` classes, `test_*` functions
- Fixtures in `conftest.py`

See `.kiro/specs/core/standards.md` for product-specific standards (JSON format, logging behavior, etc.)
EOF
echo -e "${GREEN}✓ Language-specific steering created${NC}"
echo ""

# Summary
echo -e "${GREEN}=== Refactoring Complete ===${NC}"
echo ""
echo "New structure:"
echo "  .kiro/specs/core/          - Base library specs"
echo "  .kiro/specs/infrastructure/ - Production readiness specs"
echo "  .kiro/specs/MANIFEST.md     - Spec dependencies and order"
echo "  .kiro/steering/01-07-*.md   - Numbered process steering"
echo "  .kiro/steering/language/    - Language-specific standards"
echo ""
echo -e "${YELLOW}Backup location: $BACKUP_DIR${NC}"
echo ""
echo "Next steps:"
echo "  1. Review changes with: git diff"
echo "  2. Update any broken cross-references in documents"
echo "  3. Test with Kiro agent to verify navigation works"
echo "  4. Commit changes: git add .kiro && git commit -m 'refactor: reorganize .kiro directory structure'"
echo ""
