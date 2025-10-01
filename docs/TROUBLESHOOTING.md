# GitHub Action Monitoring - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the GitHub Action monitoring system.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Authentication Issues](#authentication-issues)
- [Configuration Problems](#configuration-problems)
- [Network and API Issues](#network-and-api-issues)
- [Performance Issues](#performance-issues)
- [Integration Problems](#integration-problems)
- [Error Reference](#error-reference)

## Quick Diagnostics

### Health Check Commands

Run these commands to quickly diagnose common issues:

```bash
# 1. Check if GitHub token is set
echo "Token set: $([ -n "$GITHUB_TOKEN" ] && echo "✅ Yes" || echo "❌ No")"

# 2. Test basic API connectivity
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user > /dev/null && echo "✅ API accessible" || echo "❌ API not accessible"

# 3. Verify repository detection
python -c "
try:
    from scripts.github_pipeline_monitor import parse_github_repo_from_remote
    owner, repo = parse_github_repo_from_remote()
    print(f'✅ Repository detected: {owner}/{repo}')
except Exception as e:
    print(f'❌ Repository detection failed: {e}')
"

# 4. Test monitoring system
python scripts/github_pipeline_monitor.py --status-only --timeout 10 2>&1 | head -5
```

### Configuration Validation

```bash
# Validate current configuration
python scripts/github_monitor_config.py --validate

# Show current configuration
python scripts/github_monitor_config.py --show-config

# Get setup help
python scripts/github_monitor_config.py --setup-help
```

## Authentication Issues

### Problem: "GitHub token not provided"

**Error Message:**
```
❌ Error: GitHub token not provided
```

**Diagnosis:**
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Check shell profile
grep GITHUB_TOKEN ~/.bashrc ~/.zshrc ~/.bash_profile 2>/dev/null
```

**Solutions:**

1. **Set the token in your shell profile:**
   ```bash
   echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Set temporarily for testing:**
   ```bash
   export GITHUB_TOKEN="your_token_here"
   python scripts/github_pipeline_monitor.py --status-only
   ```

3. **Use configuration file:**
   ```yaml
   # .github-monitor.yml
   github:
     token: your_token_here
   ```

### Problem: "GitHub API authentication failed - invalid or missing token"

**Error Message:**
```
❌ Error: GitHub API authentication failed - invalid or missing token
```

**Diagnosis:**
```bash
# Test token manually
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

**Solutions:**

1. **Verify token format:**
   - Token should start with `ghp_`
   - Should be 40+ characters long

2. **Check token hasn't expired:**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Check expiration date

3. **Regenerate token:**
   - Create new token with same permissions
   - Update environment variable

### Problem: "GitHub API access denied - insufficient permissions"

**Error Message:**
```
❌ Error: GitHub API access denied - insufficient permissions
```

**Diagnosis:**
```bash
# Check token permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/OWNER/REPO/actions/runs
```

**Solutions:**

1. **Verify token permissions:**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Ensure "Actions: Read" is selected

2. **Check repository access:**
   - Verify you have read access to the repository
   - For private repos, ensure token has appropriate scope

3. **Organization settings:**
   - Some organizations restrict personal access tokens
   - Contact organization admin if needed

## Configuration Problems

### Problem: "Repository not found or not accessible"

**Error Message:**
```
❌ Error: Repository owner/repo not found or not accessible
```

**Diagnosis:**
```bash
# Check git remote configuration
git remote -v

# Test repository access
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/OWNER/REPO
```

**Solutions:**

1. **Verify git remote:**
   ```bash
   # Should show GitHub URL
   git remote get-url origin
   
   # If wrong, update it
   git remote set-url origin https://github.com/OWNER/REPO.git
   ```

2. **Manual repository specification:**
   ```bash
   python scripts/github_pipeline_monitor.py --repo OWNER/REPO --status-only
   ```

3. **Check repository name:**
   - Ensure owner and repository names are correct
   - Check for typos in repository name

### Problem: "Failed to get current commit SHA"

**Error Message:**
```
❌ Error: Failed to get current commit SHA: fatal: not a git repository
```

**Solutions:**

1. **Run from git repository root:**
   ```bash
   cd /path/to/your/git/repository
   python scripts/github_pipeline_monitor.py --status-only
   ```

2. **Initialize git repository:**
   ```bash
   git init
   git remote add origin https://github.com/OWNER/REPO.git
   ```

3. **Specify commit manually:**
   ```bash
   python scripts/github_pipeline_monitor.py --commit abc123 --status-only
   ```

## Network and API Issues

### Problem: "Network connectivity error"

**Error Message:**
```
❌ Error: Network connectivity error: [Errno 11001] getaddrinfo failed
```

**Diagnosis:**
```bash
# Test internet connectivity
ping github.com

# Test GitHub API
curl https://api.github.com

# Check DNS resolution
nslookup api.github.com
```

**Solutions:**

1. **Check internet connection:**
   - Verify network connectivity
   - Try accessing GitHub in browser

2. **Check firewall/proxy:**
   - Ensure GitHub API (api.github.com) is accessible
   - Configure proxy if needed

3. **Use alternative DNS:**
   ```bash
   # Temporarily use Google DNS
   export DNS_SERVER=8.8.8.8
   ```

### Problem: "GitHub API rate limit exceeded"

**Error Message:**
```
⚠️ GitHub API rate limit warning: 5 requests remaining
❌ Error: GitHub API rate limit exceeded
```

**Diagnosis:**
```bash
# Check current rate limit status
python scripts/github_pipeline_monitor.py --cache-stats
```

**Solutions:**

1. **Wait for rate limit reset:**
   ```bash
   # Check when rate limit resets
   python -c "
   from scripts.github_pipeline_monitor import GitHubPipelineMonitor
   from scripts.github_monitor_config import ConfigManager
   
   config = ConfigManager().load_config()
   monitor = GitHubPipelineMonitor(config)
   stats = monitor.get_cache_statistics()
   
   if 'rate_limit' in stats and stats['rate_limit']:
       reset_time = stats['rate_limit']['time_until_reset_seconds']
       print(f'Rate limit resets in {reset_time/60:.1f} minutes')
   "
   ```

2. **Reduce polling frequency:**
   ```bash
   export GITHUB_PIPELINE_POLL_INTERVAL=120  # 2 minutes
   python scripts/github_pipeline_monitor.py --status-only
   ```

3. **Use cached data:**
   ```bash
   # Allow stale cache data
   python scripts/github_pipeline_monitor.py --status-only --allow-stale
   ```

### Problem: "Invalid JSON response from GitHub API"

**Error Message:**
```
❌ Error: Invalid JSON response from GitHub API
```

**Diagnosis:**
```bash
# Test API response manually
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/OWNER/REPO/actions/runs
```

**Solutions:**

1. **Check GitHub API status:**
   - Visit [GitHub Status](https://www.githubstatus.com/)
   - Check for ongoing incidents

2. **Retry with backoff:**
   ```bash
   # The system has built-in retry logic, but you can retry manually
   sleep 30
   python scripts/github_pipeline_monitor.py --status-only
   ```

3. **Clear cache:**
   ```bash
   python -c "
   from scripts.github_cache_manager import create_cache_manager
   cache = create_cache_manager()
   cache.invalidate_cache()
   print('Cache cleared')
   "
   ```

## Performance Issues

### Problem: Slow monitoring performance

**Symptoms:**
- Long delays between status updates
- High CPU/memory usage
- Slow API responses

**Diagnosis:**
```bash
# Check cache performance
python scripts/github_pipeline_monitor.py --cache-stats --verbose

# Monitor system resources
top -p $(pgrep -f github_pipeline_monitor)

# Check API response times
time curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/OWNER/REPO/actions/runs
```

**Solutions:**

1. **Optimize polling intervals:**
   ```bash
   # Increase polling interval
   export GITHUB_PIPELINE_POLL_INTERVAL=60  # 1 minute
   
   # Use intelligent polling (default)
   python scripts/github_pipeline_monitor.py --status-only
   ```

2. **Improve cache hit ratio:**
   ```bash
   # Check cache statistics
   python scripts/github_pipeline_monitor.py --cache-stats
   
   # If hit ratio is low, consider increasing cache TTL
   ```

3. **Reduce concurrent monitoring:**
   ```bash
   # Monitor fewer workflows simultaneously
   # This is handled automatically by the intelligent polling system
   ```

### Problem: High memory usage

**Diagnosis:**
```bash
# Monitor memory usage
ps aux | grep github_pipeline_monitor

# Check cache size
python -c "
from scripts.github_cache_manager import create_cache_manager
cache = create_cache_manager()
stats = cache.get_request_statistics()
print(f'Cache entries: {stats[\"cache\"][\"total_entries\"]}')
"
```

**Solutions:**

1. **Clear cache periodically:**
   ```bash
   python -c "
   from scripts.github_cache_manager import create_cache_manager
   cache = create_cache_manager()
   cache.cleanup_expired_entries()
   "
   ```

2. **Reduce cache size:**
   ```python
   # Custom cache configuration
   from scripts.github_cache_manager import CacheConfig, create_cache_manager
   
   config = CacheConfig(max_entries=100)  # Smaller cache
   cache = create_cache_manager(config)
   ```

## Integration Problems

### Problem: Test suite integration not working

**Error Message:**
```
Pipeline checking is disabled or not configured
```

**Diagnosis:**
```bash
# Check environment variables
env | grep GITHUB_PIPELINE

# Test integration
export GITHUB_PIPELINE_CHECK=true
./scripts/run-complete-test-suite.sh --dry-run
```

**Solutions:**

1. **Enable pipeline checking:**
   ```bash
   export GITHUB_PIPELINE_CHECK=true
   ./scripts/run-complete-test-suite.sh
   ```

2. **Check test suite runner:**
   ```bash
   # Verify script exists and is executable
   ls -la ./scripts/run-complete-test-suite.sh
   
   # Test without pipeline checking
   export GITHUB_PIPELINE_CHECK=false
   ./scripts/run-complete-test-suite.sh
   ```

3. **Debug integration:**
   ```bash
   # Run with verbose output
   export GITHUB_PIPELINE_VERBOSE=true
   ./scripts/run-complete-test-suite.sh
   ```

### Problem: Make targets not working

**Error Message:**
```
make: *** No rule to make target 'monitor-pipeline'
```

**Diagnosis:**
```bash
# Check if make targets exist
make -n monitor-pipeline

# List available targets
make help
```

**Solutions:**

1. **Update Makefile:**
   - Ensure new make targets are added to your Makefile
   - Check the integration documentation

2. **Use direct script calls:**
   ```bash
   # Instead of make targets, use scripts directly
   python scripts/github_pipeline_monitor.py --status-only
   ```

## Error Reference

### Common Error Codes and Solutions

| Error Code | Message | Solution |
|------------|---------|----------|
| 401 | Unauthorized | Check GitHub token validity |
| 403 | Forbidden | Verify token permissions or rate limits |
| 404 | Not Found | Check repository name and access |
| 422 | Unprocessable Entity | Verify request parameters |
| 500 | Internal Server Error | GitHub API issue, retry later |

### Exit Codes

The monitoring system uses these exit codes:

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | All pipelines passed |
| 1 | Pipeline failure | Check failed workflows |
| 2 | Pending/timeout | Workflows still running or timed out |
| 130 | User interrupt | Monitoring was cancelled |

### Log Levels and Debugging

Enable different levels of logging:

```bash
# Minimal output
python scripts/github_pipeline_monitor.py --format minimal

# Standard output (default)
python scripts/github_pipeline_monitor.py

# Verbose output
python scripts/github_pipeline_monitor.py --verbose

# Debug output with cache stats
python scripts/github_pipeline_monitor.py --verbose --cache-stats
```

## Getting Additional Help

### Diagnostic Information Collection

When reporting issues, collect this information:

```bash
# System information
echo "OS: $(uname -s)"
echo "Python: $(python --version)"
echo "Git: $(git --version)"

# Configuration
echo "Token set: $([ -n "$GITHUB_TOKEN" ] && echo "Yes" || echo "No")"
echo "Repository: $(git remote get-url origin 2>/dev/null || echo "Not set")"

# Test basic functionality
python scripts/github_pipeline_monitor.py --status-only --verbose 2>&1 | head -20
```

### Debug Mode

Run in debug mode for maximum information:

```bash
# Enable all debugging
export GITHUB_PIPELINE_VERBOSE=true
export GITHUB_PIPELINE_DEBUG=true
python scripts/github_pipeline_monitor.py --verbose --cache-stats
```

### Community Resources

- **Documentation**: Check the main [GitHub Action Monitoring](GITHUB_ACTION_MONITORING.md) guide
- **Examples**: Review [Workflow Examples](WORKFLOW_EXAMPLES.md) for common patterns
- **Setup**: Follow [GitHub Token Setup](GITHUB_TOKEN_SETUP.md) for authentication

### Creating Support Requests

When creating support requests, include:

1. **Error message** (full text)
2. **Command used** (exact command line)
3. **Environment information** (OS, Python version)
4. **Configuration** (sanitized, no tokens)
5. **Steps to reproduce** the issue

This troubleshooting guide should help resolve most common issues. If you encounter problems not covered here, the diagnostic commands will help identify the root cause.