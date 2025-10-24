# mypylogger v0.2.0

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
