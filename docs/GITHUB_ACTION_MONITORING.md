# GitHub Action Monitoring

A comprehensive system for monitoring GitHub Actions CI/CD pipeline status from your local development environment. This tool provides real-time feedback on remote pipeline execution, allowing developers to make informed decisions about code quality and deployment readiness without leaving their local development workflow.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Integration](#integration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Features

### Core Monitoring Capabilities
- **Real-time Pipeline Monitoring**: Track GitHub Actions workflow status in real-time
- **Intelligent Polling**: Adaptive polling intervals based on workflow status and history
- **Multiple Output Formats**: Console, JSON, and minimal output formats
- **Progress Indicators**: Real-time progress updates with estimated completion times
- **Failure Detection**: Immediate notification of pipeline failures with detailed error information

### Performance Optimizations
- **Response Caching**: Reduces redundant API calls with intelligent TTL management
- **Rate Limiting Compliance**: Automatic GitHub API rate limit tracking and throttling
- **Concurrent Monitoring**: Support for monitoring multiple workflows simultaneously
- **Memory Optimization**: Efficient resource usage during extended monitoring sessions

### Developer Workflow Integration
- **Test Suite Integration**: Blocks local test completion when remote pipelines fail
- **Make Command Integration**: New make targets for pipeline monitoring
- **Quality Gate Enforcement**: Ensures both local and remote quality gates pass
- **Bypass Options**: Emergency bypass for offline development or urgent fixes

## Quick Start

### 1. Set up GitHub Token

Create a GitHub Personal Access Token with the following permissions:
- **Actions: Read** (required for pipeline monitoring)

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"
```

### 2. Basic Usage

```bash
# Monitor current commit's pipeline status
python scripts/github_pipeline_monitor.py --status-only

# Monitor and wait for pipeline completion
python scripts/github_pipeline_monitor.py

# Monitor after pushing to pre-release branch
python scripts/github_pipeline_monitor.py --after-push --branch pre-release
```

### 3. Integration with Test Suite

```bash
# Run tests with pipeline checking enabled
GITHUB_PIPELINE_CHECK=true ./scripts/run-complete-test-suite.sh

# Or use make targets
make test-complete-with-pipeline
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Git repository with GitHub remote
- GitHub Personal Access Token
- Internet connection for GitHub API access

### Setup Steps

1. **Clone or navigate to your project directory**
   ```bash
   cd your-project-directory
   ```

2. **Install dependencies** (if not already installed)
   ```bash
   pip install -r requirements.txt
   ```

3. **Create GitHub Personal Access Token**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Click "Generate new token (classic)"
   - Select scopes: **Actions: Read**
   - Copy the generated token

4. **Configure environment variables**
   ```bash
   # Add to your shell profile (.bashrc, .zshrc, etc.)
   export GITHUB_TOKEN="your_token_here"

   # Optional: Configure default settings
   export GITHUB_PIPELINE_TIMEOUT=30  # minutes
   export GITHUB_PIPELINE_POLL_INTERVAL=15  # seconds
   ```

5. **Verify setup**
   ```bash
   python scripts/github_pipeline_monitor.py --cache-stats
   ```

## Configuration

### Environment Variables

The system supports configuration through environment variables:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Required | `ghp_xxxxxxxxxxxx` |
| `GITHUB_PIPELINE_CHECK` | Enable pipeline checking in test suite | `false` | `true` |
| `GITHUB_PIPELINE_TIMEOUT` | Timeout for pipeline monitoring (minutes) | `30` | `45` |
| `GITHUB_PIPELINE_POLL_INTERVAL` | Base polling interval (seconds) | `30` | `15` |
| `GITHUB_PIPELINE_BRANCH` | Default branch to monitor | `pre-release` | `main` |
| `GITHUB_PIPELINE_VERBOSE` | Enable verbose output | `false` | `true` |
| `GITHUB_PIPELINE_COLORS` | Enable colored output | `true` | `false` |

### Configuration File

Create a `.github-monitor.yml` file in your project root for persistent configuration:

```yaml
github:
  token: ${GITHUB_TOKEN}  # Environment variable reference
  repository: auto        # Auto-detect from git remote

monitoring:
  branches:
    - pre-release
    - main
  poll_interval: 30       # seconds
  timeout: 30            # minutes
  auto_monitor: true     # Monitor on push automatically

integration:
  test_suite_runner: true
  make_commands: true
  block_on_failure: true

output:
  format: console        # console, json, minimal
  colors: true
  progress_indicators: true
```

### Repository Auto-Detection

The system automatically detects your GitHub repository from the git remote:

```bash
# These remotes are supported:
git remote add origin git@github.com:owner/repo.git
git remote add origin https://github.com/owner/repo.git
```

## Usage

### Command Line Interface

#### Basic Monitoring

```bash
# Check current pipeline status
python scripts/github_pipeline_monitor.py --status-only

# Monitor specific commit
python scripts/github_pipeline_monitor.py --commit abc123

# Monitor with custom timeout
python scripts/github_pipeline_monitor.py --timeout 45
```

#### Output Formats

```bash
# Console output (default)
python scripts/github_pipeline_monitor.py --format console

# JSON output for scripting
python scripts/github_pipeline_monitor.py --format json

# Minimal output
python scripts/github_pipeline_monitor.py --format minimal
```

#### Verbose and Debug Options

```bash
# Verbose output with detailed information
python scripts/github_pipeline_monitor.py --verbose

# Show cache and rate limit statistics
python scripts/github_pipeline_monitor.py --cache-stats

# Disable colors for CI environments
python scripts/github_pipeline_monitor.py --no-colors
```

### Make Command Integration

New make targets are available for pipeline monitoring:

```bash
# Monitor current commit's pipeline
make monitor-pipeline

# Monitor after push to pre-release
make monitor-after-push

# Quick pipeline status check
make check-pipeline-status

# Wait for pipeline completion with timeout
make wait-for-pipeline

# Wait for pipeline completion with extended timeout (60 minutes)
make wait-for-pipeline-extended

# Run complete test suite with pipeline checking
make test-complete-with-pipeline

# Run complete test suite and wait for pipeline completion
make test-complete-wait-pipeline

# Run complete test suite with pipeline bypass (emergency mode)
make test-complete-bypass-pipeline
```

### Test Suite Integration

The system integrates with your existing test suite runner:

```bash
# Enable pipeline checking
export GITHUB_PIPELINE_CHECK=true
./scripts/run-complete-test-suite.sh

# Disable pipeline checking (for offline development)
export GITHUB_PIPELINE_CHECK=false
./scripts/run-complete-test-suite.sh

# Run with bypass option (for emergencies)
export GITHUB_PIPELINE_BYPASS=true
./scripts/run-complete-test-suite.sh

# Configure timeout and polling
export GITHUB_PIPELINE_TIMEOUT=45
export GITHUB_PIPELINE_POLL_INTERVAL=15
./scripts/run-complete-test-suite.sh
```

## Integration

### Continuous Integration

#### GitHub Actions Integration

Add pipeline monitoring to your GitHub Actions workflow:

```yaml
name: CI with Pipeline Monitoring
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests with pipeline monitoring
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_PIPELINE_CHECK: true
        run: ./scripts/run-complete-test-suite.sh
```

#### Pre-commit Hooks

Add pipeline monitoring to pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pipeline-check
        name: GitHub Pipeline Check
        entry: python scripts/github_pipeline_monitor.py --status-only
        language: system
        pass_filenames: false
        always_run: true
```

### IDE Integration

#### VS Code Integration

Add tasks to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Monitor Pipeline",
      "type": "shell",
      "command": "python",
      "args": ["scripts/github_pipeline_monitor.py"],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      }
    },
    {
      "label": "Check Pipeline Status",
      "type": "shell",
      "command": "python",
      "args": ["scripts/github_pipeline_monitor.py", "--status-only"],
      "group": "test"
    }
  ]
}
```

### Development Workflow Examples

#### Feature Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push to remote
git push origin feature/new-feature

# 4. Monitor pipeline status
make monitor-after-push

# 5. Run local tests with pipeline checking
make test-complete-with-pipeline
```

#### Release Workflow

```bash
# 1. Merge to pre-release
git checkout pre-release
git merge feature/new-feature

# 2. Push and monitor
git push origin pre-release
make monitor-after-push --branch pre-release

# 3. Wait for all pipelines to complete
make wait-for-pipeline

# 4. If successful, merge to main
git checkout main
git merge pre-release
git push origin main
```

## Troubleshooting

### Common Issues

#### Authentication Problems

**Problem**: `401 Unauthorized` error
```
❌ Error: GitHub API authentication failed - invalid or missing token
```

**Solution**:
1. Verify your GitHub token is set: `echo $GITHUB_TOKEN`
2. Check token permissions include "Actions: Read"
3. Regenerate token if necessary

**Problem**: `403 Forbidden` error
```
❌ Error: GitHub API access denied - insufficient permissions
```

**Solution**:
1. Ensure token has "Actions: Read" permission
2. Verify you have access to the repository
3. Check if repository is private and token has appropriate scope

#### Repository Detection Issues

**Problem**: Repository not found or not accessible
```
❌ Error: Repository owner/repo not found or not accessible
```

**Solution**:
1. Verify git remote is configured: `git remote -v`
2. Check repository name and owner are correct
3. Ensure you have read access to the repository

#### Rate Limiting

**Problem**: Rate limit exceeded
```
⚠️ GitHub API rate limit warning: 5 requests remaining
```

**Solution**:
1. Wait for rate limit to reset (shown in warning)
2. Reduce polling frequency with `--poll-interval`
3. Use caching to reduce API calls

#### Network Issues

**Problem**: Network connectivity errors
```
❌ Error: Network connectivity error: [Errno 11001] getaddrinfo failed
```

**Solution**:
1. Check internet connection
2. Verify GitHub API is accessible: `curl https://api.github.com`
3. Check firewall/proxy settings
4. For offline development, disable pipeline checking: `GITHUB_PIPELINE_CHECK=false`

#### Bypass Options

For emergency situations or offline development, you can bypass pipeline monitoring:

**Disable Pipeline Checking**:
```bash
# Completely disable pipeline checking
export GITHUB_PIPELINE_CHECK=false
./scripts/run-complete-test-suite.sh
```

**Emergency Bypass**:
```bash
# Bypass failed pipelines (emergency mode)
export GITHUB_PIPELINE_BYPASS=true
./scripts/run-complete-test-suite.sh
```

**Network Issues**:
If you're experiencing network issues or working offline, disable monitoring to continue local development without interruption. Common network issues include DNS resolution failures, firewall blocking, or intermittent connectivity problems.

### Debug Mode

Enable verbose output for detailed troubleshooting:

```bash
# Verbose output with detailed information
python scripts/github_pipeline_monitor.py --verbose

# Show cache and API statistics
python scripts/github_pipeline_monitor.py --cache-stats --verbose

# Debug configuration issues
python scripts/github_monitor_config.py --setup-help
```

### Configuration Validation

Validate your configuration:

```bash
# Test GitHub API connectivity
python scripts/github_pipeline_monitor.py --status-only --verbose

# Validate repository detection
python -c "
from scripts.github_pipeline_monitor import parse_github_repo_from_remote
print(parse_github_repo_from_remote())
"

# Check environment variables
env | grep GITHUB_
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Enable verbose mode for detailed error information
2. **Verify configuration**: Use the configuration validation commands
3. **Test connectivity**: Ensure GitHub API is accessible
4. **Check permissions**: Verify token has correct permissions
5. **Review documentation**: Check the advanced usage section

## Advanced Usage

### Custom Polling Strategies

Configure intelligent polling for different scenarios:

```python
# Custom polling strategy
from scripts.github_intelligent_polling import PollingStrategy

strategy = PollingStrategy(
    queued_interval=120,      # Slow polling for queued workflows
    active_interval=10,       # Fast polling for active workflows
    completing_interval=5,    # Very fast polling near completion
    max_interval=300,         # Maximum interval cap
    completion_threshold_ratio=0.8  # When to switch to completing phase
)
```

### Cache Management

Control caching behavior:

```bash
# Show cache statistics
python scripts/github_pipeline_monitor.py --cache-stats

# Clear cache for fresh data
python -c "
from scripts.github_cache_manager import create_cache_manager
cache = create_cache_manager()
cache.invalidate_cache()
print('Cache cleared')
"
```

### Performance Monitoring

Monitor system performance:

```python
# Get performance statistics
from scripts.github_pipeline_monitor import GitHubPipelineMonitor
from scripts.github_monitor_config import ConfigManager

config = ConfigManager().load_config()
monitor = GitHubPipelineMonitor(config)

# Get cache and polling statistics
cache_stats = monitor.get_cache_statistics()
polling_stats = monitor.polling_manager.get_polling_statistics()

print(f"Cache hit ratio: {cache_stats['cache']['hit_ratio']:.1%}")
print(f"Active workflows: {polling_stats['active_workflows']}")
```

### Programmatic Usage

Use the monitoring system in your own scripts:

```python
from scripts.github_pipeline_monitor import GitHubPipelineMonitor
from scripts.github_monitor_config import ConfigManager

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Create monitor
monitor = GitHubPipelineMonitor(config)

# Get current status
status = monitor.get_pipeline_status()
print(f"Overall status: {status.overall_status}")

# Wait for completion
if status.overall_status == "pending":
    final_status = monitor.wait_for_pipeline_completion()
    print(f"Final status: {final_status.overall_status}")
```

### Integration with Other Tools

#### Slack Notifications

```python
# Example: Send Slack notification on pipeline completion
import requests
from scripts.github_pipeline_monitor import GitHubPipelineMonitor

def send_slack_notification(status):
    webhook_url = "your_slack_webhook_url"
    message = {
        "text": f"Pipeline {status.overall_status} for commit {status.commit_sha[:8]}"
    }
    requests.post(webhook_url, json=message)

# Monitor and notify
monitor = GitHubPipelineMonitor(config)
status = monitor.wait_for_pipeline_completion()
send_slack_notification(status)
```

#### Custom Dashboards

```python
# Example: Export status for dashboard
import json
from scripts.github_pipeline_monitor import GitHubPipelineMonitor

monitor = GitHubPipelineMonitor(config)
status = monitor.get_pipeline_status()

# Export to JSON for dashboard consumption
dashboard_data = {
    "timestamp": datetime.now().isoformat(),
    "commit": status.commit_sha,
    "status": status.overall_status,
    "workflows": [
        {
            "name": run.name,
            "status": run.status,
            "conclusion": run.conclusion,
            "duration": run.duration_seconds
        }
        for run in status.workflow_runs
    ]
}

with open("pipeline_status.json", "w") as f:
    json.dump(dashboard_data, f, indent=2)
```

---

For more information, see the [GitHub Token Setup Guide](GITHUB_TOKEN_SETUP.md) and [API Documentation](../scripts/).
