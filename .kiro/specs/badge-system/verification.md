# Badge Verification Specification

**Status:** Verified Implementation  
**Last Updated:** October 8, 2025  
**Purpose:** Document badge health monitoring and validation systems

---

## Overview

Badge verification ensures all 13 badges in the mypylogger project remain functional, accessible, and accurate. The verification system uses three orthogonal approaches: visual inspection, automated HTTP validation, and continuous CI monitoring.

**Verification Components:**
1. **validate_badges.py** - Standalone badge validation script
2. **badge_health_monitor.py** - CI-integrated monitoring with issue creation
3. **badge-health.yml** - GitHub Actions workflow for automated checks

**Key Principles:**
- **Three orthogonal methods** - Visual, HTTP, automated CI
- **Fail fast** - Detect badge failures immediately
- **Actionable alerts** - Create GitHub issues with specific remediation steps
- **No false positives** - Only alert on actual failures

---

## Verification Method 1: Visual Inspection

### Purpose

Human verification that badges display correctly and contain accurate information.

### When to Use

- After any badge-related changes
- Before releases
- When automated checks fail
- Weekly manual spot-checks

### Inspection Checklist

**Location:** README.md, badges section

**For Each Badge:**
1. Badge renders (not broken image)
2. Text is readable and accurate
3. Color appropriate for status
4. Logo displays (if applicable)
5. Badge links to correct destination (if clickable)

**Tier 1 Badges (Core):**
- Build Status: Shows recent build status (passing/failing)
- Coverage: Shows current coverage percentage
- Security: Shows security scan status
- License: Shows "MIT" (static)

**Tier 2 Badges (Quality):**
- PyPI Version: Matches latest PyPI release
- Python Versions: Lists 3.9, 3.10, 3.11, 3.12
- Documentation: Shows appropriate status

**Tier 3 Badges (Performance/Analytics):**
- Ubuntu Performance: Shows latency and throughput
- macOS Performance: Shows latency and throughput
- Downloads: Shows download count

### Visual Inspection Procedure

**Step 1: Open README.md**
- On GitHub: Navigate to repository main page
- Locally: Open in markdown viewer

**Step 2: Check Each Badge**
- Verify badge renders as image
- Read badge text
- Compare with expected values

**Step 3: Test Clickability**
- Click each badge
- Verify links to correct destination
- Check linked page loads correctly

**Step 4: Document Issues**
- Note any broken badges
- Record expected vs actual values
- Screenshot if helpful

### Common Visual Issues

**Gray "Unknown" Badge:**
- Cause: Badge URL malformed or service unavailable
- Action: Check badge URL syntax

**Stale Values:**
- Cause: Cache or update mechanism failure
- Action: Force refresh, check update workflow

**Broken Image:**
- Cause: shields.io unavailable or badge URL invalid
- Action: Verify badge URL, check shields.io status

---

## Verification Method 2: HTTP Validation

### Purpose

Automated validation that badge URLs return valid responses and render correctly.

### Script: validate_badges.py

**Location:** scripts/validate_badges.py

**Function:** Programmatically verify all badge URLs are accessible and return valid SVG images.

### Script Architecture

**Key Functions:**
1. Badge URL extraction from README.md
2. HTTP request to each badge URL
3. Response validation (status code, content type)
4. Response time monitoring
5. Report generation

### Implementation Details

**Badge URL Extraction:**

import re

def extract_badge_urls(readme_path):
    """Extract all badge URLs from README.md"""
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Pattern: ![badge](url)
    pattern = r'!\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    badges = []
    for alt_text, url in matches:
        if 'shields.io' in url or 'badge' in url.lower():
            badges.append({
                'name': alt_text,
                'url': url
            })
    
    return badges

**HTTP Validation:**

import requests

