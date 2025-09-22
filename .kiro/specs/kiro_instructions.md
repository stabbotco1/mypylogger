# File 1: kiro_instructions.md

# Purpose
This file provides explicit instructions to Kiro to generate the initial project documentation set.

# Instructions for Kiro
1. **Split out documents**  
   - Take the combined specifications provided in this repo and split them into individual `.md` files.  
   - Place them in the correct directories (`/`, `/tests`, `/docs`, `/steering`).  

2. **Tasks to Create Documentation**
   - `requirements.md` — detailed functional and non-functional requirements.  
   - `design.md` — detailed architecture and design decisions.  
   - `tasks.md` — enumerated tasks for building the project.  
   - `steering/logging-standards.md` — detailed logging conventions.  
   - `README.md` — project overview and usage summary.  
   - `CONTRIBUTING.md` — contribution guidelines.  
   - `tests/README.md` — testing philosophy and structure.  
   - `CONFIG.md` — full configuration options with environment variable descriptions.  
   - `USAGE.md` — usage examples, from basic logging to advanced scenarios.  
   - `ARCHITECTURE.md` — narrative architecture description.  
   - `EXTENDING.md` — how to extend with new handlers.  
   - `EXAMPLES.md` — runnable example descriptions.  
   - `ROADMAP.md` — planned roadmap with milestones.  
   - `SECURITY.md` — security reporting and patching policy.  
   - `CODE_OF_CONDUCT.md` — contributor conduct.  
   - `docs/ONBOARDING.md` — onboarding steps for new contributors.  
   - `docs/RELEASE.md` — release process and publishing workflow.  

3. **First Task**  
   - Generate all the above documents with detailed contents.  
   - Populate them with enough depth that they serve as a solid initial specification set for the `kiro_logging` project.  

---

# File 2: Detailed Initial Spec Documents

## requirements.md
### Functional Requirements
- Library shall provide JSON-formatted logging with consistent fields.  
- Must support multiple handlers: file, stdout, contrib.  
- Configuration driven entirely by environment variables.  
- Log files must flush immediately to disk.  
- Null values must be normalized to `"null"`.  
- Library must be thread-safe and usable across modules.  
- Must operate correctly in local development, Docker containers, and AWS Lambda.  

### Non-Functional Requirements
- High reliability: logging should never crash the host application.  
- Minimal latency overhead (< 1ms per log line).  
- Portable: no dependencies beyond standard library + `python-json-logger`.  
- Security: log sanitization options to prevent leaking secrets.  

---

## design.md
### Architecture
- **Singleton Logger**: ensures only one global logger is configured.  
- **Custom JSON Formatter**: normalizes fields, timestamps, nulls.  
- **Handlers**:  
  - FileHandler (ImmediateFlush).  
  - StreamHandler (stdout).  
  - Contrib handlers (AWS CloudWatch).  
- **Configuration**:  
  - Environment variables loaded at startup.  
  - Defaults for local development.  
- **Directory Layout**:  

src/core/...
src/contrib/...
steering/...
tests/...
docs/...


### Key Design Decisions
- JSON-only for consistency across platforms.  
- UTC timestamps in ISO8601 with milliseconds.  
- Environment-based flexibility for deployment contexts.  
- Steering documents drive coding and logging style.  

---

## tasks.md
### Phase 1: Documentation Setup
- Generate all stub `.md` documents in correct directories.  
- Populate with content based on combined specs.  

### Phase 2: Core Implementation
- Implement `SingletonLogger`.  
- Implement `CustomJsonFormatter`.  
- Implement `ImmediateFlushFileHandler`.  
- Implement `ParallelStdoutHandler`.  

### Phase 3: Extensions
- Add contrib `cloudwatch_handler.py`.  
- Provide examples for Lambda and containerized environments.  

### Phase 4: Testing
- Unit tests for each core component.  
- Integration tests for logger initialization and multiple handlers.  
- Mock-based tests for contrib modules.  

