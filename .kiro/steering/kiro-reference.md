# Kiro Reference Manual

**Purpose**: Detailed workflow patterns and advanced usage

## What is Kiro?

Kiro is a structured approach to working with Claude on software projects. It provides:
- Clear specifications (what to build)
- Organized tasks (tracking progress)
- Standard workflows (how to execute)
- Quality gates (ensuring correctness)

## Core Philosophy

### Separation of Concerns
- Specs define WHAT to build (read-only during execution)
- Tasks track WHERE you are (updated frequently)
- Standards define HOW to build (consistent quality)
- State documents show CURRENT status

### Single Source of Truth
- One file per concern
- No duplicate information
- Clear authority hierarchy
- Archive old information

### Empirical Validation
- CI passing = task complete
- Measurements over estimates
- Working code over documentation
- Real deployments validate design

## Session Workflow Patterns

### Pattern 1: Continuing Active Work

Start of session:
1. Claude reads PROJECT_STATE.md and CURRENT_TASKS.md
2. You pick next incomplete task
3. Execute task following project-standards.md
4. Update CURRENT_TASKS.md when done
5. Commit with appropriate message format

### Pattern 2: Starting New Phase

When beginning a new project phase:
1. Review MANIFEST.md for phase overview
2. Read phase requirements.md (understand WHAT)
3. Read phase design.md (understand HOW)
4. Break work into tasks in CURRENT_TASKS.md
5. Execute tasks sequentially
6. Update PROJECT_STATE.md when phase completes

### Pattern 3: Bug Fix / Urgent Issue

For unplanned work:
1. Create task in CURRENT_TASKS.md under "Active Work"
2. Mark as high priority if needed
3. Fix issue following standards
4. Update CURRENT_TASKS.md when complete
5. Don't skip quality gates even for "quick fixes"

### Pattern 4: Exploratory / Research Work

For investigation or proof-of-concept:
1. Create research task in CURRENT_TASKS.md
2. Document findings as you go
3. If pursuing: convert to proper spec
4. If abandoning: document why in task notes
5. Archive or delete experimental code

## Task Management

### Task Lifecycle

States:
- Active Work: Currently being executed
- Blocked: Cannot proceed (document blocker)
- Recently Completed: Done in last 5 tasks
- Archived: Historical tasks moved to archive/

### Task Completion Criteria

A task is complete when:
1. Acceptance criteria met
2. Tests written and passing
3. Code formatted and linted
4. Documentation updated
5. CI pipeline passes
6. Changes committed to main

NOT complete if any of above fail, even if "it works on my machine"

### Updating CURRENT_TASKS.md

When completing task:
- Update "Last Updated" date
- Move from Active → Recently Completed
- Add completion date
- Keep only last 5 in Recently Completed
- Move older items to archive/tasks/

## Working with Claude

### Effective Context Sharing

Good:
- "Read PROJECT_STATE.md and CURRENT_TASKS.md"
- "I'm working on task 9, here's the error I'm seeing"
- "Review this code for issues"

Bad:
- No context, expecting Claude to remember
- Assuming Claude knows project history
- Not mentioning which task you're on

### When Claude Gets Confused

Signs of confusion:
- References archived/deleted files
- Gives contradictory advice
- Can't locate current task
- Suggests already-completed work

Solutions:
1. Re-share PROJECT_STATE.md and CURRENT_TASKS.md
2. Explicitly state which task you're on
3. If confusion persists, start fresh session
4. Note what caused confusion to improve docs

### Prompting Patterns

For code generation:
"Generate [component] for task N. It should [requirements]. Follow standards in project-standards.md."

For debugging:
"Task N: Getting [error]. Here's my code [paste]. What's wrong?"

For review:
"Review this implementation of task N against its requirements in [spec file]."

## Git Integration

### Branch Naming

Format: task-N-brief-description

Examples:
- task-9-regression-tracking
- fix-badge-caching
- refactor-perf-benchmarks

