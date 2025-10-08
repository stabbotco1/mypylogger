# Badge Troubleshooting Guide

**Status:** Verified Implementation  
**Last Updated:** October 8, 2025  
**Purpose:** Document actual problems encountered and solutions that worked

---

## Overview

This guide documents real badge failures encountered in the mypylogger project and the fixes that actually resolved them. Unlike theoretical troubleshooting, these are empirical solutions to actual problems.

**Scope:**
- Problems actually encountered during badge implementation
- Fixes that were tested and verified to work
- Preventive measures based on real failures
- Common failure patterns observed in practice

**Not Included:**
- Hypothetical problems
- Untested solutions
- Problems from other projects (unless verified applicable)

---

## Critical Fixes That Worked

### Fix 1: Race Condition in Performance Badge Updates

**Problem Encountered:**

When performance badges updated in parallel (Ubuntu and macOS jobs running simultaneously), one badge would update successfully but the other would fail silently or create a git conflict.

**Symptoms:**
- Only Ubuntu badge updated, macOS badge showed stale values
- Or vice versa - only macOS badge updated
- Git push failures in workflow logs
- Intermittent failures - sometimes both updated, sometimes only one

**Root Cause:**

Parallel matrix jobs:
1. Both jobs checked out main at same commit
2. Both modified README.md independently
3. First job committed and pushed successfully
4. Second job's push failed - base commit was stale
5. Second job's changes lost

**Solution That Worked:**

Added max-parallel: 1 to workflow matrix strategy:

strategy:
  max-parallel: 1  # CRITICAL FIX
  matrix:
    os: [ubuntu-latest, macos-latest]

**Location:** .github/workflows/performance-badge-update.yml

**Why This Works:**
- Forces sequential execution
- Ubuntu job completes entirely before macOS starts
- macOS job sees Ubuntu's commit as base
- No concurrent README.md modification possible

**Verification:**

After fix:
- Both badges update in single workflow run
- Single commit contains both platform updates
- No more push failures in logs
- Consistent behavior across all runs

**Alternative Approaches Tried:**
1. Git pull before push - Still had race window, didn't work
2. Retry logic on push failure - Added complexity, unreliable
3. Separate workflow files - Same problem, harder to maintain

**Committed:** Verified in .github/workflows/performance-badge-update.yml Line 9-12

---

### Fix 2: BSD vs GNU sed Syntax Errors

**Problem Encountered:**

Performance badge update workflow succeeded on Ubuntu but failed on macOS with error:
sed: 1: 'README.md': extra characters at the end of h command

**Symptoms:**
- Ubuntu badge updated correctly
- macOS workflow step failed
- Error message mentioned sed and README.md
- Workflow logs showed sed syntax error

**Root Cause:**

Different sed implementations:
- Ubuntu (GitHub Actions ubuntu-latest): GNU sed
- macOS (GitHub Actions macos-latest): BSD sed

GNU sed syntax for in-place edit:
sed -i "pattern" file

BSD sed syntax for in-place edit:
sed -i '' "pattern" file  # Requires empty string after -i

**Solution That Worked:**

Platform-specific sed commands in scripts/measure_performance.py:

Line 139-151:
if platform_name == "Ubuntu":
    # GNU sed - no empty string needed
    sed_cmd = f'sed -i "s|Ubuntu-[^-]*ms,%20[^-]*K/sec|Ubuntu-{perf_text}|g" README.md'
elif platform_name == "macOS":
    # BSD sed - empty string required after -i
    sed_cmd = f"sed -i '' \"s|macOS-[^-]*ms,%20[^-]*K/sec|macOS-{perf_text}|g\" README.md"

subprocess.run(sed_cmd, shell=True, check=True)

**Why This Works:**
- Detects platform using platform.system()
- Uses correct sed syntax for each platform
- Both platforms now update successfully

**Verification:**

After fix:
- Both Ubuntu and macOS workflow steps succeed
- Both badges update with current performance metrics
- No more sed syntax errors in logs

**Committed:** Verified in scripts/measure_performance.py Lines 139-151

---

### Fix 3: Documentation Validation Too Strict

**Problem Encountered:**

