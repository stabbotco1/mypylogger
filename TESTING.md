# Testing Quick Reference

## Complete Test Suite Runner

### Quick Commands

```bash
# Fast task verification (recommended for most tasks)
make test-complete-fast

# Complete verification (before commits/PRs)
make test-complete

# Performance validation (for performance-critical tasks)
make test-complete-performance

# Help and options
./scripts/run-complete-test-suite.sh --help
```

### What Gets Verified

✅ **Code Quality** - Formatting, linting, type checking, security  
✅ **Test Coverage** - ≥90% coverage requirement  
✅ **Functionality** - All tests pass  
✅ **Performance** - Benchmarks meet requirements (with --performance)  
✅ **Package Build** - Distribution packages build correctly  
✅ **Documentation** - Badges and docs are valid  

### Usage Patterns

| Scenario | Command | When to Use |
|----------|---------|-------------|
| **Task Completion** | `make test-complete-fast` | After completing any task |
| **Before Commit** | `make test-complete` | Before committing changes |
| **Before PR** | `make test-complete-performance` | Before creating pull requests |
| **Debugging** | `./scripts/run-complete-test-suite.sh --verbose` | When investigating failures |

### Success Indicators

- ✅ All quality gates passed
- ✅ Coverage ≥90% maintained  
- ✅ No security vulnerabilities
- ✅ Package builds successfully
- ✅ Performance benchmarks pass (if included)

### Quick Troubleshooting

The test suite now handles most setup issues automatically, but if you encounter problems:

```bash
# If formatting issues
make fix-formatting

# If environment setup fails
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# If coverage issues
make test-coverage
open htmlcov/index.html

# If performance issues
make test-performance
```

## Individual Test Commands

```bash
# Fast unit tests only
make test-fast

# Tests with coverage report
make test-coverage  

# Performance benchmarks
make test-performance

# All tests
make test-all

# Quality checks only
make qa
```

## Coverage Requirements

- **Minimum**: 90%
- **Target**: 95%+
- **Scope**: All code in `mypylogger/`

## Performance Requirements

- **Latency**: <1ms per log (95th percentile)
- **Throughput**: >10,000 logs/second
- **Memory**: <50MB baseline increase

---

**💡 Tip**: Use `make test-complete-fast` after completing any task to ensure quality and catch regressions early!