### Commit Workflow

Standard flow:
1. Make changes
2. Run formatters: black . && isort .
3. Run tests: pytest -v --cov
4. Stage: git add [files]
5. Commit: git commit -m "type: description"
6. Push: git push
7. Verify CI passes

### Handling CI Failures

If CI fails:
1. Read the failure logs carefully
2. Fix locally
3. Re-run quality checks
4. Commit fix
5. Push again
6. Task isn't done until CI passes

Never:
- Skip CI to "save time"
- Commit with "fix later" comment
- Merge despite failing checks

## Quality Assurance

### Pre-Commit Checks

Always run before committing:
- Formatters (black, isort)
- Linters (flake8)
- Type checker (mypy)
- Security (bandit)
- Tests (pytest with coverage)

Or use: ./scripts/pre-release-check.sh

### Performance Validation

For performance-sensitive code:
1. Run scripts/measure_performance.py
2. Compare to requirements (0.1ms, 10K logs/sec)
3. If regression: investigate before committing
4. Document trade-offs if accepting regression

### Security Review

Before committing:
- No hardcoded secrets
- No commented-out credentials
- Dependencies up to date (pip-audit)
- Bandit scan passes

## Release Process

### Pre-Release Checklist

1. All tasks in phase complete
2. All CI checks passing
3. Coverage >= 90%
4. Performance within requirements
5. Security scans clean
6. Documentation updated
7. CHANGELOG accurate

### Triggering Release

Via GitHub Actions:
1. Go to Actions tab
2. Select "Manual Release to PyPI"
3. Click "Run workflow"
4. Leave version empty (auto-increment) or specify
5. Monitor progress (3-5 minutes)
6. Verify on PyPI

### Post-Release

1. Update PROJECT_STATE.md with new version
2. Update CURRENT_TASKS.md if applicable
3. Archive completed phase specs if phase done
4. Begin next phase or task

## Common Patterns

### Adding a New Feature

1. Create spec in .kiro/specs/[feature-name]/
2. Write requirements.md (WHAT)
3. Write design.md (HOW)
4. Break into tasks in CURRENT_TASKS.md
5. Execute tasks
6. Update PROJECT_STATE.md when done

### Fixing a Bug

1. Add to CURRENT_TASKS.md if not trivial
2. Write failing test first
3. Fix bug
4. Verify test passes
5. Run full quality checks
6. Commit and update tasks

### Refactoring

1. Ensure tests exist and pass
2. Make refactoring changes
3. Verify tests still pass
4. Run performance benchmarks
5. Commit if no regressions

### Documentation Updates

1. Update relevant files
2. Verify markdown valid
3. Check links work
4. Run documentation validation
5. Commit with "docs:" prefix

## Troubleshooting

### "Task won't complete"

Check:
- Did CI pass?
- Did you update CURRENT_TASKS.md?
- Did you commit all changes?
- Are acceptance criteria actually met?

### "Can't find specification"

Check:
- MANIFEST.md for current active spec
- Might be archived if phase complete
- PROJECT_STATE.md shows current phase

### "Conflicting requirements"

Check:
- Which spec is active per MANIFEST.md?
- Are you reading archived docs?
- Is there a newer version of the spec?

### "Claude is confused"

Check:
- Did you share current state docs?
- Are you referencing archived files?
- Is session context too long?
- Start fresh session if needed

## Advanced Topics

### Template Extraction

When ready to create reusable template:
1. Complete infrastructure phase
2. Review all specs and tasks
3. Identify project-specific vs reusable
4. Create template structure
5. Document customization points
6. Test on new project (OIDC library)

### Multi-Phase Projects

For projects with multiple phases:
1. Define all phases in MANIFEST.md
2. Complete phases sequentially
3. Archive completed phase specs
4. Update PROJECT_STATE.md between phases
5. Maintain single CURRENT_TASKS.md across phases
