# mypylogger v0.2.0

<!-- BADGES START -->
[![Quality Gate](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/quality-gate.yml?branch=main&style=flat)](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/quality-gate.yml?branch=main&style=flat) [![Security Scan](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/security-scan.yml?branch=main&style=flat)](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/security-scan.yml?branch=main&style=flat) [![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000?style=flat)](https://img.shields.io/badge/code%20style-ruff-000000?style=flat) [![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue?style=flat)](https://img.shields.io/badge/type%20checked-mypy-blue?style=flat) [![Python Versions](https://img.shields.io/pypi/pyversions/mypylogger?style=flat)](https://img.shields.io/pypi/pyversions/mypylogger?style=flat) [![PyPI Version](https://img.shields.io/pypi/v/mypylogger?style=flat)](https://img.shields.io/pypi/v/mypylogger?style=flat) [![Downloads: Development](https://img.shields.io/badge/downloads-development-yellow?style=flat)](https://img.shields.io/badge/downloads-development-yellow?style=flat) [![License: MIT](https://img.shields.io/github/license/stabbotco1/mypylogger?style=flat)](https://img.shields.io/github/license/stabbotco1/mypylogger?style=flat)
<!-- BADGES END -->

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
