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
