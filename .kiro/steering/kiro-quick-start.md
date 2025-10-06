# Kiro Quick Start Guide

**Purpose**: Get started with a new Claude session in under 2 minutes

## Starting a New Session

### 1. Orient Yourself (30 seconds)

Check project state: cat .kiro/PROJECT_STATE.md
See active tasks: cat .kiro/CURRENT_TASKS.md

### 2. Share Context with Claude (30 seconds)

Say to Claude:
"I'm working on mypylogger. Please read .kiro/PROJECT_STATE.md and .kiro/CURRENT_TASKS.md to understand current status."

### 3. Pick Your Work (30 seconds)

Choose from CURRENT_TASKS.md:
- Next sequential task, OR
- High-priority blocked item, OR
- Bug fix / urgent issue

### 4. Execute Task (varies)

Follow the standard workflow:
1. Activate venv: source venv/bin/activate
2. Check git status: git status
3. Create feature branch if needed: git checkout -b task-N-description
4. Write code/tests
5. Run quality checks: ./scripts/pre-release-check.sh
6. Commit and push
7. Update CURRENT_TASKS.md when complete

## Common Commands

- Activate environment: source venv/bin/activate
- Run tests: pytest -v
- Run all quality checks: ./scripts/pre-release-check.sh
- Check CI status: gh run list --limit 5
- Format code: black . && isort .
- View kiro structure: tree .kiro/

## When to Read More Documentation

- First time using Kiro? Read .kiro/steering/kiro-reference.md
- Need coding standards? Read .kiro/steering/project-standards.md
- Python-specific questions? Read .kiro/steering/language/python-standards.md
- Need spec details? Read .kiro/specs/MANIFEST.md

## Emergency: "Claude is Confused"

If Claude seems lost or gives contradictory advice:

1. Stop and re-orient: Share PROJECT_STATE.md and CURRENT_TASKS.md again
2. Check for stale context: Is Claude referencing archived files?
3. Start fresh session: If context is corrupted, start new chat
4. Report issue: Note what caused confusion to improve docs

## Key Principles

- One source of truth: CURRENT_TASKS.md is THE task list
- Specs are read-only: They define the plan, don't edit during execution
- Update as you go: Keep CURRENT_TASKS.md current
- CI is the judge: Task isn't done until CI passes
