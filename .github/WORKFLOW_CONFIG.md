# GitHub Actions Workflow Configuration

This document describes the GitHub Actions workflow configuration for mypylogger v0.2.0, including caching strategies, common patterns, and implementation guidelines.

## Directory Structure

```
.github/
├── workflows/
│   ├── _common-setup.yml     # Common configuration patterns (reference)
│   ├── _template.yml         # Workflow template (reference)
│   ├── quality-gate.yml     # PR quality checks (to be implemented)
│   ├── security-scan.yml    # Security monitoring (to be implemented)
│   └── publish.yml          # PyPI publishing (to be implemented)
├── dependabot.yml           # Dependency updates (to be implemented)
├── CODEOWNERS              # Code review assignments (to be implemented)
└── WORKFLOW_CONFIG.md      # This documentation file
```

## UV Caching Strategy

### Cache Configuration

All workflows use a consistent UV caching strategy to meet performance requirements:

```yaml
- name: Cache UV dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
    restore-keys: |
      uv-${{ runner.os }}-${{ matrix.python-version }}-
      uv-${{ runner.os }}-
```

### Cache Key Strategy

- **Primary key**: `uv-{OS}-{Python-version}-{uv.lock-hash}`
- **Fallback keys**: Progressive fallback for partial cache hits
- **Cache path**: `~/.cache/uv` (UV's default cache directory)

### Cache Benefits

- **Performance**: Reduces dependency installation time from minutes to seconds
- **Reliability**: Consistent dependency versions across workflow runs
- **Cost efficiency**: Reduces GitHub Actions compute time
- **Network efficiency**: Minimizes package downloads

## Common Workflow Patterns

### 1. Standard Job Setup

```yaml
jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: true
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install UV
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH
      - name: Cache UV dependencies
        # ... (see cache configuration above)
      - name: Install dependencies
        run: uv sync
```

### 2. Quality Check Commands

Standard commands that match local development environment:

```yaml
- name: Run tests with coverage
  run: uv run pytest --cov=mypylogger --cov-fail-under=95

- name: Run linting checks
  run: uv run ruff check .

- name: Check code formatting
  run: uv run ruff format --check .

- name: Run type checking
  run: uv run mypy src/

- name: Run master test script
  run: ./scripts/run_tests.sh
```

### 3. Environment Variables

Global environment variables for consistency:

```yaml
env:
  UV_CACHE_DIR: ~/.cache/uv
  COVERAGE_THRESHOLD: "95"
  PYTHON_VERSION_MATRIX: "3.8,3.9,3.10,3.11,3.12"
```

## Performance Optimization

### Execution Time Targets

- **Quality gate workflows**: < 5 minutes (Requirement 5.1)
- **Individual jobs**: < 10 minutes timeout
- **Cache hit rate**: > 80% target (Requirement 5.3)

### Optimization Strategies

1. **Parallel execution**: Use matrix strategy for Python versions
2. **Fail-fast**: Stop on first failure for quick feedback
3. **Dependency caching**: UV cache with smart key strategy
4. **Minimal installs**: Only install required dependencies

### Cache Effectiveness Monitoring

Monitor cache performance through:
- Cache hit/miss rates in workflow logs
- Total workflow execution times
- Dependency installation step duration

## Security Configuration

### Default Permissions

```yaml
permissions:
  contents: read  # Minimal permissions by default
```

### Secure Patterns

- No hardcoded secrets in workflow files
- Use GitHub secrets for sensitive data
- OIDC authentication for PyPI publishing
- Dependabot for automated security updates

## Requirements Mapping

### Requirement 7.1: Consistent Environment
- ✅ Use UV package manager (same as local development)
- ✅ Same Python versions (3.8-3.12)
- ✅ Same quality check commands

### Requirement 7.4: Dependency Consistency
- ✅ Use uv.lock for reproducible builds
- ✅ Cache based on uv.lock hash
- ✅ Consistent dependency versions

### Requirement 2.4 & 5.3: Performance Caching
- ✅ UV dependency caching implemented
- ✅ Progressive cache key fallback
- ✅ Cache effectiveness monitoring

### Requirement 5.1: Fast Feedback
- ✅ 5-minute workflow target
- ✅ Fail-fast strategy
- ✅ Parallel execution

## Implementation Guidelines

### For New Workflows

1. **Copy patterns** from `_template.yml`
2. **Use consistent** caching configuration
3. **Follow naming** conventions (kebab-case)
4. **Include timeouts** for all jobs
5. **Document requirements** mapping in comments

### For Workflow Updates

1. **Maintain compatibility** with existing cache keys
2. **Test changes** on feature branches first
3. **Monitor performance** impact
4. **Update documentation** when patterns change

### Quality Gates

All workflows must:
- Use UV for package management
- Include dependency caching
- Have appropriate timeouts
- Follow security best practices
- Map to specific requirements

## Troubleshooting

### Common Issues

1. **Cache misses**: Check uv.lock file changes
2. **UV installation failures**: Verify curl and shell access
3. **Timeout issues**: Adjust timeout-minutes setting
4. **Permission errors**: Check workflow permissions

### Debug Commands

```yaml
- name: Debug UV cache
  run: |
    echo "UV cache directory: $UV_CACHE_DIR"
    ls -la ~/.cache/uv/ || echo "Cache directory not found"
    uv cache info

- name: Debug environment
  run: |
    uv --version
    uv run python --version
    uv run python -c "import sys; print(sys.path)"
```

## Future Enhancements

### Planned Improvements

1. **Cache warming**: Pre-populate caches for faster cold starts
2. **Artifact caching**: Cache test results and build artifacts
3. **Matrix optimization**: Dynamic matrix based on changed files
4. **Performance monitoring**: Automated performance regression detection

### Monitoring and Metrics

Track workflow performance through:
- GitHub Actions insights
- Workflow execution time trends
- Cache hit rate analysis
- Failure rate monitoring