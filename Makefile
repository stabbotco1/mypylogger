# Makefile for mypylogger development workflow
# Provides automated quality checks, testing, and development commands

.PHONY: help install install-dev clean lint format type-check security test test-fast test-coverage test-performance test-all build check-package pre-commit setup-dev monitor-pipeline monitor-after-push check-pipeline-status wait-for-pipeline wait-for-pipeline-extended test-complete-with-pipeline test-complete-wait-pipeline test-complete-bypass-pipeline quality-gate-full ci-full pre-push-full

# Default target
help:
	@echo "mypylogger Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup          Create venv and setup complete development environment"
	@echo "  install        Install package in development mode"
	@echo "  install-dev    Install with development dependencies"
	@echo "  setup-dev      Complete development environment setup (requires active venv)"
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
	@echo "  test-complete  Run comprehensive test suite with full reporting"
	@echo "  test-complete-fast Run fast verification with reporting"
	@echo "  test-complete-performance Include performance benchmarks in reporting"
	@echo ""
	@echo "Build and Package:"
	@echo "  build          Build package distributions"
	@echo "  check-package  Validate package build"
	@echo "  clean          Clean build artifacts and cache files"
	@echo ""
	@echo "Documentation and Verification:"
	@echo "  docs-check               Check documentation completeness"
	@echo "  verify-badges            Verify README badge URLs and configuration"
	@echo "  validate-badges-verbose  Run detailed badge validation with verbose output"
	@echo "  validate-docs-dates      Check for outdated dates in documentation"
	@echo "  validate-docs-dates-verbose Show all dates including acceptable ones"
	@echo "  test-badge-performance   Test badge loading performance and fallback behavior"
	@echo "  badge-health-check       Run comprehensive badge health monitoring"
	@echo "  badge-health-ci          Run badge health check for CI/CD integration"
	@echo "  fix-formatting           Fix all code formatting issues automatically"
	@echo ""
	@echo "Pipeline Monitoring:"
	@echo "  monitor-pipeline       Monitor current commit's pipeline status"
	@echo "  monitor-after-push     Monitor pipeline after push to pre-release"
	@echo "  check-pipeline-status  Quick pipeline status check"
	@echo "  wait-for-pipeline      Wait for pipeline completion with timeout"
	@echo ""
	@echo "Development Workflow:"
	@echo "  qa             Run all quality checks (lint + type + security)"
	@echo "  ci             Run full CI pipeline locally"
	@echo "  ci-full        Enhanced CI with pipeline verification"
	@echo "  quality-gate-full Enhanced quality gate with optional pipeline check"
	@echo "  pre-push-full  Enhanced pre-push with pipeline awareness"
	@echo ""
	@echo "Environment Variables:"
	@echo "  ENABLE_PIPELINE_CHECK=true   Enable pipeline checking in enhanced targets"

# Setup commands
setup:
	@echo "Setting up complete development environment..."
	./scripts/setup-dev.sh

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

# Fix all formatting issues
fix-formatting:
	@echo "Fixing all formatting issues..."
	./scripts/fix-formatting.sh

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

# Enhanced CI with pipeline integration
ci-full: qa test-coverage test-performance build check-package
	@echo "Running enhanced CI pipeline with remote pipeline verification..."
	@if [ "$$ENABLE_PIPELINE_CHECK" = "true" ]; then \
		echo "Verifying remote GitHub Actions pipelines..."; \
		python scripts/github_pipeline_monitor.py --status-only --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/') || \
		(echo "❌ Remote pipelines failed - CI pipeline blocked"; exit 1); \
		echo "✅ Remote pipelines passed"; \
	else \
		echo "Remote pipeline checking disabled (set ENABLE_PIPELINE_CHECK=true to enable)"; \
	fi
	@echo "Enhanced CI pipeline completed successfully!"
	@echo "Package is ready for release with verified remote pipelines."

# Complete test suite runner
test-complete:
	@echo "Running complete test suite with comprehensive reporting..."
	./scripts/run-complete-test-suite.sh

test-complete-fast:
	@echo "Running fast test suite verification..."
	./scripts/run-complete-test-suite.sh --verbose

test-complete-performance:
	@echo "Running complete test suite with performance benchmarks..."
	./scripts/run-complete-test-suite.sh --performance

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