### Phase 5: Tooling
- Create `.gitignore`.  
- Add GitHub Actions workflow.  
- Create Makefile.  
- Create bootstrap script.  
- Add dev/prod Dockerfiles.  

---

## steering/logging-standards.md
### Logging Conventions
- All timestamps: UTC, ISO8601, millisecond precision.  
- Required fields: `time`, `levelname`, `message`, `filename`, `lineno`, `funcName`.  
- Optional fields: `taskName` (removed if unused).  
- Nulls replaced with string `"null"`.  
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.  
- `APP_NAME` prefixes log filenames.  
- Environment flags configure truncation (`EMPTY_LOG_FILE_ON_RUN`) and stdout mirroring (`PARALLEL_STDOUT_LOGGING`).  

---

## README.md
### Overview
`kiro_logging` is a production-ready Python logging library.  
It provides JSON logging, file/stdout handlers, and contrib integrations.  
It is designed for use across local, container, and cloud environments.  

### Features
- JSON logs with consistent schema.  
- Environment-driven configuration.  
- Immediate flush file handler.  
- Parallel stdout handler.  
- Extensible contrib modules.  

---

## CONTRIBUTING.md
### Contribution Guidelines
- All changes must include tests.  
- Update specs when requirements/design change.  
- Run `make all` before committing.  
- Follow logging standards from `steering/logging-standards.md`.  
- Open PRs with descriptive messages.  

---

## tests/README.md
### Testing Philosophy
- Unit tests validate core logic.  
- Integration tests simulate real-world usage.  
- Contrib handlers tested with mocks.  
- Coverage goal: ≥90%.  
- Use `pytest` as the test runner.  

---

## CONFIG.md
### Environment Variables
- `APP_NAME`: Name of the application. Default: `default_app`.  
- `LOG_LEVEL`: Logging level. Default: `INFO`.  
- `EMPTY_LOG_FILE_ON_RUN`: Truncate logs on startup (`true`/`false`).  
- `PARALLEL_STDOUT_LOGGING`: Mirror logs to stdout (`true`, or level).  

---

## USAGE.md
### Basic Example
```python
from kiro_logging import SingletonLogger

logger = SingletonLogger.get_logger()
logger.info("Application started")

Advanced Example

export LOG_LEVEL=DEBUG
export PARALLEL_STDOUT_LOGGING=true
python app.py

ARCHITECTURE.md
Components

    Core: SingletonLogger, formatters, handlers.

    Contrib: AWS CloudWatch handler.

    Docs: Steering, specs, onboarding, release.

    Tests: Unit and integration suites.

EXTENDING.md
Extending kiro_logging

    Add new handler in src/contrib.

    Ensure it inherits from Python logging handler.

    Follow steering conventions.

    Add tests and examples.

EXAMPLES.md
Examples

    Minimal logger usage.

    AWS Lambda logger integration.

    Dockerized service logs.

    CloudWatch contrib handler.

ROADMAP.md
Planned Features

    v0.1.0: Core functionality + CloudWatch.

    v0.2.0: File rotation.

    v0.3.0: Structured context injection.

    v1.0.0: Stable release with contrib ecosystem.

SECURITY.md
Security Policy

    Supported: Latest release.

    Report: security@yourdomain.com

    .

    Do not disclose vulnerabilities publicly before patch release.

CODE_OF_CONDUCT.md
Code of Conduct

    Be respectful and inclusive.

    No harassment or abuse tolerated.

    Conflicts resolved constructively.

docs/ONBOARDING.md
Onboarding Guide

    Clone repo.

    Create virtualenv.

    Install dependencies with pip install -e ".[dev]".

    Run make all.

    Review steering docs.

docs/RELEASE.md
Release Process

    Bump version in pyproject.toml.

    Update CHANGELOG.md.

    Commit and tag release.

    Build and upload to PyPI.

    Build and push Docker images.

    Publish GitHub release with notes.