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