# Enhanced quality gate with optional pipeline checking
quality-gate-full: qa test-coverage
	@echo "Running enhanced quality gate..."
	@if [ "$$ENABLE_PIPELINE_CHECK" = "true" ]; then \
		echo "Pipeline checking enabled - verifying remote pipelines..."; \
		./scripts/run-complete-test-suite.sh --check-pipeline --verbose; \
	else \
		echo "Pipeline checking disabled (set ENABLE_PIPELINE_CHECK=true to enable)"; \
		./scripts/run-complete-test-suite.sh --verbose; \
	fi
	@echo "Enhanced quality gate passed!"

# Development server/tools
dev-server:
	@echo "Starting development environment..."
	@echo "Use 'make watch-tests' in another terminal for continuous testing."

# Documentation helpers
docs-check:
	@echo "Checking documentation..."
	python -c "import mypylogger; help(mypylogger)"
	@echo "Documentation check complete!"

# Badge verification
verify-badges:
	@echo "Verifying README badges..."
	python scripts/validate_badges.py

validate-docs-dates:
	@echo "Validating documentation dates..."
	python scripts/validate_documentation_dates.py

validate-docs-dates-verbose:
	@echo "Validating documentation dates (verbose)..."
	python scripts/validate_documentation_dates.py --verbose
	@echo "Badge verification complete!"

test-badge-performance:
	@echo "Testing badge loading performance..."
	python scripts/test_badge_performance.py
	@echo "Badge performance test complete!"

validate-badges-verbose:
	@echo "Running detailed badge validation..."
	python scripts/validate_badges.py --verbose
	@echo "Detailed badge validation complete!"

badge-health-check:
	@echo "Running badge health check..."
	python scripts/badge_health_monitor.py --verbose
	@echo "Badge health check complete!"

badge-health-ci:
	@echo "Running badge health check for CI/CD..."
	python scripts/badge_health_monitor.py --format github-actions --fail-on-error
	@echo "CI badge health check complete!"

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

# Enhanced pre-push with pipeline awareness
pre-push-full: qa test-coverage
	@echo "Running enhanced pre-push checks..."
	@if [ "$$ENABLE_PIPELINE_CHECK" = "true" ]; then \
		echo "Checking current pipeline status before push..."; \
		python scripts/github_pipeline_monitor.py --status-only --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/') && \
		echo "✅ Current pipelines are passing - safe to push" || \
		(echo "⚠️  Current pipelines have issues - consider waiting or fixing before push"; exit 1); \
	else \
		echo "Pipeline checking disabled (set ENABLE_PIPELINE_CHECK=true to enable)"; \
	fi
	@echo "Enhanced pre-push checks complete!"

# Release preparation
prepare-release: ci
	@echo "Release preparation complete!"
	@echo "Ready for version tagging and PyPI publication."

# Pipeline monitoring commands
monitor-pipeline:
	@echo "Monitoring current commit's pipeline status..."
	python scripts/github_pipeline_monitor.py --status-only --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')

monitor-after-push:
	@echo "Monitoring pipeline after push to pre-release..."
	python scripts/github_pipeline_monitor.py --after-push --branch pre-release --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')

check-pipeline-status:
	@echo "Quick pipeline status check..."
	python scripts/github_pipeline_monitor.py --status-only --format minimal --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')

wait-for-pipeline:
	@echo "Waiting for pipeline completion (30 minute timeout)..."
	python scripts/github_pipeline_monitor.py --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')

wait-for-pipeline-extended:
	@echo "Waiting for pipeline completion (60 minute timeout)..."
	python scripts/github_pipeline_monitor.py --timeout 60 --repo $(shell git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')

# Pipeline-integrated quality gates
test-complete-with-pipeline:
	@echo "Running complete test suite with pipeline quality gate..."
	./scripts/run-complete-test-suite.sh --check-pipeline

test-complete-wait-pipeline:
	@echo "Running complete test suite and waiting for pipeline completion..."
	./scripts/run-complete-test-suite.sh --check-pipeline --pipeline-wait

# Emergency bypass for pipeline issues
test-complete-bypass-pipeline:
	@echo "Running complete test suite with pipeline bypass (emergency mode)..."
	./scripts/run-complete-test-suite.sh --check-pipeline --pipeline-bypass
