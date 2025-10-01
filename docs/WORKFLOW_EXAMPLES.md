# GitHub Action Monitoring - Workflow Examples

This document provides practical examples of how to integrate GitHub Action monitoring into common development workflows.

## Table of Contents

- [Basic Development Workflows](#basic-development-workflows)
- [Team Collaboration Workflows](#team-collaboration-workflows)
- [Release Management Workflows](#release-management-workflows)
- [CI/CD Integration Examples](#cicd-integration-examples)
- [Emergency Procedures](#emergency-procedures)

## Basic Development Workflows

### Feature Development Workflow

This is the most common workflow for developing new features:

```bash
# 1. Create and switch to feature branch
git checkout -b feature/user-authentication
git push -u origin feature/user-authentication

# 2. Develop your feature with iterative commits
git add .
git commit -m "Add user authentication endpoints"
git push origin feature/user-authentication

# 3. Monitor pipeline status after each push
python scripts/github_pipeline_monitor.py --after-push --branch feature/user-authentication

# 4. Run local tests with pipeline checking
export GITHUB_PIPELINE_CHECK=true
./scripts/run-complete-test-suite.sh

# 5. If all tests pass, create pull request
gh pr create --title "Add user authentication" --body "Implements user login/logout functionality"
```

### Bug Fix Workflow

For fixing bugs with immediate pipeline feedback:

```bash
# 1. Create bug fix branch
git checkout -b bugfix/fix-login-validation
git push -u origin bugfix/fix-login-validation

# 2. Make the fix
git add .
git commit -m "Fix login validation edge case"
git push origin bugfix/fix-login-validation

# 3. Monitor pipeline with verbose output
python scripts/github_pipeline_monitor.py --after-push --verbose --branch bugfix/fix-login-validation

# 4. If pipeline fails, check specific failure details
python scripts/github_pipeline_monitor.py --status-only --format json | jq '.workflow_runs[] | select(.conclusion == "failure")'

# 5. Fix issues and push again
git add .
git commit -m "Address linting issues"
git push origin bugfix/fix-login-validation
```

### Hotfix Workflow

For urgent production fixes:

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. Make minimal fix
git add .
git commit -m "Fix critical security vulnerability"
git push origin hotfix/critical-security-fix

# 3. Monitor with high priority
python scripts/github_pipeline_monitor.py --after-push --timeout 15 --poll-interval 10

# 4. If successful, merge to main immediately
git checkout main
git merge hotfix/critical-security-fix
git push origin main

# 5. Monitor main branch pipeline
python scripts/github_pipeline_monitor.py --after-push --branch main
```

## Team Collaboration Workflows

### Code Review Workflow

Integrating pipeline monitoring with code reviews:

```bash
# Reviewer workflow
# 1. Check out the PR branch
gh pr checkout 123

# 2. Review code locally
git log --oneline -5

# 3. Check current pipeline status
python scripts/github_pipeline_monitor.py --status-only

# 4. Run local tests with pipeline checking
make test-complete-with-pipeline

# 5. If everything passes, approve the PR
gh pr review --approve --body "LGTM! All pipelines passing."
```

### Pair Programming Workflow

For collaborative development:

```bash
# Driver's machine
# 1. Create shared branch
git checkout -b feature/shared-component
git push -u origin feature/shared-component

# 2. Make changes and push frequently
git add .
git commit -m "WIP: Add component structure"
git push origin feature/shared-component

# 3. Monitor pipeline in background
python scripts/github_pipeline_monitor.py --after-push &

# Navigator can monitor on their machine
# 4. Navigator monitors progress
python scripts/github_pipeline_monitor.py --status-only --format minimal

# 5. Both can see real-time updates
watch -n 30 'python scripts/github_pipeline_monitor.py --status-only --format minimal'
```

### Integration Branch Workflow

For teams using integration branches:

```bash
# 1. Merge feature to integration branch
git checkout integration
git pull origin integration
git merge feature/new-feature
git push origin integration

# 2. Monitor integration pipeline
python scripts/github_pipeline_monitor.py --after-push --branch integration --timeout 45

# 3. If successful, merge to pre-release
git checkout pre-release
git pull origin pre-release
git merge integration
git push origin pre-release

# 4. Monitor pre-release pipeline
python scripts/github_pipeline_monitor.py --after-push --branch pre-release
```

## Release Management Workflows

### Standard Release Workflow

Complete release process with pipeline monitoring:

```bash
# 1. Prepare release branch
git checkout -b release/v1.2.0
git push -u origin release/v1.2.0

# 2. Update version numbers and changelog
# ... make version updates ...
git add .
git commit -m "Prepare release v1.2.0"
git push origin release/v1.2.0

# 3. Monitor release preparation pipeline
python scripts/github_pipeline_monitor.py --after-push --branch release/v1.2.0

# 4. Merge to pre-release for final testing
git checkout pre-release
git merge release/v1.2.0
git push origin pre-release

# 5. Wait for all pre-release pipelines
python scripts/github_pipeline_monitor.py --wait-for-pipeline --timeout 60

# 6. If successful, merge to main
git checkout main
git merge pre-release
git tag v1.2.0
git push origin main --tags

# 7. Monitor production deployment pipeline
python scripts/github_pipeline_monitor.py --after-push --branch main --verbose
```

### Canary Release Workflow

For gradual rollouts:

```bash
# 1. Create canary branch
git checkout -b canary/v1.2.0
git push -u origin canary/v1.2.0

# 2. Deploy to canary environment
git add .
git commit -m "Deploy v1.2.0 to canary"
git push origin canary/v1.2.0

# 3. Monitor canary deployment
python scripts/github_pipeline_monitor.py --after-push --branch canary/v1.2.0

# 4. Monitor canary metrics (external monitoring)
# ... check application metrics ...

# 5. If canary is successful, promote to production
git checkout main
git merge canary/v1.2.0
git push origin main

# 6. Monitor production deployment
python scripts/github_pipeline_monitor.py --after-push --branch main --timeout 30
```

### Rollback Workflow

For handling failed releases:

```bash
# 1. Identify the issue
python scripts/github_pipeline_monitor.py --status-only --format json > pipeline_status.json

# 2. Check failed workflows
cat pipeline_status.json | jq '.workflow_runs[] | select(.conclusion == "failure")'

# 3. Quick rollback to previous version
git checkout main
git revert HEAD --no-edit
git push origin main

# 4. Monitor rollback pipeline
python scripts/github_pipeline_monitor.py --after-push --branch main --poll-interval 10

# 5. Verify rollback success
python scripts/github_pipeline_monitor.py --status-only
```

## CI/CD Integration Examples

### GitHub Actions Integration

Integrate monitoring into your GitHub Actions workflow:

```yaml
# .github/workflows/ci.yml
name: CI with Pipeline Monitoring

on:
  push:
    branches: [ main, pre-release ]
  pull_request:
    branches: [ main ]

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
        run: |
          pip install -r requirements.txt
      
      - name: Run tests with pipeline monitoring
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_PIPELINE_CHECK: true
        run: |
          ./scripts/run-complete-test-suite.sh
      
      - name: Monitor dependent pipelines
        if: github.ref == 'refs/heads/pre-release'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/github_pipeline_monitor.py --status-only --format json
```

### Jenkins Integration

For Jenkins CI/CD pipelines:

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        GITHUB_TOKEN = credentials('github-token')
        GITHUB_PIPELINE_CHECK = 'true'
    }
    
    stages {
        stage('Test') {
            steps {
                sh './scripts/run-complete-test-suite.sh'
            }
        }
        
        stage('Monitor Pipelines') {
            when {
                branch 'pre-release'
            }
            steps {
                sh '''
                    python scripts/github_pipeline_monitor.py --status-only --format json > pipeline_status.json
                    cat pipeline_status.json
                '''
                archiveArtifacts artifacts: 'pipeline_status.json'
            }
        }
        
        stage('Wait for Dependencies') {
            when {
                branch 'main'
            }
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    sh 'python scripts/github_pipeline_monitor.py --wait-for-pipeline'
                }
            }
        }
    }
    
    post {
        failure {
            sh '''
                echo "Pipeline failed. Checking GitHub Actions status..."
                python scripts/github_pipeline_monitor.py --status-only --verbose
            '''
        }
    }
}
```

### GitLab CI Integration

For GitLab CI/CD:

```yaml
# .gitlab-ci.yml
stages:
  - test
  - monitor
  - deploy

variables:
  GITHUB_PIPELINE_CHECK: "true"

test:
  stage: test
  script:
    - ./scripts/run-complete-test-suite.sh
  artifacts:
    reports:
      junit: test-results.xml

monitor_github_pipelines:
  stage: monitor
  script:
    - python scripts/github_pipeline_monitor.py --status-only --format json
  artifacts:
    reports:
      junit: pipeline-status.json
  only:
    - pre-release
    - main

deploy:
  stage: deploy
  script:
    - python scripts/github_pipeline_monitor.py --wait-for-pipeline --timeout 30
    - ./deploy.sh
  only:
    - main
```

## Emergency Procedures

### Pipeline Failure Emergency Response

When pipelines fail and you need to respond quickly:

```bash
# 1. Immediate status check
python scripts/github_pipeline_monitor.py --status-only --format json > emergency_status.json

# 2. Identify failed workflows
cat emergency_status.json | jq -r '.workflow_runs[] | select(.conclusion == "failure") | "\(.name): \(.html_url)"'

# 3. Check if it's a transient failure
python scripts/github_pipeline_monitor.py --status-only --verbose

# 4. If transient, retry the workflow (via GitHub UI or API)
# If systematic, proceed with emergency bypass

# 5. Emergency bypass for critical fixes
export GITHUB_PIPELINE_BYPASS=true
./scripts/run-complete-test-suite.sh

# 6. Document the bypass decision
echo "Emergency bypass used: $(date) - Reason: Critical production issue" >> emergency_log.txt
```

### Offline Development

When GitHub API is unavailable:

```bash
# 1. Disable pipeline checking
export GITHUB_PIPELINE_CHECK=false

# 2. Run local tests only
./scripts/run-complete-test-suite.sh

# 3. Use cached status if available
python scripts/github_pipeline_monitor.py --cache-stats

# 4. Work with stale cache data
python scripts/github_pipeline_monitor.py --status-only --allow-stale

# 5. Re-enable when connectivity returns
unset GITHUB_PIPELINE_CHECK  # Returns to default behavior
```

### Rate Limit Emergency

When hitting GitHub API rate limits:

```bash
# 1. Check current rate limit status
python scripts/github_pipeline_monitor.py --cache-stats

# 2. Increase polling intervals
export GITHUB_PIPELINE_POLL_INTERVAL=120  # 2 minutes

# 3. Use cached data more aggressively
python scripts/github_pipeline_monitor.py --status-only --allow-stale

# 4. Wait for rate limit reset
python -c "
import json
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

## Advanced Workflow Patterns

### Multi-Repository Coordination

For projects spanning multiple repositories:

```bash
# 1. Monitor multiple repositories
repos=("org/repo1" "org/repo2" "org/repo3")

for repo in "${repos[@]}"; do
    echo "Checking $repo..."
    python scripts/github_pipeline_monitor.py --repo "$repo" --status-only --format minimal
done

# 2. Wait for all repositories to complete
for repo in "${repos[@]}"; do
    echo "Waiting for $repo..."
    python scripts/github_pipeline_monitor.py --repo "$repo" --wait-for-pipeline --timeout 20 &
done
wait

echo "All repositories completed!"
```

### Conditional Pipeline Monitoring

Monitor different pipelines based on changes:

```bash
# 1. Check what files changed
changed_files=$(git diff --name-only HEAD~1)

# 2. Determine monitoring strategy
if echo "$changed_files" | grep -q "src/"; then
    echo "Source code changed - monitoring all pipelines"
    python scripts/github_pipeline_monitor.py --wait-for-pipeline --timeout 45
elif echo "$changed_files" | grep -q "docs/"; then
    echo "Documentation changed - monitoring docs pipeline only"
    python scripts/github_pipeline_monitor.py --status-only --format minimal
else
    echo "No significant changes - quick status check"
    python scripts/github_pipeline_monitor.py --status-only
fi
```

### Performance-Aware Monitoring

Adjust monitoring based on system performance:

```bash
# 1. Check system load
load_avg=$(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')

# 2. Adjust polling based on load
if (( $(echo "$load_avg > 2.0" | bc -l) )); then
    echo "High system load - reducing monitoring frequency"
    export GITHUB_PIPELINE_POLL_INTERVAL=60
else
    echo "Normal system load - standard monitoring"
    export GITHUB_PIPELINE_POLL_INTERVAL=30
fi

# 3. Monitor with adjusted settings
python scripts/github_pipeline_monitor.py --after-push
```

## Troubleshooting Workflows

### Debug Failed Pipeline

When a pipeline fails and you need to investigate:

```bash
# 1. Get detailed failure information
python scripts/github_pipeline_monitor.py --status-only --verbose --format json > failure_details.json

# 2. Extract failure information
cat failure_details.json | jq -r '.workflow_runs[] | select(.conclusion == "failure") | {name: .name, url: .html_url, conclusion: .conclusion}'

# 3. Check if it's a known issue
grep -r "$(cat failure_details.json | jq -r '.workflow_runs[0].name')" docs/troubleshooting/

# 4. Reproduce locally if possible
export GITHUB_PIPELINE_CHECK=false
./scripts/run-complete-test-suite.sh

# 5. Fix and retry
git add .
git commit -m "Fix pipeline issue"
git push origin current-branch
python scripts/github_pipeline_monitor.py --after-push
```

### Performance Debugging

When monitoring is slow or inefficient:

```bash
# 1. Check cache performance
python scripts/github_pipeline_monitor.py --cache-stats --verbose

# 2. Monitor API usage
python -c "
from scripts.github_pipeline_monitor import GitHubPipelineMonitor
from scripts.github_monitor_config import ConfigManager

config = ConfigManager().load_config()
monitor = GitHubPipelineMonitor(config)
stats = monitor.get_cache_statistics()

print(f'Cache hit ratio: {stats[\"cache\"][\"hit_ratio\"]:.1%}')
print(f'Recent requests: {stats[\"requests\"][\"recent_requests_10min\"]}')
if 'rate_limit' in stats and stats['rate_limit']:
    print(f'Rate limit remaining: {stats[\"rate_limit\"][\"remaining\"]}')
"

# 3. Optimize polling strategy
export GITHUB_PIPELINE_POLL_INTERVAL=45  # Slower polling
python scripts/github_pipeline_monitor.py --after-push

# 4. Clear cache if needed
python -c "
from scripts.github_cache_manager import create_cache_manager
cache = create_cache_manager()
cleared = cache.invalidate_cache()
print(f'Cleared {cleared} cache entries')
"
```

These workflow examples provide practical guidance for integrating GitHub Action monitoring into real development scenarios. Choose the patterns that best fit your team's workflow and customize them as needed.