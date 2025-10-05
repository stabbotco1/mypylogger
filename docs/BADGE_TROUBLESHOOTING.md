# Badge Troubleshooting Quick Reference

## Quick Diagnostics

### 🔍 Check Badge Health
```bash
make badge-health-check
```

### 🔗 Validate Badge Links
```bash
make verify-badges
```

### ⚡ Test Performance Badges
```bash
python scripts/measure_performance.py --verbose
```

## Common Problems & Solutions

### 🚫 Badge Not Displaying

**Problem**: Badge shows as broken image or doesn't load

**Quick Fixes**:
1. Hard refresh browser (Ctrl+F5 / Cmd+Shift+R)
2. Check badge URL directly: Copy badge URL and open in new tab
3. Run: `make verify-badges`

**If Still Broken**:
- Check [Shields.io Status](https://status.shields.io/)
- Verify URL encoding (spaces = %20, commas = %2C)
- Check for typos in badge URL

### ❓ Badge Shows "Unknown"

**Problem**: Badge displays "unknown" instead of expected value

**Quick Fixes**:
1. Check if GitHub Actions workflow has run recently
2. Verify workflow name matches badge URL exactly
3. Manually trigger the workflow

**Common Causes**:
- Workflow hasn't run yet (new repository)
- Workflow name changed but badge URL not updated
- Workflow permissions issues

### 🔗 Badge Link Broken

**Problem**: Clicking badge leads to 404 or wrong page

**Quick Fix**:
```bash
make verify-badges  # This checks all badge links
```

**Manual Check**:
1. Click each badge to verify destination
2. Update link targets in README.md if needed
3. Test again after changes

### 📊 Performance Badge Outdated

**Problem**: Performance badges show old or incorrect metrics

**Quick Fixes**:
1. Run fresh benchmarks:
   ```bash
   python scripts/measure_performance.py --verbose
   ```

2. Update badges manually:
   ```bash
   python scripts/measure_performance.py --update-badges
   ```

3. Check automated workflow logs in GitHub Actions

### 🐌 Slow Badge Loading

**Problem**: Badges take too long to load

**Quick Test**:
```bash
make test-badge-performance
```

**Solutions**:
- Check internet connection
- Verify Shields.io service status
- Consider badge caching issues

## Emergency Commands

### 🚨 Full Badge System Check
```bash
# Comprehensive health check
python scripts/badge_health_monitor.py --verbose

# Get JSON report for analysis
python scripts/badge_health_monitor.py --format json > badge_report.json
```

### 🔄 Reset Performance Badges
```bash
# Measure fresh performance
python scripts/measure_performance.py --verbose

# Update both OS badges
python scripts/measure_performance.py --update-badges

# Commit changes
git add README.md
git commit -m "Update performance badges with fresh measurements"
```

### 🛠️ Badge URL Debugging
```bash
# Test specific badge URL
curl -I "https://img.shields.io/badge/test-message-green"

# Check badge with parameters
curl -I "https://img.shields.io/badge/Ubuntu-0.012ms%2C%2086K%2Fsec-brightgreen?logo=ubuntu"
```

## Badge Status Indicators

### ✅ Healthy Badge Signs
- Loads quickly (<2 seconds)
- Shows current/accurate information
- Link navigates to correct destination
- Alt text is descriptive and meaningful

### ⚠️ Warning Signs
- Takes >5 seconds to load
- Shows outdated information
- Link leads to generic page instead of specific resource
- Displays "unknown" status occasionally

### 🚨 Critical Issues
- Consistently shows "unknown" status
- Badge URL returns 404 error
- Link is completely broken
- Badge causes page layout issues

## Quick Reference Commands

| Task | Command |
|------|---------|
| **Validate all badges** | `make verify-badges` |
| **Detailed validation** | `make validate-badges-verbose` |
| **Health check** | `make badge-health-check` |
| **Performance test** | `make test-badge-performance` |
| **Update performance** | `python scripts/measure_performance.py --update-badges` |
| **Fresh benchmarks** | `python scripts/measure_performance.py --verbose` |
| **CI health check** | `make badge-health-ci` |

## Badge URL Patterns

### GitHub Actions Status
```
https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow}.yml?branch={branch}&label={label}&logo=github
```

### PyPI Information
```
https://img.shields.io/pypi/v/{package}?logo=pypi&logoColor=white
https://img.shields.io/pypi/pyversions/{package}?logo=python&logoColor=white
https://img.shields.io/pypi/dm/{package}?logo=pypi&logoColor=white
```

### Custom Performance
```
https://img.shields.io/badge/{OS}-{latency}ms%2C%20{throughput}K%2Fsec-brightgreen?logo={logo}
```

### Static Badges
```
https://img.shields.io/badge/{label}-{message}-{color}?logo={icon}&logoColor={logoColor}
```

## URL Encoding Reference

| Character | Encoded |
|-----------|---------|
| Space | `%20` |
| Comma | `%2C` |
| Forward slash | `%2F` |
| Percent | `%25` |
| Ampersand | `%26` |

## When to Create GitHub Issues

### 🐛 Bug Reports
- Badge consistently shows incorrect information
- Badge links are permanently broken
- Performance badges show impossible values

### 🔧 Enhancement Requests
- Need new badge for additional metric
- Badge styling improvements
- Badge automation enhancements

### 📋 Maintenance Tasks
- Quarterly badge system review
- Badge service migration needs
- Documentation updates required

## Getting Help

### 📚 Documentation
- `docs/BADGE_CONFIGURATION.md` - Complete configuration reference
- `docs/BADGE_MANAGEMENT.md` - Comprehensive management guide
- `docs/PERFORMANCE_BADGES.md` - Performance badge specifics

### 🔧 Tools
- `scripts/validate_badges.py` - Badge validation script
- `scripts/badge_health_monitor.py` - Health monitoring script
- `scripts/measure_performance.py` - Performance measurement script

### 🤝 Support
- Create GitHub issue with badge problem details
- Include output from `make badge-health-check`
- Provide badge URLs and expected vs actual behavior

---

**💡 Pro Tip**: Run `make badge-health-check` weekly to catch issues early!