def validate_badge(badge):
    """Validate single badge URL"""
    try:
        response = requests.get(
            badge['url'],
            timeout=5,
            headers={'User-Agent': 'badge-validator/1.0'}
        )
        
        return {
            'name': badge['name'],
            'url': badge['url'],
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'response_time': response.elapsed.total_seconds(),
            'success': response.status_code == 200 and 'svg' in response.headers.get('Content-Type', '')
        }
    except requests.exceptions.RequestException as e:
        return {
            'name': badge['name'],
            'url': badge['url'],
            'success': False,
            'error': str(e)
        }

**Report Generation:**

def generate_report(results):
    """Generate validation report"""
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    print(f"\nBadge Validation Report")
    print(f"{'='*50}")
    print(f"Total badges: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"\nDetails:")
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['name']}")
        if not result['success']:
            print(f"  URL: {result['url']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Status: {result.get('status_code', 'N/A')}")
    
    return failed == 0

### Usage

**Command Line:**

# Validate all badges
python scripts/validate_badges.py

# Validate and exit with error code if failures
python scripts/validate_badges.py --strict

# Output JSON format
python scripts/validate_badges.py --format json

**Expected Output:**

Badge Validation Report
==================================================
Total badges: 13
Passed: 13
Failed: 0

Details:
✓ Build Status
✓ Coverage
✓ Security
✓ License
✓ PyPI Version
✓ Python Versions
✓ Documentation
✓ Ubuntu
✓ macOS
✓ Downloads
✓ Code Quality
✓ Maintainability
✓ Last Commit

### Validation Criteria

**Success Criteria:**
- HTTP status code: 200
- Content-Type: contains "svg" or "image/svg+xml"
- Response time: < 10 seconds
- No exceptions during request

**Failure Conditions:**
- HTTP status code: 4xx or 5xx
- Content-Type: not SVG
- Timeout (> 10 seconds)
- Network error or exception

### Limitations

**Cannot Validate:**
- Actual badge text content (dynamic SVG)
- Badge accuracy (displayed values correct)
- Visual rendering quality
- Link destinations (if badge is clickable)

**Can Validate:**
- Badge URL accessibility
- Badge service availability
- Response format (SVG)
- Response time performance

---

## Verification Method 3: Automated CI Monitoring

### Purpose

Continuous automated monitoring with GitHub issue creation for failures.

### Script: badge_health_monitor.py

**Location:** scripts/badge_health_monitor.py

**Function:** CI-integrated badge monitoring with automated issue creation and performance tracking.

### Script Architecture

**Key Functions:**
1. Badge validation (reuses validate_badges.py logic)
2. Workflow freshness checking
3. GitHub issue creation/updating
4. Performance metric tracking
5. Multiple output formats

### Implementation Details

#### Badge Validation

**Reuses core validation:**

from validate_badges import extract_badge_urls, validate_badge

def monitor_badges():
    """Monitor all badges and return health status"""
    badges = extract_badge_urls('README.md')
    results = [validate_badge(b) for b in badges]
    
    failures = [r for r in results if not r['success']]
    
    return {
        'total': len(results),
        'passed': len(results) - len(failures),
        'failed': len(failures),
        'failures': failures,
        'timestamp': datetime.now().isoformat()
    }

#### Workflow Freshness Check

**Purpose:** Detect stale performance badges when workflow hasn't run recently.

import subprocess
from datetime import datetime, timedelta

