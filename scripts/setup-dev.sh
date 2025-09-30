#!/bin/bash
# Development environment setup script for mypylogger
# This script sets up a complete development environment with all quality tools

set -e  # Exit on any error

echo "🚀 Setting up mypylogger development environment..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Consider running: python -m venv venv && source venv/bin/activate"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install package in development mode
echo "📦 Installing mypylogger in development mode..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "📁 Creating development directories..."
mkdir -p reports/security
mkdir -p reports/coverage
mkdir -p reports/performance
mkdir -p logs

# Run initial quality checks
echo "🔍 Running initial quality checks..."
echo "  - Code formatting..."
black --check . || (echo "❌ Code formatting issues found. Run 'make format' to fix." && exit 1)

echo "  - Import sorting..."
isort --check-only . || (echo "❌ Import sorting issues found. Run 'make format' to fix." && exit 1)

echo "  - Linting..."
flake8 . || (echo "❌ Linting issues found. Check output above." && exit 1)

echo "  - Type checking..."
mypy mypylogger/ || (echo "❌ Type checking issues found. Check output above." && exit 1)

# Run fast tests
echo "🧪 Running fast test suite..."
pytest tests/unit/ -v || (echo "❌ Tests failed. Check output above." && exit 1)

# Run security scans
echo "🔒 Running security scans..."
bandit -r mypylogger/ -f txt || (echo "⚠️  Security issues found. Review output above.")
safety check || (echo "⚠️  Dependency vulnerabilities found. Review output above.")

# Generate coverage report
echo "📊 Generating coverage report..."
pytest --cov=mypylogger --cov-report=html --cov-report=term-missing --cov-fail-under=90

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   • Run 'make help' to see available commands"
echo "   • Run 'make test-fast' for quick testing"
echo "   • Run 'make watch-tests' for continuous testing"
echo "   • Run 'make qa' for full quality checks"
echo "   • Open htmlcov/index.html to view coverage report"
echo ""
echo "🔧 Development workflow:"
echo "   1. Make changes to code"
echo "   2. Run 'make test-fast' to verify changes"
echo "   3. Run 'make qa' before committing"
echo "   4. Commit (pre-commit hooks will run automatically)"
echo "   5. Push to trigger CI/CD pipeline"
echo ""
echo "Happy coding! 🎉"