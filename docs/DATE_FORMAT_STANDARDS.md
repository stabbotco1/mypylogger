# Date Format Standards

## Overview

This document defines standardized date formats for the mypylogger project to ensure consistency across all documentation, code, and configuration files.

## Standard Date Formats

### ISO 8601 Standard
All dates in the project should follow ISO 8601 format for international compatibility and machine readability.

#### Date Only
**Format**: `YYYY-MM-DD`
**Example**: `2025-10-04`
**Usage**: Documentation dates, configuration dates, version dates

#### Date and Time (UTC)
**Format**: `YYYY-MM-DDTHH:MM:SS.sssZ`
**Example**: `2025-10-04T22:30:45.123Z`
**Usage**: Log timestamps, API responses, detailed timestamps

#### Date and Time (Local)
**Format**: `YYYY-MM-DDTHH:MM:SS±HH:MM`
**Example**: `2025-10-04T15:30:45-07:00`
**Usage**: Local time references (rare, prefer UTC)

### Human-Readable Formats
For user-facing documentation where readability is prioritized over machine parsing.

#### Month Year
**Format**: `Month YYYY`
**Example**: `October 2025`
**Usage**: High-level documentation dates, policy updates

#### Full Date
**Format**: `Month DD, YYYY`
**Example**: `October 4, 2025`
**Usage**: Release notes, announcements (use sparingly)

## Usage Guidelines

### Documentation Files

#### Security and Policy Documents
```markdown
**Last Updated**: 2025-10-04
**Next Review**: 2026-01-04
**Policy Effective**: 2025-10-04
```

#### Vulnerability Reports
```markdown
**Scan Date**: 2025-10-04T22:27:00Z
**Report Generated**: 2025-10-04T22:30:00Z
**Next Scan**: 2025-10-05T22:27:00Z
```

#### Configuration Files
```yaml
# Safety policy expiration
expires: "2026-12-31"

# Workflow schedule
schedule:
  - cron: '0 2 * * 0'  # Weekly on Sundays at 2 AM UTC
```

### Code and Examples

#### Log Output Examples
```json
{
  "time": "2025-10-04T22:30:45.123Z",
  "levelname": "INFO",
  "message": "Application started"
}
```

#### File Naming Examples
```
logs/my_app_2025_10_04.log
reports/security_scan_2025_10_04.txt
backups/database_2025_10_04_22_30.sql
```

#### Test Data
```python
# Use relative dates for test data
from datetime import datetime, timedelta

test_date = datetime.utcnow()
past_date = test_date - timedelta(days=30)
future_date = test_date + timedelta(days=30)
```

### Version Control

#### Git Tags
```bash
# Version tags with date
git tag -a v0.1.0 -m "Release v0.1.0 - 2025-10-04"

# Date-based tags for snapshots
git tag snapshot-2025-10-04
```

#### Commit Messages
```bash
# Include date context when relevant
git commit -m "Update security scan results (2025-10-04)"
git commit -m "Fix vulnerability reported on 2025-10-03"
```

## Format Validation

### Automated Validation
The project includes automated date format validation:

```bash
# Check date formats in documentation
make validate-docs-dates

# Verbose output showing all dates
make validate-docs-dates-verbose
```

### Manual Validation
Regular expressions for validating date formats:

```python
# ISO 8601 date
r'\b\d{4}-\d{2}-\d{2}\b'

# ISO 8601 timestamp
r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?\b'

# Month Year format
r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
```

## Common Patterns

### Documentation Headers
```markdown
---
title: "Document Title"
date: "2025-10-04"
last_updated: "2025-10-04"
version: "1.0"
---
```

### Configuration Timestamps
```yaml
metadata:
  created: "2025-10-04T22:30:45Z"
  updated: "2025-10-04T22:30:45Z"
  expires: "2026-10-04T22:30:45Z"
```

### API Responses
```json
{
  "timestamp": "2025-10-04T22:30:45.123Z",
  "created_at": "2025-10-04T22:30:45.123Z",
  "updated_at": "2025-10-04T22:30:45.123Z",
  "expires_at": "2026-10-04T22:30:45.123Z"
}
```

## Timezone Handling

### Preferred: UTC
Always use UTC for:
- Log timestamps
- API responses
- Database records
- Configuration files
- Automated systems

### Local Time (When Necessary)
Include timezone offset when using local time:
- User interface displays
- Regional documentation
- Local deployment schedules

### Timezone Conversion
```python
from datetime import datetime, timezone

# Always store in UTC
utc_time = datetime.now(timezone.utc)
iso_string = utc_time.isoformat()

# Convert for display
local_time = utc_time.astimezone()
```

## Migration Guidelines

### Updating Existing Dates

#### Step 1: Identify Non-Standard Dates
```bash
# Find dates that don't match ISO 8601
grep -r '\b[0-9]\{1,2\}/[0-9]\{1,2\}/[0-9]\{4\}\b' docs/
grep -r '\b[0-9]\{1,2\}-[0-9]\{1,2\}-[0-9]\{4\}\b' docs/
```

#### Step 2: Convert to Standard Format
```bash
# Convert MM/DD/YYYY to YYYY-MM-DD
# Convert DD-MM-YYYY to YYYY-MM-DD
# Update manually or with sed scripts
```

#### Step 3: Validate Changes
```bash
# Run validation after changes
make validate-docs-dates
```

### Updating Code Examples
```python
# Before (non-standard)
log_file = f"logs/app_{datetime.now().strftime('%m_%d_%Y')}.log"

# After (standard)
log_file = f"logs/app_{datetime.now().strftime('%Y_%m_%d')}.log"
```

## Best Practices

### Do's
- ✅ Use ISO 8601 format for all machine-readable dates
- ✅ Include timezone information (prefer UTC)
- ✅ Use consistent format within each document
- ✅ Validate dates with automated tools
- ✅ Update dates when content changes significantly

### Don'ts
- ❌ Mix date formats within the same document
- ❌ Use ambiguous formats (MM/DD/YY vs DD/MM/YY)
- ❌ Omit timezone information for timestamps
- ❌ Use relative dates in permanent documentation ("last month")
- ❌ Leave placeholder dates in production documentation

### Special Cases

#### Historical Dates
For historical references, use the appropriate format for the context:
```markdown
# Historical software versions
- Python 2.7 (released 2010-07-03, EOL 2020-01-01)
- Python 3.0 (released 2008-12-03)
```

#### Future Dates
For planned dates or expiration dates:
```markdown
# Roadmap items
- Feature X: Planned for 2025-12-01
- Support ends: 2026-12-31
```

#### Approximate Dates
When exact dates are not available:
```markdown
# Use quarters or months for approximations
- Approximately Q4 2025
- Expected in December 2025
- Sometime in 2025
```

## Tools and Resources

### Validation Tools
- `scripts/validate_documentation_dates.py` - Project-specific date validation
- `make validate-docs-dates` - Quick validation command
- Online ISO 8601 validators for manual checking

### Conversion Tools
```python
# Python datetime formatting
from datetime import datetime

# Current date in ISO format
iso_date = datetime.now().strftime('%Y-%m-%d')
iso_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
```

### IDE Integration
Most modern IDEs support date format validation and conversion:
- VS Code: Date format extensions
- PyCharm: Built-in datetime formatting
- Vim/Neovim: Date manipulation plugins

This standard ensures consistent, professional, and machine-readable date handling throughout the mypylogger project.