def check_workflow_freshness(workflow_name, max_age_days=10):
    """Check if workflow has run recently"""
    try:
        # Get last workflow run
        result = subprocess.run(
            ['gh', 'run', 'list', '--workflow', workflow_name, '--limit', '1', '--json', 'createdAt'],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        runs = json.loads(result.stdout)
        
        if not runs:
            return {
                'stale': True,
                'reason': 'No workflow runs found',
                'workflow': workflow_name
            }
        
        last_run = datetime.fromisoformat(runs[0]['createdAt'].replace('Z', '+00:00'))
        age = datetime.now(last_run.tzinfo) - last_run
        
        if age.days > max_age_days:
            return {
                'stale': True,
                'reason': f'Last run {age.days} days ago',
                'workflow': workflow_name,
                'last_run': last_run.isoformat()
            }
        
        return {'stale': False, 'workflow': workflow_name}
        
    except Exception as e:
        return {
            'stale': False,
            'error': str(e),
            'workflow': workflow_name
        }

**Workflows to Monitor:**
- performance-badge-update.yml (weekly, max age: 10 days)
- ci.yml (on every push, max age: 7 days)
- security.yml (weekly, max age: 10 days)

#### GitHub Issue Creation

**Purpose:** Automatically create issues when badge failures detected.

def create_or_update_issue(health_status):
    """Create or update GitHub issue for badge failures"""
    if health_status['failed'] == 0:
        # Close existing issue if all badges healthy
        close_badge_health_issue()
        return
    
    title = f"Badge Health Alert: {health_status['failed']} badge(s) failing"
    
    body = f"""## Badge Health Report
    
**Status:** {health_status['failed']} of {health_status['total']} badges failing
**Timestamp:** {health_status['timestamp']}

### Failed Badges

"""
    
    for failure in health_status['failures']:
        body += f"#### {failure['name']}\n"
        body += f"- **URL:** {failure['url']}\n"
        if 'error' in failure:
            body += f"- **Error:** {failure['error']}\n"
        else:
            body += f"- **Status Code:** {failure.get('status_code', 'N/A')}\n"
        body += "\n"
    
    body += """### Remediation Steps

1. Check if shields.io is operational: https://status.shields.io
2. Verify badge URLs in README.md are correct
3. For workflow-driven badges, check recent workflow runs
4. Run `python scripts/validate_badges.py` locally for details

### Auto-Resolution

This issue will automatically close when all badges return to healthy status.
"""
    
    # Check for existing issue
    existing_issue = find_badge_health_issue()
    
    if existing_issue:
        update_issue(existing_issue['number'], body)
    else:
        create_issue(title, body, labels=['badge-health', 'automated'])

**Deduplication Logic:**

def find_badge_health_issue():
    """Find existing badge health issue to avoid spam"""
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--label', 'badge-health', '--state', 'open', '--json', 'number,title'],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        issues = json.loads(result.stdout)
        
        # Return first badge health issue
        return issues[0] if issues else None
        
    except Exception as e:
        print(f"Error checking for existing issues: {e}")
        return None

#### Performance Tracking

**Purpose:** Track badge response times over time.

def track_performance(results):
    """Track badge performance metrics"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'badges': []
    }
    
    for result in results:
        if result['success']:
            metrics['badges'].append({
                'name': result['name'],
                'response_time': result.get('response_time', 0),
                'status_code': result['status_code']
            })
    
    # Append to metrics file
    with open('.kiro/metrics/badge_performance.jsonl', 'a') as f:
        f.write(json.dumps(metrics) + '\n')

### Usage

**Command Line:**

# Run badge health check
python scripts/badge_health_monitor.py

# Create GitHub issue if failures detected
python scripts/badge_health_monitor.py --create-issue

# Output in different formats
python scripts/badge_health_monitor.py --format json
python scripts/badge_health_monitor.py --format markdown

**Expected Output:**

Badge Health Monitor
==================================================
Monitoring 13 badges...

✓ All badges healthy (13/13 passed)

Checking workflow freshness...
✓ performance-badge-update.yml: Last run 3 days ago
✓ ci.yml: Last run 2 hours ago
✓ security.yml: Last run 5 days ago

No action required.

---

## Workflow Integration

### Workflow: badge-health.yml

**Location:** .github/workflows/badge-health.yml

**Purpose:** Automated badge health monitoring in CI/CD.

### Workflow Configuration

**Triggers:**

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:

**Why These Triggers:**
- **Push/PR:** Catch badge breakage from README changes
- **Daily schedule:** Regular health checks
- **Manual dispatch:** On-demand verification

### Workflow Steps

**Step 1: Checkout**

- name: Checkout repository
  uses: actions/checkout@v3

**Step 2: Setup Python**

- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

**Step 3: Install Dependencies**

- name: Install dependencies
  run: |
    pip install requests

**Step 4: Run Badge Validation**

- name: Validate badges
  run: python scripts/validate_badges.py --strict

**Step 5: Run Health Monitor**

- name: Check badge health
  run: python scripts/badge_health_monitor.py --format json > badge_health.json

**Step 6: Upload Artifact**

- name: Upload health report
  uses: actions/upload-artifact@v3
  with:
    name: badge-health-report
    path: badge_health.json

**Step 7: Create Issue on Failure**

- name: Create issue if badges failing
  if: failure()
  run: python scripts/badge_health_monitor.py --create-issue
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

### Workflow Behavior

**On Success:**
- All badges validated
- Health report uploaded as artifact
- No issues created
- Workflow passes

**On Failure:**
- Badge validation fails
- Health report shows failures
- GitHub issue created/updated
- Workflow marked as failed

**Issue Management:**
- One issue per badge health problem
- Issue updated if already exists (no spam)
- Issue auto-closes when badges healthy again

---

## Verification Schedules

### Continuous Verification

**Trigger:** Every push to main

**Actions:**
1. Run validate_badges.py
2. Run badge_health_monitor.py
3. Upload health report artifact

**Purpose:** Immediate detection of badge breakage from code changes

### Daily Verification

**Trigger:** 6 AM UTC daily

**Actions:**
1. Full badge validation
2. Workflow freshness checks
3. Create issue if failures detected

**Purpose:** Regular health monitoring, catch external service issues

### Weekly Verification

**Trigger:** Manual or as needed

**Actions:**
1. Visual inspection of all badges
2. Verify badge values match expectations
3. Test badge clickability
4. Review any open badge health issues

**Purpose:** Human verification, catch issues automation misses

### Pre-Release Verification

**Trigger:** Before publishing new version

**Actions:**
1. Run all automated checks
2. Visual inspection
3. Verify version badges will update correctly
4. Check all badge links functional

**Purpose:** Ensure badges accurate for release

---

## Troubleshooting Verification Failures

### Validation Script Fails

**Symptom:** validate_badges.py exits with non-zero code

**Diagnosis:**

Run script locally:
python scripts/validate_badges.py

Check output for specific failing badges

**Common Causes:**
1. shields.io service outage
2. Badge URL typo in README.md
3. Network connectivity issue
4. Workflow hasn't run (performance badges stale)

**Resolution:**
- Check shields.io status page
- Verify badge URLs in README.md
- Re-run workflows if needed
- Check network/firewall if local

### Health Monitor Creates False Issue

**Symptom:** GitHub issue created but badges appear healthy

**Diagnosis:**

Check issue details:
- Which badges flagged as failing?
- What error reported?

Manually test badge URLs:
curl -I https://img.shields.io/badge/...

**Common Causes:**
1. Transient network error
2. shields.io temporary outage
3. Rate limiting

**Resolution:**
- Wait 10 minutes and re-run
- Close issue if badges now healthy
- Adjust monitoring thresholds if too sensitive

### Workflow Freshness Check Fails

**Symptom:** badge_health_monitor.py reports stale workflow

**Diagnosis:**

Check workflow run history:
gh run list --workflow=performance-badge-update.yml

Verify last run time:
gh run view --workflow=performance-badge-update.yml

**Common Causes:**
1. Workflow schedule disabled
2. Workflow file has errors
3. GitHub Actions quota exceeded

**Resolution:**
- Enable workflow schedule if disabled
- Fix workflow syntax errors
- Check Actions usage in repository settings
- Manually trigger workflow: gh workflow run performance-badge-update.yml

### All Badges Fail Simultaneously

**Symptom:** validate_badges.py reports all badges failing

**Diagnosis:**

Test shields.io directly:
curl -I https://img.shields.io/badge/test-test-blue

Check shields.io status:
Visit https://status.shields.io

**Common Causes:**
1. shields.io service outage
2. Network connectivity issue
3. DNS resolution problem

**Resolution:**
- Wait for shields.io to recover
- Check network connectivity
- Verify DNS resolving shields.io correctly

---

## Maintenance Procedures

### Adding New Badge

**Checklist:**
1. Add badge to README.md
2. Run validate_badges.py to verify accessible
3. Update expected badge count in tests (if hardcoded)
4. Verify badge appears in health reports
5. Document badge in appropriate spec file

### Removing Badge

**Checklist:**
1. Remove badge from README.md
2. Run validate_badges.py to verify count correct
3. Update documentation
4. Close any related badge health issues

### Updating Validation Scripts

**Testing:**
1. Run locally against current README.md
2. Verify all badges detected
3. Verify correct pass/fail status
4. Check report format
5. Test issue creation (dry-run mode)

**Deployment:**
1. Commit script changes
2. Push to main
3. Verify workflow runs successfully
4. Monitor first few automated runs

---

## Metrics and Reporting

### Badge Health Metrics

**Tracked Metrics:**
- Total badges: 13
- Pass rate: percentage of badges accessible
- Average response time: shields.io performance
- Failure count by badge: identify problematic badges
- Workflow freshness: days since last run

**Metric Storage:**

.kiro/metrics/badge_performance.jsonl (one JSON object per line)

Example:
{"timestamp": "2025-10-08T10:00:00Z", "badges": [{"name": "Build Status", "response_time": 0.234, "status_code": 200}, ...]}

### Report Formats

**Console Output (Human):**

Badge Validation Report
==================================================
Total badges: 13
Passed: 13
Failed: 0

**JSON Output (Machine):**

{
  "total": 13,
  "passed": 13,
  "failed": 0,
  "timestamp": "2025-10-08T10:00:00Z",
  "failures": []
}

**Markdown Output (GitHub):**

# Badge Health Report

**Status:** ✓ All badges healthy
**Timestamp:** 2025-10-08 10:00:00 UTC
**Total:** 13 badges
**Passed:** 13
**Failed:** 0

### Historical Analysis

**Purpose:** Identify patterns in badge failures

**Data Source:** .kiro/metrics/badge_performance.jsonl

**Analysis:**

import json
from collections import Counter

def analyze_badge_failures(log_file):
    """Analyze badge failure patterns"""
    failures_by_badge = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            if 'failures' in data:
                for failure in data['failures']:
                    failures_by_badge[failure['name']] += 1
    
    print("Badge Failure Frequency:")
    for badge, count in failures_by_badge.most_common():
        print(f"{badge}: {count} failures")

**Usage:**

python -c "from badge_health_monitor import analyze_badge_failures; analyze_badge_failures('.kiro/metrics/badge_performance.jsonl')"

---

## Integration with Other Systems

### Pre-Commit Hooks

**Purpose:** Validate badges before committing README changes

**Setup:**

.git/hooks/pre-commit:
#!/bin/bash
if git diff --cached --name-only | grep -q "README.md"; then
    echo "README.md changed, validating badges..."
    python scripts/validate_badges.py --strict
    if [ $? -ne 0 ]; then
        echo "Badge validation failed. Commit aborted."
        exit 1
    fi
fi

### Release Process Integration

**Purpose:** Ensure badges accurate before release

**Release Checklist Item:**

- [ ] Run badge validation: python scripts/validate_badges.py
- [ ] Visual inspection: All badges display correctly
- [ ] Version badge: Will update after PyPI publish (5-10 min)
- [ ] Performance badges: Updated within last week

### Documentation Generation

**Purpose:** Include badge health in generated docs

**Implementation:**

# In docs build script
python scripts/badge_health_monitor.py --format markdown > docs/badge-status.md

**Result:** docs/badge-status.md included in documentation site

---

## Related Documentation

**Common Principles:** See .kiro/steering/badge-standards.md
**System Overview:** See .kiro/specs/badge-system/overview.md
**Core Badges:** See .kiro/specs/badge-system/core-badges.md
**Quality Badges:** See .kiro/specs/badge-system/quality-badges.md
**Performance Badges:** See .kiro/specs/badge-system/performance-badges.md
**Troubleshooting:** See .kiro/specs/badge-system/troubleshooting.md

---

**End of Badge Verification Specification**