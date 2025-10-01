# GitHub Token Setup Guide

This guide walks you through setting up a GitHub Personal Access Token for the GitHub Actions monitoring system.

## Why You Need This

The GitHub Actions monitoring system requires a GitHub Personal Access Token to:
- Query workflow run status via GitHub's API
- Monitor pipeline progress in real-time
- Integrate pipeline status with local development tools

## Quick Setup (TL;DR)

1. Go to [GitHub Settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select **Actions: Read** permission only
4. Copy token and set: `export GITHUB_TOKEN="your_token_here"`
5. Test: `python scripts/github_pipeline_monitor.py --status-only`

## Step-by-Step Setup

### 1. Create a GitHub Personal Access Token

1. **Go to GitHub Settings**
   - Navigate to https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**
   - Click "Generate new token (classic)"
   - Give it a descriptive name like `mypylogger-pipeline-monitor`

3. **Select Minimal Required Permissions**
   - **IMPORTANT**: You only need **Actions: Read-only** permission
   - Uncheck all other permissions (Administration, Artifact metadata, etc.)
   - This follows the principle of least privilege

4. **Generate and Copy Token**
   - Click "Generate token"
   - **Copy the token immediately** - you won't see it again
   - Token will look like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. Set Up Environment Variable (Secure Personal Laptop)

For a secure personal laptop setup:

```bash
# Add to your shell profile (macOS/Linux with zsh)
echo 'export GITHUB_TOKEN=your_actual_token_here' >> ~/.zshrc

# Reload your shell configuration
source ~/.zshrc

# Verify the token is set
echo $GITHUB_TOKEN
```

For bash users:
```bash
echo 'export GITHUB_TOKEN=your_actual_token_here' >> ~/.bashrc
source ~/.bashrc
```

### 3. Test the Setup

```bash
# Test the GitHub monitoring system
python scripts/github_pipeline_monitor.py --status-only --repo your-username/your-repo

# You should see output like:
# 📊 Pipeline Status
# 📝 Commit: abc12345
# ✅ Overall Status: SUCCESS
# Workflows:
#   ✅ CI/CD Pipeline: success (1m 23s)
#   ✅ Security Scanning: success (45s)
```

## Security Considerations

### Personal Laptop (Recommended for Development)
- Token stored in shell profile (`~/.zshrc` or `~/.bashrc`)
- Only accessible to your user account
- Persists across terminal sessions
- Easy to rotate by updating the file

### Production/Shared Environments (Future Enhancement)
For production or shared environments, consider:
- CI/CD environment variables
- Secret management systems (HashiCorp Vault, AWS Secrets Manager)
- macOS Keychain integration
- Token rotation automation

## Troubleshooting

### "Environment variable GITHUB_TOKEN not found"
- Verify token is set: `echo $GITHUB_TOKEN`
- Reload shell: `source ~/.zshrc`
- Check token was added to correct profile file

### "GitHub API authentication failed"
- Verify token hasn't expired
- Check token has Actions: Read-only permission
- Test token manually: `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user`

### "Repository not found or not accessible"
- Verify repository name is correct
- Ensure token has access to the repository
- For private repos, token needs appropriate permissions

### "GitHub API rate limit exceeded"
- Wait for rate limit reset (usually 1 hour)
- Consider using authenticated requests (higher limits)
- Reduce polling frequency in configuration

## Token Management Best Practices

### Regular Rotation
- Rotate tokens every 90 days
- Use descriptive names to track token usage
- Remove unused tokens promptly

### Minimal Permissions
- Only grant Actions: Read-only for pipeline monitoring
- Avoid granting unnecessary permissions
- Review and audit token permissions regularly

### Secure Storage
- Never commit tokens to code repositories
- Use environment variables or secure secret storage
- Consider using short-lived tokens for automation

## Advanced Configuration

### Custom Configuration File
Create `.github-monitor.yml` in your project root:

```yaml
github:
  token: ${GITHUB_TOKEN}  # References environment variable
  repository: auto        # Auto-detect from git remote

monitoring:
  branches:
    - pre-release
    - main
  poll_interval: 30       # seconds
  timeout: 30            # minutes

output:
  format: console        # console, json, minimal
  colors: true
  progress_indicators: true
```

### Multiple Repositories
For monitoring multiple repositories, you can:
- Use the same token across repositories (if permissions allow)
- Create repository-specific tokens for better security isolation
- Configure different monitoring settings per repository

## Getting Help

If you encounter issues:

1. **Check Configuration**
   ```bash
   python scripts/github_monitor_config.py --validate
   ```

2. **Get Setup Help**
   ```bash
   python scripts/github_monitor_config.py --setup-help
   ```

3. **Create Sample Configuration**
   ```bash
   python scripts/github_monitor_config.py --create-config
   ```

4. **View Current Configuration**
   ```bash
   python scripts/github_monitor_config.py --show-config
   ```

## Example: Complete Setup Session

Here's what a successful setup looks like:

```bash
# 1. Set up token (replace with your actual token)
$ echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.zshrc
$ source ~/.zshrc

# 2. Verify token
$ echo $GITHUB_TOKEN
ghp_your_token_here

# 3. Test monitoring
$ python scripts/github_pipeline_monitor.py --status-only --repo stabbotco1/mypylogger

📊 Pipeline Status
📝 Commit: 2f40aaa5
❌ Overall Status: FAILURE

Workflows:
  ❌ Security Scanning: failure (25s)
  ❌ CI/CD Pipeline: failure (2m 9s)

Summary:
  Total workflows: 2
  ✗ 2 failed
  Total time: 2m 34s
```

Success! The system is now monitoring your GitHub Actions pipelines.