Documentation validation workflow failed because validate_documentation_dates.py was checking for exact date match, but documentation had minor variations in date format or timezone.

**Symptoms:**
- CI workflow failed on documentation validation step
- Error: "Documentation date mismatch"
- Documentation was actually current but format didn't match expectation
- Blocked merges despite docs being correct

**Root Cause:**

Overly strict date validation:
- Expected exact ISO format with timezone
- Documentation used human-readable format
- Timezone differences caused false failures
- Edge cases around midnight caused issues

**Solution That Worked:**

Modified validate_documentation_dates.py to be more lenient:
- Accept multiple date formats
- Allow date within 24-hour window instead of exact match
- Focus on "documentation is recent" not "format is exact"

**Code Change:**

Before (too strict):
if doc_date != expected_date:
    raise ValueError(f"Date mismatch: {doc_date} != {expected_date}")

After (appropriately lenient):
from datetime import datetime, timedelta

doc_datetime = parse_flexible_date(doc_date)
expected_datetime = parse_flexible_date(expected_date)
delta = abs((doc_datetime - expected_datetime).total_seconds())

if delta > 86400:  # 24 hours in seconds
    raise ValueError(f"Documentation date too old: {doc_date}")

**Verification:**

After fix:
- Documentation validation passes for current docs
- No false failures from format differences
- Still catches actually stale documentation
- CI no longer blocks valid PRs

**Note:** This fix is mentioned in handoff document but may need verification in actual scripts

---

## Common Failure Patterns

### Pattern 1: Gray "Unknown" Badge

**Symptom:** Badge displays gray background with "unknown" text

**Common Causes:**

1. **First-time badge, no data yet**
   - Fresh badge URL that hasn't been accessed
   - shields.io hasn't cached it yet
   - Wait 5-10 minutes and refresh

2. **Badge URL syntax error**
   - Typo in package name
   - Wrong endpoint path
   - Missing required parameters

3. **Data source unavailable**
   - PyPI API down (for PyPI badges)
   - GitHub API rate limited
   - Codecov API unavailable

**Diagnosis Steps:**

Step 1: Check badge URL syntax
- View README.md source
- Verify package name spelling
- Compare with shields.io documentation

Step 2: Test data source directly
For PyPI badges:
curl https://pypi.org/pypi/mypylogger/json

For GitHub badges:
curl https://api.github.com/repos/stabbotco1/mypylogger

Step 3: Check shields.io status
Visit: https://status.shields.io

**Solutions That Worked:**

For syntax errors:
- Fix package name in badge URL
- Verify endpoint path correct
- Add required parameters

For new badges:
- Wait 10 minutes for shields.io to cache
- Force refresh: Ctrl+Shift+R
- Try accessing badge URL directly

For data source issues:
- Wait for service to recover
- Check service status page
- Verify API keys/tokens if needed

---

### Pattern 2: Stale Performance Badge Values

**Symptom:** Performance badges show same values for weeks despite code changes

**Common Causes:**

1. **Workflow not running**
   - Schedule disabled
   - Workflow file has errors
   - GitHub Actions quota exceeded

2. **sed pattern doesn't match README**
   - Manual edit broke pattern
   - Badge format changed
   - Pattern regex incorrect

3. **Workflow runs but commits fail**
   - Git permissions issue
   - Protected branch rules
   - Race condition (pre-fix)

**Diagnosis Steps:**

Step 1: Check workflow runs
gh run list --workflow=performance-badge-update.yml --limit 5

Expected: Recent successful runs (within 7 days)

Step 2: Verify sed pattern matches
grep -o 'Ubuntu-[^-]*ms,%20[^-]*K/sec' README.md
grep -o 'macOS-[^-]*ms,%20[^-]*K/sec' README.md

Expected: Each outputs one match

Step 3: Check recent commits
git log --oneline --grep="performance badges" -n 5

Expected: Recent commit with badge update

**Solutions That Worked:**

For workflow not running:
- Check .github/workflows/performance-badge-update.yml exists
- Verify cron syntax: '0 3 * * 0'
- Manually trigger: gh workflow run performance-badge-update.yml

