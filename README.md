# mypylogger v0.2.0

[![Quality Gate](https://github.com/stabbotco1/mypylogger/actions/workflows/quality-gate.yml/badge.svg?branch=main)](https://github.com/stabbotco1/mypylogger/actions/workflows/quality-gate.yml)
[![Security Scanning](https://github.com/stabbotco1/mypylogger/actions/workflows/security-scan.yml/badge.svg?branch=main)](https://github.com/stabbotco1/mypylogger/actions/workflows/security-scan.yml)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

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
