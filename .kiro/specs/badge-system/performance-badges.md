# Performance Badges Specification

**Status:** Verified Implementation  
**Last Updated:** October 8, 2025  
**Tier:** 3 (Advanced/Project-Specific)  
**Badges Covered:** 2 (Ubuntu Performance, macOS Performance)

---

## Overview

The performance badges provide real-time metrics for mypylogger's logging throughput and latency on different platforms. These badges are the most complex in the system due to platform-specific implementation details, race condition management, and direct README modification requirements.

**Badges:**
1. **Ubuntu Performance** - Latency and throughput on Ubuntu
2. **macOS Performance** - Latency and throughput on macOS

**Key Characteristics:**
- **Update Mechanism:** Workflow-driven with direct file modification
- **Update Frequency:** Weekly schedule + on push to main
- **Data Source:** Custom benchmarking script (scripts/measure_performance.py)
- **Workflow:** .github/workflows/performance-badge-update.yml
- **Critical Constraint:** Race condition prevention via max-parallel: 1

---

## Badge 1: Ubuntu Performance

### Display Format

Badge markdown:
![Ubuntu](https://img.shields.io/badge/Ubuntu-0.84ms,%2017.9K/sec-orange?logo=ubuntu)

**Example Rendered:**
- **Text:** "Ubuntu-0.84ms, 17.9K/sec"
- **Color:** Orange (configurable)
- **Logo:** Ubuntu logo
- **Metrics:**
  - Latency: 0.84ms average per log operation
  - Throughput: 17.9K messages per second

### Purpose

Demonstrates mypylogger's performance characteristics on Ubuntu Linux, the most common CI/CD and server deployment platform.

### Data Source

**Script:** scripts/measure_performance.py (Lines 96-137)

**Measurement Methodology:**

Latency measurement (Line 96-108):
- 100 samples collected
- time.perf_counter() for high-resolution timing
- Each sample measures single logger.info() call
- Convert to milliseconds (* 1000)
- Calculate mean of all samples

Throughput measurement (Line 110-117):
- 15000 messages in continuous loop
- Measure total duration
- Calculate messages per second
- Format as K/sec for readability

**Platform Detection:**

Line 84-92:
- import platform
- system = platform.system()
- if system == "Linux": platform_name = "Ubuntu"
- elif system == "Darwin": platform_name = "macOS"

### Implementation Details

#### Badge URL Pattern

https://img.shields.io/badge/Ubuntu-{PERF_TEXT}-orange?logo=ubuntu

Where PERF_TEXT format: {latency}ms,%20{throughput}K/sec
- %20 is URL-encoded space
- Example: 0.84ms,%2017.9K/sec

#### README Update Mechanism (Critical)

**sed Command (Line 130):**

sed -i "s|Ubuntu-[^-]*ms,%20[^-]*K/sec|Ubuntu-${PERF_TEXT}|g" README.md

**Pattern Explanation:**
- Ubuntu- : Literal match
- [^-]* : Match any characters except hyphen (captures old latency)
- ms,%20 : Literal match including URL-encoded space
- [^-]* : Match any characters except hyphen (captures old throughput)
- K/sec : Literal match

**Why This Pattern:**
- Uses hyphen as delimiter to avoid greedy matching
- Handles variable-width numbers (0.84 vs 10.25)
- Preserves badge URL structure
- No regex lookahead needed

**Platform Specificity:**

Ubuntu uses GNU sed:
sed -i "pattern" file  # No backup file needed

macOS would fail with this syntax (needs empty string for in-place)

### Update Process

#### Workflow Trigger (.github/workflows/performance-badge-update.yml)

Triggers:
- push: branches [main]
- schedule: cron '0 3 * * 0'  # Weekly, Sunday 3 AM UTC
- workflow_dispatch  # Manual trigger

#### Execution Flow

**Step 1: Checkout with Token**
- uses: actions/checkout@v3
- with token: secrets.GITHUB_TOKEN
- fetch-depth: 1

**Step 2: Set up Python**
- uses: actions/setup-python@v4
- python-version: '3.11'

**Step 3: Install Dependencies**
pip install -e .
- Installs mypylogger in editable mode
- Required for performance measurements to reflect actual package behavior

**Step 4: Run Performance Measurement**
run: python scripts/measure_performance.py

**Step 5: Commit Changes (If Any)**
- git config user.email "github-actions[bot]@users.noreply.github.com"
- git config user.name "github-actions[bot]"
- git diff --quiet || git commit -am "Update performance badges [skip ci]"
- git push

**Key Detail:** [skip ci] prevents infinite loop of badge updates triggering more CI runs

### Race Condition Prevention

#### The Problem

When badges are updated in parallel:
1. Job 1 (Ubuntu) checks out main branch
2. Job 2 (macOS) checks out main branch (same commit)
3. Job 1 updates README.md, commits, pushes
4. Job 2 updates README.md, commits, attempts push
5. **Push fails:** Job 2's base commit is now stale
6. **Result:** One badge updates successfully, other fails silently or creates conflict

#### The Solution (Critical Configuration)

**Workflow Matrix Strategy:**

strategy:
  max-parallel: 1  # Forces sequential execution
  matrix:
    os: [ubuntu-latest, macos-latest]

**Why max-parallel: 1:**
- Ensures Ubuntu job completes fully before macOS starts
- First job's commit becomes base for second job
- No possibility of concurrent README modification
- Slight performance cost (~2 min sequential vs ~1 min parallel) is acceptable

**Alternative Approaches Considered:**
1. Git pull before push - Still creates race window
2. Separate workflow files - Harder to maintain, same race issue
3. Rebase on conflict - Added complexity, may still fail
4. max-parallel: 1 - Simple, reliable, maintainable (CHOSEN)

### Verification Methods

#### Method 1: Visual Inspection

**Location:** README.md, Performance section

**Expected Badge:**
![Ubuntu](https://img.shields.io/badge/Ubuntu-0.84ms,%2017.9K/sec-orange?logo=ubuntu)

**Checklist:**
- Badge displays "Ubuntu" label
- Shows latency in milliseconds (0.5-2.0ms typical)
- Shows throughput in K/sec (15-25K typical)
- Orange background color
- Ubuntu logo visible

#### Method 2: HTTP Validation

**Script:** scripts/validate_badges.py

**Test approach:**
- GET request to badge URL
- Verify HTTP 200 response
- Verify Content-Type: image/svg+xml
- Note: Cannot validate dynamic text content from shields.io

**Limitations:**
- Shields.io serves all well-formed URLs as 200 OK
- Cannot programmatically verify displayed text matches README
- Visual inspection still required for accuracy

#### Method 3: Workflow Validation

**GitHub Actions:** .github/workflows/badge-health.yml

**Ubuntu-Specific Check:**

Part of badge_health_monitor.py:
- Verify performance badge updates are recent
- Check last workflow run timestamp
- Alert if days_since(last_run) > 10 (weekly + buffer)
- Report issue if stale

### Acceptance Criteria

**Automated Checks:**
- Workflow runs successfully on schedule (weekly)
- README.md updated with new performance text
- Commit message includes "Update performance badges [skip ci]"
- No conflicts during push (race condition absent)
- Badge renders correctly on shields.io

**Performance Thresholds (Sanity Checks):**
- Latency: 0.1ms < value < 10ms
- Throughput: 5K/sec < value < 100K/sec
- Values change over time (not static)

**Note:** Exact performance values vary with GitHub runner load and Python version. Thresholds detect measurement failures, not performance regressions.

### Known Issues

#### Issue 1: First Run May Show "Unknown"

**Symptom:** After initial workflow setup, badge shows "Unknown" text

**Cause:** README.md didn't contain the expected pattern for sed to match

**Fix:** Manual first update:
- Run locally: python scripts/measure_performance.py
- Commit: git commit -am "Initialize performance badges"
- Push: git push

**Prevention:** Ensure README.md contains initial badge with correct pattern before enabling workflow

#### Issue 2: Extreme Performance Values

**Symptom:** Throughput shows 100K/sec or latency shows 0.01ms (unrealistically fast)

**Cause:** GitHub Actions runner under very light load, or measurement loop optimized away by JIT

**Impact:** Low - indicates fast performance, not inaccurate

**Fix:** None needed, values will normalize over multiple runs

#### Issue 3: sed Pattern Mismatch After Manual Edit

**Symptom:** Workflow runs but badge not updated

**Cause:** Someone manually edited badge text in README.md, breaking sed pattern

**Diagnosis:**
Check if pattern matches:
grep -o 'Ubuntu-[^-]*ms,%20[^-]*K/sec' README.md

Should output: Ubuntu-0.84ms,%2017.9K/sec
If no output, pattern is broken

**Fix:**
Restore expected pattern format manually
Ensure: Ubuntu-{num}ms,%20{num}K/sec

---

## Badge 2: macOS Performance

### Display Format

Badge markdown:
![macOS](https://img.shields.io/badge/macOS-0.79ms,%2019.0K/sec-orange?logo=apple)

**Example Rendered:**
- **Text:** "macOS-0.79ms, 19.0K/sec"
- **Color:** Orange (matches Ubuntu for consistency)
- **Logo:** Apple logo
- **Metrics:**
  - Latency: 0.79ms average per log operation
  - Throughput: 19.0K messages per second

### Purpose

Demonstrates mypylogger's performance characteristics on macOS, important for developers using Mac laptops for local development and testing.

### Data Source

**Script:** scripts/measure_performance.py (Lines 96-151)

**Methodology:** Identical to Ubuntu (see Badge 1), but executed on macOS runner

**Platform Detection:**

Line 86-88:
elif system == "Darwin":
    platform_name = "macOS"

### Implementation Details

#### Badge URL Pattern

https://img.shields.io/badge/macOS-{PERF_TEXT}-orange?logo=apple

Where PERF_TEXT format: {latency}ms,%20{throughput}K/sec

#### README Update Mechanism (Platform-Specific)

**sed Command (Line 147):**

sed -i '' "s|macOS-[^-]*ms,%20[^-]*K/sec|macOS-${PERF_TEXT}|g" README.md

**Critical Difference from Ubuntu:**

macOS (BSD sed):
sed -i '' "pattern" file  # Empty string required after -i

Ubuntu (GNU sed):
sed -i "pattern" file     # No empty string needed

**Why the Difference:**
- **BSD sed** (macOS): -i flag requires backup file extension
  - -i '' means "no backup file"
  - -i '.bak' would create README.md.bak
- **GNU sed** (Ubuntu): -i alone means in-place, no backup
  - -i implicitly means no backup
  - -i.bak would create backup

**Script Implementation (Lines 139-151):**

if platform_name == "Ubuntu":
    # GNU sed syntax
    sed_cmd = f'sed -i "s|Ubuntu-[^-]*ms,%20[^-]*K/sec|Ubuntu-{perf_text}|g" README.md'
elif platform_name == "macOS":
    # BSD sed syntax - note the empty string after -i
    sed_cmd = f"sed -i '' \"s|macOS-[^-]*ms,%20[^-]*K/sec|macOS-{perf_text}|g\" README.md"

subprocess.run(sed_cmd, shell=True, check=True)

**Why Shell=True Here:**
- String substitution is already complete (f-string)
- sed command contains no user input
- Simpler than constructing list with quotes

### Update Process

**Workflow Configuration:** Same as Ubuntu, but runs second due to max-parallel: 1

**Execution Order:**
1. Ubuntu job completes entirely (checkout → measure → commit → push)
2. macOS job starts (checks out commit with Ubuntu's update)
3. macOS measures, updates README.md
4. macOS commits and pushes (now includes both badge updates)

**Why This Works:**
- macOS job sees Ubuntu's changes
- Single final commit contains both platform updates
- No race condition possible

### Race Condition Prevention

**Configuration:** Same max-parallel: 1 strategy as Ubuntu

**Sequential Flow:**

Time 0:00 - Ubuntu job starts
Time 0:30 - Ubuntu measures performance
Time 0:31 - Ubuntu updates README.md
Time 0:32 - Ubuntu commits and pushes
Time 0:33 - Ubuntu job ends
Time 0:33 - macOS job starts (sees Ubuntu's commit)
Time 1:03 - macOS measures performance
Time 1:04 - macOS updates README.md (now has both updates)
Time 1:05 - macOS commits and pushes
Time 1:06 - macOS job ends

**Final README.md state:** Both badges updated in single workflow run

### Verification Methods

#### Method 1: Visual Inspection

**Location:** README.md, Performance section

**Expected Badge:**
![macOS](https://img.shields.io/badge/macOS-0.79ms,%2019.0K/sec-orange?logo=apple)

**Checklist:**
- Badge displays "macOS" label
- Shows latency in milliseconds (0.5-2.0ms typical)
- Shows throughput in K/sec (15-25K typical)
- Orange background color
- Apple logo visible

#### Method 2: HTTP Validation

**Script:** scripts/validate_badges.py

**Test approach:**
- GET request to badge URL
- Verify HTTP 200 response
- Verify Content-Type: image/svg+xml

**Limitations:** Same as Ubuntu badge - cannot validate dynamic text

#### Method 3: Workflow Validation

**Check:** Same badge_health_monitor.py workflow freshness check (applies to both platforms)

### Acceptance Criteria

**Automated Checks:**
- Workflow runs successfully after Ubuntu job
- README.md updated with new macOS performance text
- Both Ubuntu and macOS badges updated in same commit
- No push conflicts (sequential execution working)
- Badge renders correctly with Apple logo

**Performance Thresholds:**
- Latency: 0.1ms < value < 10ms
- Throughput: 5K/sec < value < 100K/sec
- macOS performance similar to Ubuntu (within 2x)

**Relative Performance:**
- macOS often slightly faster than Ubuntu (better I/O on GitHub runners)
- Differences under 50% are normal and not concerning
- Large differences (>3x) indicate measurement issue

### Known Issues

#### Issue 1: BSD sed Syntax Errors

**Symptom:** Workflow fails on macOS with "sed: 1: 'README.md': extra characters at the end of h command"

**Cause:** Forgot empty string after -i flag

**Fix:** Ensure script uses sed -i '' "pattern" on macOS, not sed -i "pattern"

**Verification:**
Check measure_performance.py Line 147:
grep "sed -i ''" scripts/measure_performance.py
Should see: sed -i '' "s|macOS-...

#### Issue 2: macOS Runner Unavailability

**Symptom:** Workflow queued for extended time (>30 min) or fails with "No macOS runners available"

**Cause:** GitHub Actions has limited macOS runner capacity, especially for free tier

**Impact:** Badge updates delayed but not lost

**Mitigation:**
- Weekly schedule reduces runner demand
- Manual workflow_dispatch can retry if urgent
- Ubuntu badge still updates successfully (independent)

#### Issue 3: Unicode in Performance Output

**Symptom:** Badge shows garbled characters or sed fails

**Cause:** Non-ASCII characters in performance measurement output (rare)

**Prevention:**
measure_performance.py uses ASCII-safe formatting:
perf_text = f"{avg_latency:.2f}ms,%20{throughput_k:.1f}K/sec"
Only uses: digits, period, 'ms', 'K', 'sec', comma

**If Occurs:** Check for locale issues in GitHub Actions runner

---

## Workflow Configuration Details

### Complete Workflow File

**Location:** .github/workflows/performance-badge-update.yml

**Full Configuration:**

name: Update Performance Badges

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 3 * * 0'  # 3 AM UTC every Sunday
  workflow_dispatch:

jobs:
  update-badges:
    runs-on: ${{ matrix.os }}
    strategy:
      max-parallel: 1  # CRITICAL: Prevents race conditions
      matrix:
        os: [ubuntu-latest, macos-latest]
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 1
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Measure performance
        run: python scripts/measure_performance.py
      
      - name: Commit badge updates
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git diff --quiet || git commit -am "Update performance badges [skip ci]"
          git push

### Workflow Triggers

#### Push to Main

**Use Case:** Update badges whenever code changes that might affect performance

**Behavior:**
- Runs on every push/merge to main branch
- Provides immediate feedback on performance impact of changes

#### Weekly Schedule

**Use Case:** Keep badges fresh even without code changes

**Behavior:**
- Runs every Sunday at 3 AM UTC
- Detects environment-related performance changes
- Prevents "stale badge" appearance

#### Manual Dispatch

**Use Case:** On-demand updates for testing or debugging

**Behavior:**
- Accessible from GitHub Actions UI
- Useful for:
  - Testing workflow changes
  - Recovering from failures
  - Updating after manual README edits

### Environment Considerations

#### GitHub Runner Specifications

**Ubuntu:**
- 2-core CPU
- 7 GB RAM
- SSD storage

**macOS:**
- 3-core CPU
- 14 GB RAM
- SSD storage

**Impact on Performance:**
- macOS has more resources but performance often similar
- Runner load varies, causing ±30% variation in measurements
- Measurements reflect "GitHub Actions CI environment" performance, not user machines

#### Python Version Consistency

python-version: '3.11'

**Why Fixed Version:**
- Performance can vary between Python versions
- Consistency allows trend analysis over time
- Should match minimum supported version or current stable

**Alternative Approach:**

Could use matrix to measure all supported versions:
matrix:
  os: [ubuntu-latest, macos-latest]
  python-version: ['3.9', '3.10', '3.11', '3.12']

But this would require 8 badges or aggregated metrics - more complexity than value

---

## Performance Measurement Details

### Script Architecture

**File:** scripts/measure_performance.py

**Structure:**
1. Setup (Lines 1-30): Imports, configuration
2. Logger initialization (Lines 32-82): Create test logger with realistic config
3. Platform detection (Lines 84-92): Identify OS for badge naming
4. Latency measurement (Lines 96-108): 100 sample average
5. Throughput measurement (Lines 110-117): 15000 message test
6. Formatting (Lines 119-125): Convert to badge text format
7. README update (Lines 127-151): Platform-specific sed commands

### Measurement Methodology Philosophy

**Latency Measurement:**
- **100 samples:** Balance between statistical validity and runtime
- **perf_counter():** Highest resolution timer available
- **Mean (not median):** Matches user's average experience
- **Single message per sample:** Isolates per-message overhead

**Throughput Measurement:**
- **15000 messages:** Large enough to amortize startup costs
- **Continuous loop:** Realistic logging burst scenario
- **No delays:** Maximum throughput measurement
- **K/sec formatting:** More readable than messages/sec for large numbers

### Realistic Configuration

Logger setup (Lines 35-78, simplified):
- logging.getLogger("performance_test")
- setLevel(logging.INFO)
- RotatingFileHandler with maxBytes=10MB, backupCount=5
- Formatter with timestamp and context
- File I/O included (not just in-memory)

**Why This Matters:**
- Measurements reflect real-world use patterns
- File I/O included (not just in-memory)
- Formatting overhead included
- Log rotation logic included

### Temperature/Warmup Considerations

**Cold Start:**

Lines 94-95:
Warmup - first few logs may be slower
for _ in range(10):
    logger.info("Warmup message")

**Why Warmup:**
- JIT compilation (if PyPy)
- OS file system caching
- Python module initialization
- Prevents outlier skewing average

---

## Troubleshooting Performance Badges

### Diagnosis Checklist

When performance badges aren't updating or showing incorrect values:

**Step 1: Check Workflow Status**

gh run list --workflow=performance-badge-update.yml --limit 5

**Expected:** Recent successful run (within 7 days)
**If Failed:** Check logs for specific error

**Step 2: Verify README Pattern**

Check Ubuntu badge pattern:
grep -o 'Ubuntu-[^-]*ms,%20[^-]*K/sec' README.md

Check macOS badge pattern:
grep -o 'macOS-[^-]*ms,%20[^-]*K/sec' README.md

**Expected:** Each grep outputs one match
**If No Match:** Pattern broken, manual fix needed

**Step 3: Test Measurement Script Locally**

python scripts/measure_performance.py
git diff README.md

**Expected:** README.md shows changed performance values
**If No Changes:** Script error or sed pattern mismatch

**Step 4: Check Recent Commits**

git log --oneline --grep="performance badges" -n 5

**Expected:** Recent commit (within 7 days) with performance badge update
**If Absent:** Workflow not running or failing silently

### Common Failure Patterns

#### Pattern 1: Both Badges Stop Updating

**Symptoms:**
- No recent "Update performance badges" commits
- Workflow shows no recent runs

**Likely Causes:**
1. Weekly schedule disabled or cron syntax error
2. Workflow file deleted/moved
3. GitHub Actions disabled for repository

**Diagnosis:**

Check if workflow file exists:
ls -la .github/workflows/performance-badge-update.yml

Check cron syntax:
grep "cron:" .github/workflows/performance-badge-update.yml

**Fix:**
- Restore workflow file if missing
- Verify cron syntax: '0 3 * * 0'
- Check Settings → Actions → Allow all actions

#### Pattern 2: Only One Badge Updates

**Symptoms:**
- Ubuntu badge updates, macOS doesn't (or vice versa)
- Workflow runs but one platform fails

**Likely Causes:**
1. Platform-specific sed syntax error
2. Runner unavailable for one platform
3. Race condition (max-parallel not set to 1)

**Diagnosis:**

Check workflow logs for specific platform failure:
gh run view --log --workflow=performance-badge-update.yml

Verify max-parallel setting:
grep "max-parallel" .github/workflows/performance-badge-update.yml

**Fix:**
- Verify sed syntax matches platform ('' for macOS, none for Ubuntu)
- Check max-parallel: 1 is set
- Retry workflow manually if runner was unavailable

#### Pattern 3: Badges Show Stale Values

**Symptoms:**
- Values don't change over multiple weeks
- Same numbers despite code changes

**Likely Causes:**
1. Workflow runs but sed pattern doesn't match
2. [skip ci] preventing updates on push
3. Badge cached by browser/CDN

**Diagnosis:**

Check if pattern matches current README:
grep "Ubuntu-" README.md
grep "macOS-" README.md

Check if sed pattern in script matches README format:
grep "sed -i" scripts/measure_performance.py

**Fix:**
- Manually update README to match expected pattern
- Force refresh: Ctrl+Shift+R (bypass cache)
- Run workflow manually to test

#### Pattern 4: sed Command Fails in Workflow

**Symptoms:**
- Workflow fails at "Measure performance" step
- Error message contains "sed: "

**Likely Causes:**
1. BSD vs GNU sed syntax mismatch
2. Special characters in performance output
3. README pattern changed manually

**Diagnosis:**

View sed command that failed:
gh run view --log

Test sed locally on same platform:
Ubuntu: sed -i "s|Ubuntu-[^-]*ms,%20[^-]*K/sec|Ubuntu-TEST|g" README.md
macOS: sed -i '' "s|macOS-[^-]*ms,%20[^-]*K/sec|macOS-TEST|g" README.md

**Fix:**
- Verify correct sed syntax for platform in measure_performance.py
- Check for typos in sed pattern (common: forgetting %20, wrong delimiters)
- Ensure README has expected pattern format

### Recovery Procedures

#### Full Badge Reset

If badges are completely broken:

**Step 1: Restore Known-Good Pattern**

In README.md, replace with:
![Ubuntu](https://img.shields.io/badge/Ubuntu-0.00ms,%200.0K/sec-orange?logo=ubuntu)
![macOS](https://img.shields.io/badge/macOS-0.00ms,%200.0K/sec-orange?logo=apple)

**Step 2: Test Script Locally**

python scripts/measure_performance.py
# Should update README.md with real values

**Step 3: Commit and Push**

git add README.md
git commit -m "Reset performance badge format"
git push

**Step 4: Trigger Workflow**

gh workflow run performance-badge-update.yml

**Step 5: Verify Update**

Wait 2-3 minutes, then:
git pull
grep "Ubuntu-" README.md
grep "macOS-" README.md

#### Emergency Manual Update

If automated updates failing and need current values:

**Step 1: Run Locally**

python scripts/measure_performance.py

**Step 2: Commit Manual Update**

git add README.md
git commit -m "Manual performance badge update [skip ci]"
git push

**Step 3: Debug Workflow Later**

Badges now current while you fix automation

---

## Future Enhancements

### Potential Improvements

#### 1. Historical Performance Tracking

**Idea:** Track performance over time in separate file or database

**Benefits:**
- Detect performance regressions
- Visualize trends
- Correlate with code changes

**Implementation:**

Append to .kiro/metrics/performance_history.json:
{
  "timestamp": "2025-10-08T03:00:00Z",
  "platform": "ubuntu",
  "latency_ms": 0.84,
  "throughput_k": 17.9,
  "python_version": "3.11",
  "commit_sha": "abc123..."
}

#### 2. Performance Regression Alerts

**Idea:** Fail workflow if performance degrades significantly

**Benefits:**
- Catch performance bugs in CI
- Prevent merging slow code
- Quantitative performance SLOs

**Implementation:**

In measure_performance.py:
THRESHOLD_LATENCY_MS = 5.0  # Fail if > 5ms
THRESHOLD_THROUGHPUT_K = 5.0  # Fail if < 5K/sec

if avg_latency > THRESHOLD_LATENCY_MS:
    raise Exception(f"Performance regression: latency {avg_latency}ms exceeds {THRESHOLD_LATENCY_MS}ms")

#### 3. Multiple Python Version Badges

**Idea:** Show performance for Python 3.9, 3.10, 3.11, 3.12

**Benefits:**
- Identify version-specific performance issues
- Help users choose optimal Python version
- Document performance characteristics across versions

**Challenges:**
- 8 total badges (4 versions × 2 platforms)
- More README clutter
- Longer workflow runtime

**Alternative:** Single badge with "best" or "average" performance

#### 4. Performance Trend Graph

**Idea:** Generate SVG graph showing performance over last 30 days

**Benefits:**
- Visual performance trends
- Easier to spot regressions
- More engaging than static numbers

**Implementation:**
- Store measurements in git (performance_history.json)
- Generate SVG using matplotlib or plotly
- Commit SVG to repository
- Embed in README

**Challenges:**
- Repository size growth
- Requires charting library
- More complex workflow

---

## Related Documentation

**Common Principles:** See .kiro/steering/badge-standards.md
**System Overview:** See .kiro/specs/badge-system/overview.md
**Core Badges:** See .kiro/specs/badge-system/core-badges.md
**Quality Badges:** See .kiro/specs/badge-system/quality-badges.md
**Verification:** See .kiro/specs/badge-system/verification.md
**Troubleshooting:** See .kiro/specs/badge-system/troubleshooting.md

---

**End of Performance Badges Specification**