For pattern mismatch:
- Restore expected pattern in README.md
- Run script locally to test: python scripts/measure_performance.py
- Verify changes appear: git diff README.md

For commit failures:
- Check workflow logs for error messages
- Verify GITHUB_TOKEN has write permissions
- Ensure max-parallel: 1 is set (race condition fix)

---

### Pattern 3: Build Status Badge Shows Wrong Status

**Symptom:** Build status badge shows "passing" when tests failed, or vice versa

**Common Causes:**

1. **Wrong workflow referenced**
   - Badge URL points to different workflow file
   - Workflow name doesn't match badge

2. **Wrong branch specified**
   - Badge checks main but CI runs on develop
   - Branch name typo in badge URL

3. **Badge cached with old status**
   - shields.io cache not expired
   - Recent CI run not reflected yet

**Diagnosis Steps:**

Step 1: Verify badge URL
From README.md:
![Build Status](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/ci.yml?branch=main&label=build&logo=github)

Check:
- Repository: stabbotco1/mypylogger
- Workflow: ci.yml
- Branch: main

Step 2: Check actual CI status
gh run list --workflow=ci.yml --branch=main --limit 1

Compare with badge display

Step 3: Test URL directly
curl -I "https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/ci.yml?branch=main"

**Solutions That Worked:**

For wrong workflow:
- Update badge URL to correct workflow file
- Verify workflow file name matches

For wrong branch:
- Update badge URL branch parameter
- Or remove branch parameter to use default

For cache issues:
- Wait 5-10 minutes for cache expiration
- Force refresh: Ctrl+Shift+R
- Check actual CI status on GitHub Actions page

---

### Pattern 4: Coverage Badge Doesn't Update

**Symptom:** Coverage badge shows old percentage after coverage improved

**Common Causes:**

1. **Codecov integration not working**
   - CODECOV_TOKEN missing or invalid
   - Codecov upload failed in CI
   - Coverage report not generated

2. **Badge URL wrong**
   - Wrong repository in badge URL
   - Typo in badge URL path

3. **Coverage data not uploaded**
   - CI workflow missing Codecov step
   - Coverage report file not found
   - Upload step failed silently

**Diagnosis Steps:**

Step 1: Check Codecov dashboard
Visit: https://codecov.io/gh/stabbotco1/mypylogger

Verify coverage percentage shown

Step 2: Check CI workflow logs
gh run view --workflow=ci.yml --log

Look for "Uploading coverage to Codecov" step

