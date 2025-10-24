# Product Overview

## mypylogger v0.2.0

A Python logging library designed to provide enhanced logging capabilities. This is version 0.2.0 of the mypylogger project, representing a significant update with modern Python practices and improved functionality.

## Vision

Create a **zero-dependency JSON logging library with sensible defaults** for Python applications. mypylogger v0.2.0 does ONE thing exceptionally well: structured JSON logs that work everywhere—from local development to AWS Lambda to Kubernetes.

## Core Value Proposition

**What makes mypylogger different:**
1. **Minimal Dependencies** (only `python-json-logger`)
   - Works in restricted environments (Lambda, containers, air-gapped systems)
   - Minimal attack surface, fast installation
   - No transitive dependency hell

2. **Clean, Predictable JSON Output**
   - Flat structure, consistent key ordering (timestamp always first)
   - Human-readable AND machine-parseable
   - Ready for Splunk, Dynatrace, CloudWatch without transformation

3. **Developer-Friendly Defaults**
   - Works out-of-box with minimal configuration
   - Environment-driven config (no code changes for different environments)
   - Immediate flush for real-time monitoring during development

4. **Standard Python Patterns**
   - Uses stdlib `logging.getLogger(__name__)` pattern
   - Not a singleton (properly handles per-module loggers)
   - Compatible with existing Python logging ecosystem

## Development Approach

The project follows a **phased development methodology** with strict gates between phases. Each phase must be 100% complete before proceeding to the next phase.

## Development Phases

### Phase 1: Project Foundation
**Objective**: Establish complete project infrastructure
- Project structure and organization
- Development tooling configuration (UV, Ruff, pytest, mypy)
- Quality gates and testing infrastructure
- Basic project scaffolding

**Gate Criteria**: Complete project structure, all tooling configured, basic tests passing

### Phase 2: Core Functionality
**Objective**: Implement the core logging library
- Python logging package implementation
- Core logging features and capabilities
- Comprehensive test suite (95%+ coverage)
- Package ready for distribution

**Gate Criteria**: Full logging functionality implemented, 95%+ test coverage, ready for distribution

### Phase 3: CI/CD Integration
**Objective**: Implement automated quality and deployment pipelines
- GitHub Actions CI/CD workflows
- Automated testing, scanning, and quality gates
- Feature branch protection and merge requirements
- Automated quality enforcement

**Gate Criteria**: All CI/CD workflows operational, feature branch protection enforced

### Phase 4: Documentation & Publishing
**Objective**: Complete documentation and establish publishing workflow
- Comprehensive user documentation
- API documentation and examples
- Manual GitHub release action for PyPI publishing
- Publication workflow established

**Gate Criteria**: Complete documentation, successful PyPI publication process

## Design Principles

### 1. Simplicity Over Features
- **One clear purpose:** JSON logging
- **Obvious defaults:** Should work with zero configuration
- **Minimal API surface:** `get_logger(__name__)` and standard logging methods
- **No magic:** Explicit is better than implicit

### 2. Reliability Over Performance
- **Immediate flush by default:** Reliability > 10x speed improvement
- **Graceful degradation:** Fall back to safe defaults when operations fail
- **Predictable behavior:** Same output format across all environments

### 3. Maintainability Over Completeness
- **Small codebase:** Easy to understand and maintain (<500 lines)
- **Stdlib-based:** Leverage Python's mature logging infrastructure
- **Clear boundaries:** External tools handle rotation, filtering, analysis

## Quality Standards

- **TDD Methodology**: Test-driven development throughout all phases
- **95% Test Coverage**: Minimum coverage requirement for all phases
- **Zero Tolerance**: No linting, style, or type errors allowed
- **Master Test Script**: All phases must pass `./scripts/run_tests.sh`
- **Git Workflow**: Conventional commits on main branch

## Success Metrics

**mypylogger v0.2.0 is successful if:**
1. **Installation:** `pip install mypylogger` → working logger in <1 minute
2. **Configuration:** Works with ZERO config, customizable via env vars
3. **Output:** Valid JSON, one line per entry, timestamp always first
4. **Reliability:** Logs are never lost due to crashes or termination
5. **Size:** Core library is <500 lines of code
6. **Dependencies:** Only `python-json-logger` + Python stdlib

## Project Status

See `.kiro/PROJECT_STATUS.md` for current phase progress and next actions.