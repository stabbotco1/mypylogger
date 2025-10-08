# Quality Badges Specification

**Status:** Verified Implementation  
**Last Updated:** October 8, 2025  
**Tier:** 2 (Quality Metrics)  
**Badges Covered:** 3 (PyPI Version, Python Versions, Documentation)

---

## Overview

Quality badges provide information about package availability, compatibility, and documentation status. These are Tier 2 badges that focus on package quality and usability rather than build/test status (Tier 1) or performance metrics (Tier 3).

**Badges:**
1. **PyPI Version** - Current published version on PyPI
2. **Python Versions** - Supported Python versions
3. **Documentation** - Documentation status/availability

**Key Characteristics:**
- **Update Mechanism:** Primarily API-driven (shields.io queries external sources)
- **Update Frequency:** Real-time on page load (no workflow needed)
- **Data Source:** PyPI API, package metadata
- **Manual Updates:** Only for documentation badge (if implemented)

---

## Badge 1: PyPI Version

### Display Format

Badge markdown:
![PyPI Version](https://img.shields.io/pypi/v/mypylogger)

**Example Rendered:**
- **Text:** "pypi v1.2.3" (example version)
- **Color:** Blue (default for shields.io)
- **Logo:** None (optional: ?logo=pypi)

### Purpose

Shows the latest published version of mypylogger on PyPI, allowing users to quickly determine if they have the current release.

### Data Source

**API:** shields.io queries PyPI JSON API

**Query Flow:**
1. User loads README.md in browser
2. Browser requests badge from shields.io
3. shields.io queries https://pypi.org/pypi/mypylogger/json
4. shields.io extracts version from info.version field
5. shields.io generates and returns SVG badge

**PyPI API Response (simplified):**

{
  "info": {
    "version": "1.2.3",
    "name": "mypylogger",
    ...
  }
}

### Implementation Details

#### Badge URL Pattern

https://img.shields.io/pypi/v/mypylogger

**URL Components:**
- img.shields.io - Badge service
- /pypi/v/ - PyPI version endpoint
- mypylogger - Package name (must match PyPI exactly)

**Optional Parameters:**
- ?logo=pypi - Add PyPI logo
- ?color=blue - Override color
- ?label=version - Custom label text

#### Update Mechanism

**Automatic - No Workflow Required**

**Update Trigger:**
- User publishes new version to PyPI
- PyPI updates package metadata immediately
- Next README.md page load reflects new version (shields.io caches for ~5 minutes)

**No Repository Action Needed:**
- Badge updates automatically when PyPI metadata changes
- No commit, push, or workflow execution required
- Version comes directly from PyPI, not from repository

### Cache Behavior

**shields.io Caching:**
- Default cache: 300 seconds (5 minutes)
- After publishing to PyPI, badge may show old version for up to 5 minutes
- Force refresh: Add random query parameter (?v=timestamp)

**Browser Caching:**
- SVG images may be cached by browser
- Force refresh: Ctrl+Shift+R (hard reload)

### Verification Methods

#### Method 1: Visual Inspection

**Location:** README.md, top badge section

**Expected Badge:**
Badge displays current PyPI version

**Checklist:**
- Badge displays "pypi" or custom label
- Version number matches latest PyPI release
- Badge not showing "invalid" or "unknown"
- Clickable (should link to PyPI if configured)

**Manual Verification:**
Visit https://pypi.org/project/mypylogger/
Compare version shown on PyPI page with badge

#### Method 2: HTTP Validation

**Script:** scripts/validate_badges.py

**Test approach:**
- GET request to badge URL
- Verify HTTP 200 response
- Verify Content-Type: image/svg+xml
- Cannot validate actual version text (dynamic SVG)

**Validation Code:**

response = requests.get('https://img.shields.io/pypi/v/mypylogger', timeout=5)
assert response.status_code == 200
assert 'image/svg+xml' in response.headers['Content-Type']

#### Method 3: API Cross-Check

**Verification Script:**

import requests

# Get version from PyPI directly
pypi_response = requests.get('https://pypi.org/pypi/mypylogger/json')
pypi_version = pypi_response.json()['info']['version']

# Get badge SVG (contains version text)
badge_response = requests.get('https://img.shields.io/pypi/v/mypylogger')
badge_svg = badge_response.text

# Check if version appears in SVG
assert pypi_version in badge_svg, f"Badge version mismatch: expected {pypi_version}"

### Acceptance Criteria

**Automated Checks:**
- Badge URL returns HTTP 200
- Badge renders as valid SVG
- No "invalid" or "error" text in badge

**Manual Checks:**
- Version matches current PyPI release
- Badge updates within 10 minutes of new PyPI publish
- Badge accessible without authentication

**Version Format:**
- Follows semantic versioning (MAJOR.MINOR.PATCH)
- Matches version in setup.py or pyproject.toml
- Matches git tag for release

### Known Issues

#### Issue 1: Badge Shows "invalid"

**Symptom:** Badge displays red "invalid" text instead of version

**Likely Causes:**
1. Package name misspelled in badge URL
2. Package not published to PyPI
3. PyPI API temporarily unavailable
4. Package deleted/removed from PyPI

**Diagnosis:**

Check package exists on PyPI:
curl https://pypi.org/pypi/mypylogger/json

Expected: JSON response with package info
If 404: Package not on PyPI or name incorrect

**Fix:**
- Verify package name spelling in README.md badge URL
- Ensure package published: python -m build && twine upload dist/*
- Wait 5 minutes for shields.io cache to clear

#### Issue 2: Badge Shows Old Version

**Symptom:** Badge displays previous version after publishing new release

**Cause:** shields.io caching (5 minute default)

**Impact:** Low - badge will update automatically within 5 minutes

**Fix (if urgent):**
- Wait 5-10 minutes for cache expiration
- Hard refresh browser: Ctrl+Shift+R
- Clear shields.io cache by appending random query: ?v=12345

#### Issue 3: Version Mismatch Between Badge and Repository

**Symptom:** Badge shows version X but repository code is version Y

**Cause:** Version published to PyPI doesn't match current repository state

**Common Scenarios:**
- Forgot to bump version before publish
- Published from wrong branch
- Local changes not committed before publish

**Fix:**
- Verify version consistency:
  - setup.py or pyproject.toml
  - Git tag
  - PyPI published version
- Publish corrected version if needed

---

## Badge 2: Python Versions

### Display Format

Badge markdown:
![Python Versions](https://img.shields.io/pypi/pyversions/mypylogger)

**Example Rendered:**
- **Text:** "python 3.9 | 3.10 | 3.11 | 3.12"
- **Color:** Blue (default)
- **Logo:** None (optional: ?logo=python)

### Purpose

Displays which Python versions are officially supported by mypylogger, helping users determine compatibility with their environment.

### Data Source

**API:** shields.io queries PyPI metadata

**Query Flow:**
1. Browser requests badge from shields.io
2. shields.io queries https://pypi.org/pypi/mypylogger/json
3. shields.io extracts classifiers from metadata
4. shields.io filters for "Programming Language :: Python :: X.Y"
5. shields.io generates badge showing all supported versions

**PyPI Metadata (classifiers):**

{
  "info": {
    "classifiers": [
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12"
    ]
  }
}

### Implementation Details

#### Badge URL Pattern

https://img.shields.io/pypi/pyversions/mypylogger

**URL Components:**
- img.shields.io - Badge service
- /pypi/pyversions/ - PyPI Python versions endpoint
- mypylogger - Package name

**Optional Parameters:**
- ?logo=python - Add Python logo
- ?color=blue - Override color

#### Source of Truth

**setup.py or pyproject.toml:**

In setup.py:
classifiers=[
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

In pyproject.toml:
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

#### Update Mechanism

**Automatic - No Workflow Required**

**Update Trigger:**
1. Developer updates classifiers in setup.py/pyproject.toml
2. Builds and publishes new version to PyPI
3. PyPI updates package metadata
4. shields.io reflects new versions on next badge request (5 min cache)

**No Repository Action Needed:**
- Badge updates automatically when PyPI metadata changes
- Version list comes from PyPI classifiers, not repository

### Verification Methods

#### Method 1: Visual Inspection

**Location:** README.md, top badge section

**Expected Badge:**
Badge displays supported Python versions (currently 3.9, 3.10, 3.11, 3.12)

**Checklist:**
- Badge shows "python" or "py" label
- Lists all supported versions
- Versions match setup.py/pyproject.toml classifiers
- Badge not showing "invalid"

**Manual Verification:**
1. Check setup.py or pyproject.toml classifiers
2. Verify badge matches declared support
3. Cross-reference with actual CI test matrix

#### Method 2: HTTP Validation

**Script:** scripts/validate_badges.py

**Test approach:**
- GET request to badge URL
- Verify HTTP 200 response
- Verify Content-Type: image/svg+xml

**Validation Code:**

response = requests.get('https://img.shields.io/pypi/pyversions/mypylogger', timeout=5)
assert response.status_code == 200
assert 'image/svg+xml' in response.headers['Content-Type']

#### Method 3: Metadata Cross-Check

**Verification Script:**

import requests

# Get classifiers from PyPI
pypi_response = requests.get('https://pypi.org/pypi/mypylogger/json')
classifiers = pypi_response.json()['info']['classifiers']

# Extract Python version classifiers
python_versions = [
    c.split(' :: ')[-1] 
    for c in classifiers 
    if c.startswith('Programming Language :: Python :: 3.')
]

# Should include: ['3.9', '3.10', '3.11', '3.12']
print(f"Supported Python versions: {python_versions}")

### Acceptance Criteria

**Automated Checks:**
- Badge URL returns HTTP 200
- Badge renders as valid SVG
- No "invalid" or "unknown" text

**Manual Checks:**
- Versions match setup.py/pyproject.toml classifiers
- Versions match CI test matrix (.github/workflows/ci.yml)
- All versions actually tested in CI
- Minimum version matches documentation

**Consistency Check:**
- setup.py/pyproject.toml classifiers
- CI workflow matrix
- README.md badge
- Documentation (if separate file)

### Known Issues

#### Issue 1: Badge Shows "invalid"

**Symptom:** Badge displays "invalid" instead of Python versions

**Likely Causes:**
1. Package name misspelled
2. No Python version classifiers in metadata
3. Package not on PyPI

**Diagnosis:**

Check PyPI metadata:
curl https://pypi.org/pypi/mypylogger/json | grep "Programming Language :: Python"

Expected: Multiple "Programming Language :: Python :: 3.X" classifiers

**Fix:**
- Add classifiers to setup.py/pyproject.toml
- Publish updated package to PyPI
- Wait 5-10 minutes for cache

#### Issue 2: Badge Shows Generic "3+" Instead of Specific Versions

**Symptom:** Badge shows "python 3+" instead of listing 3.9, 3.10, etc.

**Cause:** Only generic "Programming Language :: Python :: 3" classifier present

**Fix:**
Add specific version classifiers:
classifiers=[
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",  # Add these
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

#### Issue 3: Versions Mismatch with CI Matrix

**Symptom:** Badge shows versions not actually tested in CI

**Cause:** Classifiers don't match CI workflow matrix

**Diagnosis:**

Check CI matrix:
grep "python-version:" .github/workflows/ci.yml

Compare with classifiers in setup.py/pyproject.toml

**Fix:**
- Update classifiers to match CI matrix
- Or update CI matrix to test all claimed versions
- Publish corrected package

**Best Practice:** CI matrix should test all versions in classifiers

---

## Badge 3: Documentation

### Display Format

Badge markdown (if implemented):
![Documentation](https://img.shields.io/badge/docs-available-brightgreen)

**Example Rendered:**
- **Text:** "docs available" or "docs passing"
- **Color:** Green (if docs exist/build successfully)
- **Logo:** Optional: ?logo=readthedocs

### Purpose

Indicates whether project documentation exists and is accessible, helping users find detailed usage information.

### Implementation Status

**Status:** To be verified from uploaded files

**Possible Implementations:**
1. **Static Badge** - Manually updated in README.md
2. **Read the Docs** - Automated if docs hosted on readthedocs.org
3. **GitHub Pages** - Custom workflow if docs deployed to GitHub Pages
4. **No Badge** - Documentation linked directly without badge

### Data Source (If Implemented)

**Option 1: Read the Docs Integration**

Badge URL:
https://readthedocs.org/projects/mypylogger/badge/?version=latest

**Update Mechanism:**
- Automatic when docs build on Read the Docs
- Green if build succeeds
- Red if build fails

**Option 2: Static Badge**

Badge URL:
https://img.shields.io/badge/docs-available-brightgreen

**Update Mechanism:**
- Manual update in README.md
- No automated verification

**Option 3: Custom Workflow**

Badge URL:
https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/docs.yml?label=docs

**Update Mechanism:**
- Workflow-driven
- Updates when docs workflow runs
- Shows build status

### Verification Methods (If Badge Exists)

#### Method 1: Visual Inspection

**Location:** README.md, badge section

**Expected Badge:**
Badge shows documentation status (available, passing, etc.)

**Checklist:**
- Badge displays appropriate status
- Badge links to documentation (if clickable)
- Color indicates success (green) or failure (red)

#### Method 2: Documentation Accessibility

**Test:**
1. Click badge (if linked)
2. Verify documentation loads
3. Check documentation is current (matches latest version)

**Expected:**
- Documentation accessible without authentication
- Content matches current package version
- Navigation functional

#### Method 3: HTTP Validation

**Script:** scripts/validate_badges.py

**Test approach:**
- GET request to badge URL
- Verify HTTP 200 response
- If badge links to docs, verify docs URL also returns 200

### Known Issues (If Badge Exists)

#### Issue 1: Badge Shows "failing" Despite Valid Docs

**Symptom:** Documentation badge shows red "failing" status

**Likely Causes:**
1. Read the Docs build failed
2. Documentation workflow failed
3. Badge URL pointing to wrong project

**Diagnosis:**

If Read the Docs:
Visit https://readthedocs.org/projects/mypylogger/builds/
Check recent build status

If GitHub workflow:
gh run list --workflow=docs.yml
Check recent run status

**Fix:**
- Check Read the Docs build logs for errors
- Fix documentation build issues (missing dependencies, syntax errors)
- Rebuild documentation

#### Issue 2: Badge Not Updating After Docs Fix

**Symptom:** Fixed documentation but badge still shows old status

**Cause:** Badge caching

**Fix:**
- Wait 5-10 minutes for cache expiration
- Force rebuild on Read the Docs
- Hard refresh browser

---

## Cross-Badge Consistency

### Version Alignment

**Critical Consistency Check:**

All version indicators should align:
1. PyPI Version badge
2. Git tags
3. setup.py/pyproject.toml version
4. Documentation version (if shown)
5. CHANGELOG.md latest entry

**Verification Command:**

# Check PyPI version
curl -s https://pypi.org/pypi/mypylogger/json | jq -r '.info.version'

# Check latest git tag
git describe --tags --abbrev=0

# Check setup.py version
grep "version=" setup.py

# Check pyproject.toml version
grep "version =" pyproject.toml

All should return same version number.

### Python Version Alignment

**Critical Consistency Check:**

Python versions should align across:
1. Python Versions badge (from PyPI classifiers)
2. CI test matrix (.github/workflows/ci.yml)
3. setup.py/pyproject.toml python_requires
4. Documentation (if it mentions version support)

**Verification:**

# Check classifiers
curl -s https://pypi.org/pypi/mypylogger/json | jq -r '.info.classifiers[]' | grep "Python :: 3"

# Check CI matrix
grep "python-version:" .github/workflows/ci.yml

# Check python_requires
grep "python_requires" setup.py

Should all reference same Python versions.

---

## Maintenance Procedures

### After Publishing New Version

**Checklist:**
1. Wait 5-10 minutes for PyPI to update
2. Verify PyPI Version badge shows new version
3. Force refresh if needed (Ctrl+Shift+R)
4. Check version consistency across all indicators

**If Badge Not Updating:**
- Verify package successfully uploaded to PyPI
- Check package name spelling in badge URL
- Wait additional 5 minutes for shields.io cache
- Check PyPI directly: https://pypi.org/project/mypylogger/

### When Adding/Dropping Python Version Support

**Checklist:**
1. Update classifiers in setup.py/pyproject.toml
2. Update CI matrix in .github/workflows/ci.yml
3. Update documentation (if mentions supported versions)
4. Publish new version to PyPI
5. Verify Python Versions badge updates (5-10 min)

**Order Matters:**
- Update CI matrix FIRST, verify tests pass
- Then update classifiers and publish
- Badge will update automatically from new PyPI metadata

### Pre-Release Verification

**Before publishing to PyPI:**

# Check version consistency
python -c "import setup; print(setup.version)"  # If setup.py
grep "version" pyproject.toml  # If pyproject.toml
git describe --tags

# Check classifiers present
grep "Programming Language :: Python :: 3" setup.py

# Verify all versions tested in CI
gh run list --workflow=ci.yml --limit 1 --json conclusion

All should be consistent and CI should pass.

---

## Related Documentation

**Common Principles:** See .kiro/steering/badge-standards.md
**System Overview:** See .kiro/specs/badge-system/overview.md
**Core Badges:** See .kiro/specs/badge-system/core-badges.md
**Performance Badges:** See .kiro/specs/badge-system/performance-badges.md
**Verification:** See .kiro/specs/badge-system/verification.md
**Troubleshooting:** See .kiro/specs/badge-system/troubleshooting.md

---

**End of Quality Badges Specification**