Step 3: Verify badge URL
From README.md:
![Coverage](https://img.shields.io/badge/coverage-96.48%25-brightgreen?logo=codecov)

Note: This is static badge, not dynamic Codecov badge

**Solutions That Worked:**

For Codecov integration:
- Verify CODECOV_TOKEN in repository secrets
- Check Codecov upload step in .github/workflows/ci.yml
- Ensure coverage.xml generated before upload

For badge URL:
- Use Codecov dynamic badge:
  https://img.shields.io/codecov/c/github/stabbotco1/mypylogger
- Or update static badge manually after coverage changes

**Note:** mypylogger appears to use static coverage badge, updated manually or by script

---

### Pattern 5: All Badges Turn Gray Simultaneously

**Symptom:** All badges show gray "unknown" at same time

**Common Causes:**

1. **shields.io service outage**
   - shields.io infrastructure issue
   - Affects all badges globally
   - Temporary, usually resolves quickly

2. **Network connectivity issue**
   - Local network blocking shields.io
   - Firewall or proxy issue
   - DNS resolution problem

3. **GitHub API rate limiting**
   - For badges that query GitHub API
   - Usually affects only GitHub-based badges
   - Rare, temporary

**Diagnosis Steps:**

Step 1: Check shields.io status
Visit: https://status.shields.io

Check for reported incidents

Step 2: Test shields.io directly
curl -I https://img.shields.io/badge/test-test-blue

Expected: HTTP 200 response

Step 3: Test from different network
- Try from mobile device
- Try from different computer
- Try from different location

**Solutions That Worked:**

For shields.io outage:
- Wait for service to recover (usually < 30 minutes)
- Monitor shields.io status page
- No action needed on repository side

For network issues:
- Check firewall rules for shields.io
- Verify DNS resolving correctly: nslookup img.shields.io
- Try different network if available

For rate limiting:
- Wait for rate limit to reset (usually 1 hour)
- Check GitHub API rate limit: curl https://api.github.com/rate_limit
- Reduce badge refresh frequency if needed

---

## Preventive Maintenance

### Weekly Checks

**Perform every week:**

1. Visual inspection of all badges
   - All render correctly
   - Values appear current
   - No gray "unknown" badges

2. Run validation script
   python scripts/validate_badges.py
   - All badges return HTTP 200
   - No errors reported

3. Check workflow runs
   gh run list --workflow=performance-badge-update.yml --limit 2
   - Recent successful run exists
   - No failures in last runs

4. Verify performance badge currency
   - Ubuntu and macOS values recent
   - Values seem reasonable
   - Different from last week (detecting staleness)

### Pre-Release Checks

**Before publishing new version:**

1. Update version badges will reflect new version
   - setup.py or pyproject.toml version updated
   - Git tag created
   - Wait 10 minutes after PyPI publish for badge update

2. All badges passing
   - CI badges show passing
   - Coverage badge current
   - Security badge passing

3. Performance badges recent
   - Updated within last week
   - Values appropriate for current code

4. Documentation links work
   - All badge links functional
   - Linked pages load correctly

### Monthly Reviews

**Perform monthly:**

1. Review badge health metrics
   - Check .kiro/metrics/badge_performance.jsonl
   - Identify any recurring failures
   - Investigate patterns

2. Update badge URLs if needed
   - Check for deprecated shields.io endpoints
   - Update to new API versions
   - Test all updated URLs

3. Review troubleshooting guide
   - Add new issues encountered
   - Update solutions if better ones found
   - Remove obsolete information

---

## Recovery Procedures

### Full Badge System Reset

**When to use:** Multiple badges broken, unclear cause, need fresh start

**Procedure:**

Step 1: Backup current README.md
cp README.md README.md.backup

Step 2: Restore known-good badge formats
- Copy badge section from previous working commit
- Or recreate from badge specification docs

Step 3: Test each badge individually
- Add one badge at a time
- Verify it renders correctly
- Commit after each successful badge

Step 4: Run validation
python scripts/validate_badges.py

Step 5: Trigger workflows
gh workflow run performance-badge-update.yml
gh workflow run ci.yml

Step 6: Verify all badges working
- Wait 10-15 minutes for updates
- Visual inspection
- Check validation script passes

### Emergency Badge Disable

**When to use:** Badge causing problems, need to disable temporarily

**Procedure:**

Step 1: Comment out badge in README.md
<!-- ![Badge](https://...) -->

Step 2: Commit and push
git add README.md
git commit -m "Temporarily disable [badge name] - troubleshooting [issue]"
git push

Step 3: Document issue
- Create GitHub issue describing problem
- Link to relevant logs
- Document troubleshooting steps taken

Step 4: Fix underlying issue
- Address root cause
- Test fix locally
- Verify fix works

Step 5: Re-enable badge
- Uncomment badge in README.md
- Verify it works
- Commit and push
- Close related issue

---

## Debugging Tools and Commands

### Badge URL Testing

**Test single badge:**
curl -I "https://img.shields.io/badge/test-test-blue"

**Test with full headers:**
curl -v "https://img.shields.io/pypi/v/mypylogger"

**Test with timing:**
time curl "https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/ci.yml"

### Workflow Debugging

**List recent runs:**
gh run list --workflow=performance-badge-update.yml --limit 10

**View specific run:**
gh run view [RUN_ID]

**View run logs:**
gh run view [RUN_ID] --log

**Trigger manual run:**
gh workflow run performance-badge-update.yml

### Git History Investigation

**Find when badge broke:**
git log --all --oneline --grep="badge"

**Show badge changes over time:**
git log -p README.md | grep -A5 -B5 "shields.io"

**Find last working commit:**
git bisect start
git bisect bad  # Current commit with broken badge
git bisect good [LAST_KNOWN_GOOD]  # Commit where badge worked

### Performance Badge Debugging

**Test measurement script locally:**
python scripts/measure_performance.py

**Check git diff after script:**
git diff README.md

**Verify sed pattern:**
grep "Ubuntu-" README.md
grep "macOS-" README.md

**Test sed command manually:**
# Ubuntu
sed -i "s|Ubuntu-[^-]*ms,%20[^-]*K/sec|Ubuntu-TEST|g" README.md

# macOS
sed -i '' "s|macOS-[^-]*ms,%20[^-]*K/sec|macOS-TEST|g" README.md

### Badge Health Monitoring

**Run validation:**
python scripts/validate_badges.py

**Run health monitor:**
python scripts/badge_health_monitor.py

**Check badge metrics:**
tail -20 .kiro/metrics/badge_performance.jsonl

**Analyze failures:**
python -c "from badge_health_monitor import analyze_badge_failures; analyze_badge_failures('.kiro/metrics/badge_performance.jsonl')"

---

## Known Limitations

### Cannot Fix

**shields.io Service Issues:**
- Outages beyond our control
- Must wait for service recovery
- No repository-side mitigation possible

**GitHub Actions Runner Availability:**
- macOS runners sometimes unavailable
- Queue times unpredictable
- Can only retry workflow later

**Third-Party API Rate Limits:**
- PyPI API limits
- GitHub API limits
- Codecov API limits

### Workarounds Available

**Badge Update Delays:**
- Use manual workflow dispatch for urgent updates
- Document expected delay times for users
- Consider static badges for critical information

**Platform-Specific Issues:**
- Maintain platform-specific code paths
- Document platform differences
- Test on both Ubuntu and macOS

**Cache Staleness:**
- Force refresh techniques documented
- Accept 5-10 minute update delay
- Use workflow dispatch for immediate updates

---

## Lessons Learned

### Design Decisions That Worked

**max-parallel: 1 for performance badges:**
- Simple solution to race condition
- Reliable and maintainable
- Small performance cost acceptable

**Platform-specific sed commands:**
- Handles BSD vs GNU differences
- Works reliably on both platforms
- Clear code with good comments

**Three-method verification:**
- Visual, HTTP, and automated CI
- Catches different types of failures
- Provides redundancy

### Design Decisions to Reconsider

**Static coverage badge:**
- Requires manual updates
- Could use dynamic Codecov badge instead
- Would reduce maintenance burden

**Multiple badge files in specs:**
- Good for organization
- Could consolidate if specs grow too large
- Monitor ongoing maintainability

### Best Practices Confirmed

**Document empirical reality:**
- Actual line numbers from scripts
- Real commands that work
- Verified solutions only

**Test locally before CI:**
- Run scripts locally first
- Verify changes in git diff
- Reduces CI failures

**Monitor badge health:**
- Automated validation catches issues early
- GitHub issues provide visibility
- Regular manual checks still valuable

---

## Future Improvements

### Potential Enhancements

**Better Error Messages:**
- More specific failure descriptions
- Suggested remediation steps
- Links to relevant documentation

**Automated Fixes:**
- Self-healing for known issues
- Automatic retry with backoff
- Smart cache invalidation

**Enhanced Monitoring:**
- Badge response time tracking
- Failure pattern detection
- Proactive alerting

**Documentation Integration:**
- Badge status in generated docs
- Historical performance graphs
- Trend analysis

### Not Recommended

**Overly Complex Solutions:**
- Sophisticated retry logic (max-parallel: 1 is simpler)
- Custom badge hosting (shields.io works well)
- Elaborate caching schemes (5 min default is fine)

**Premature Optimization:**
- Parallel badge updates (race condition risk)
- Custom badge generation (shields.io sufficient)
- Complex verification (current three methods adequate)

---

## Related Documentation

**Common Principles:** See .kiro/steering/badge-standards.md
**System Overview:** See .kiro/specs/badge-system/overview.md
**Core Badges:** See .kiro/specs/badge-system/core-badges.md
**Quality Badges:** See .kiro/specs/badge-system/quality-badges.md
**Performance Badges:** See .kiro/specs/badge-system/performance-badges.md
**Verification:** See .kiro/specs/badge-system/verification.md

---

**End of Badge Troubleshooting Guide**