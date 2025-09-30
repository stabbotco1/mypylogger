# Makefile for mypylogger development workflow
# Provides automated quality checks, testing, and development commands

.PHONY: help install install-dev clean lint format type-check security test test-fast test-coverage test-performance test-all build check-package pre-commit setup-dev

# Default target
help:
	@echo "mypylogger Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install        Install package in development mode"
	@echo "  install-dev    Install with development dependencies"
	@echo "  setup-dev      Complete development environment setup"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  lint           Run all linting checks"
	@echo "  format         Format code with black and isort"
	@echo "  type-check     Run mypy type checking"
	@echo "  security       Run security scans (bandit, safety)"
	@echo "  pre-commit     Run pre-commit hooks on all files"
	@echo ""
	@echo "Testing:"
	@echo "  test-fast      Run fast unit tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  test-performance Run performance benchmark tests"
	@echo "  test-all       Run complete test suite"
	@echo ""
	@echo "Build and Package:"
	@echo "  build          Build package distributions"
	@echo "  check-package  Validate package build"
	@echo "  clean          Clean build artifacts and cache files"
	@echo ""
	@echo "Development Workflow:"
	@echo "  qa             Run all quality checks (lint + type + security)"
	@echo "  ci             Run full CI pipeline locally"

# Installation commands
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

setup-dev: install-dev
	pre-commit install
	@echo "Development environment setup complete!"
	@echo "Run 'make test-fast' to verify everything works."

# Code quality commands
format:
	@echo "Formatting code with black..."
	black .
	@echo "Sorting imports with isort..."
	isort .
	@echo "Code formatting complete!"

lint:
	@echo "Running flake8 linting..."
	flake8 .
	@echo "Linting complete!"

type-check:
	@echo "Running mypy type checking..."
	mypy mypylogger/
	@echo "Type checking complete!"

security:
	@echo "Running bandit security scan..."
	bandit -r mypylogger/ -f txt
	@echo "Running safety dependency scan..."
	safety check
	@echo "Security scans complete!"

pre-commit:
	@echo "Running pre-commit hooks on all files..."
	pre-commit run --all-files

# Combined quality assurance
qa: format lint type-check security
	@echo "All quality checks passed!"

# Testing commands
test-fast:
	@echo "Running fast unit tests..."
	pytest tests/unit/ -v -m "not slow"

test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=mypylogger --cov-report=html --cov-report=term-missing --cov-fail-under=90

test-performance:
	@echo "Running performance benchmark tests..."
	pytest tests/test_performance.py -v -m performance -s

test-all:
	@echo "Running complete test suite..."
	pytest -v

# Build and package commands
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf reports/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

build: clean
	@echo "Building package..."
	python -m build
	@echo "Build complete!"

check-package: build
	@echo "Checking package..."
	python -m twine check dist/*
	@echo "Package check complete!"

# CI pipeline simulation
ci: qa test-coverage test-performance build check-package
	@echo "Full CI pipeline completed successfully!"
	@echo "Package is ready for release."

# Development workflow helpers
watch-tests:
	@echo "Starting test watcher (save files to trigger tests)..."
	pytest-watch --clear --onpass --onfail --runner "pytest tests/unit/ -v"

watch-coverage:
	@echo "Starting coverage watcher..."
	pytest-watch --clear --onpass --onfail --runner "pytest --cov=mypylogger --cov-report=term-missing"

# Performance monitoring
benchmark: test-performance
	@echo "Performance benchmarks complete!"
	@echo "Check output above for performance metrics."

# Quality gate enforcement (for CI/CD)
quality-gate: qa test-coverage
	@echo "Quality gate passed!"
	@echo "Code meets all quality standards."

# Development server/tools
dev-server:
	@echo "Starting development environment..."
	@echo "Use 'make watch-tests' in another terminal for continuous testing."

# Documentation helpers
docs-check:
	@echo "Checking documentation..."
	python -c "import mypylogger; help(mypylogger)"
	@echo "Documentation check complete!"

# Dependency management
update-deps:
	@echo "Updating development dependencies..."
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"
	@echo "Dependencies updated!"

# Git workflow helpers
pre-push: qa test-coverage
	@echo "Pre-push checks complete!"
	@echo "Safe to push to repository."

# Release preparation
prepare-release: ci
	@echo "Release preparation complete!"
	@echo "Ready for version tagging and PyPI publication."