# mypylogger v0.2.0

[![Build Status](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/stabbotco1/mypylogger/main/.github/badges/build-status.json)](https://github.com/stabbotco1/mypylogger/actions/workflows/quality-gate.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/stabbotco1/mypylogger/main/.github/badges/coverage.json)](https://github.com/stabbotco1/mypylogger/actions/workflows/quality-gate.yml)
[![Security](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/stabbotco1/mypylogger/main/.github/badges/security.json)](https://github.com/stabbotco1/mypylogger/actions/workflows/security-scan.yml)
[![Code Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/stabbotco1/mypylogger/main/.github/badges/code-style.json)](https://github.com/astral-sh/ruff)

[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-v0.2.0-orange?logo=pypi&logoColor=white)](https://pypi.org/project/mypylogger/)
[![Downloads](https://img.shields.io/badge/downloads-development-green?logo=pypi&logoColor=white)](https://pypi.org/project/mypylogger/)
[![License](https://img.shields.io/badge/license-MIT-blue?logo=opensourceinitiative&logoColor=white)](https://github.com/stabbotco1/mypylogger/blob/main/LICENSE)

A Python logging library designed to provide enhanced logging capabilities with zero dependencies and sensible defaults.

## Vision

Create a **zero-dependency JSON logging library with sensible defaults** for Python applications. mypylogger v0.2.0 does ONE thing exceptionally well: structured JSON logs that work everywhere—from local development to AWS Lambda to Kubernetes.

## Installation

```bash
pip install mypylogger
```

## Quick Start

```python
from mypylogger import get_logger

logger = get_logger(__name__)
logger.info("Application started")
```

## Features

- **Minimal Dependencies** (only `python-json-logger`)
- **Clean, Predictable JSON Output**
- **Developer-Friendly Defaults**
- **Standard Python Patterns**

## Development

This project uses UV for dependency management:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Check linting
uv run ruff check .
```

## License

MIT License
