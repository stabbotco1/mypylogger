# Design Document

## Overview

The badge system implements a fast, lean MVP solution for displaying professional project badges in mypylogger v0.2.0's README.md. The design uses shields.io integration with Python APIs to generate dynamic badges that reflect current project state, with robust file handling to prevent race conditions during concurrent updates.

## Architecture

### High-Level Architecture

```
mypylogger/
├── badges/                    # All badge-specific code
│   ├── __init__.py           # Badge system entry point
│   ├── generator.py          # Core badge generation logic
│   ├── updater.py            # README update with atomic writes
│   ├── security.py           # Security scanning integration
│   └── config.py             # Badge configuration and URLs
├── scripts/
│   └── run_tests.sh          # Enhanced with security checks
└── README.md                 # Target file for badge insertion
```

### Design Principles

1. **Minimal Code Footprint**: Only essential code for MVP functionality
2. **CI-Only Badge Updates**: Badges updated exclusively by CI/CD workflows
3. **Shields.io Integration**: Leverage external service for badge generation
4. **Local Testing Focus**: Local development focuses on code quality, not badge updates
5. **Single Source of Truth**: CI environment determines badge status

## Components and Interfaces

### Badge Generator (`badges/generator.py`)

**Purpose**: Generate shields.io URLs for each badge type

**Key Functions**:
```python
def generate_quality_gate_badge() -> str:
    """Generate overall quality gate badge that requires all quality checks to pass."""
    
def generate_comprehensive_security_badge() -> str:
    """Generate comprehensive security badge combining all security tests (local + GitHub CodeQL)."""
    
def generate_code_style_badge() -> str:
    """Generate Ruff code style compliance badge URL."""
    
def generate_type_check_badge() -> str:
    """Generate mypy type checking badge URL."""
    
def generate_python_versions_badge() -> str:
    """Generate Python compatibility badge URL."""
    
def generate_pypi_version_badge() -> str:
    """Generate PyPI version badge URL."""
    
def generate_downloads_badge() -> str:
    """Generate downloads status badge URL."""
    
def generate_license_badge() -> str:
    """Generate MIT license badge URL."""
```

**Badge Status Detection**:
- **CI-driven status**: All badge status determined from CI test results
- **Quality Gate badge**: Reflects CI test execution results (all tests must pass)
- **Comprehensive security badge**: Combines CI security scans with GitHub CodeQL results
- **Code quality badges**: Based on CI execution of ruff and mypy
- **Static badges**: Use project configuration and PyPI API data
- **Local testing**: Focuses only on test execution, not badge generation

### README Updater (`badges/updater.py`)

**Purpose**: Update README.md with generated badges (CI-only execution)

**Key Functions**:
```python
def update_readme_with_badges(badges: List[str]) -> bool:
    """Update README.md with badge markdown (CI environment only)."""
    
def commit_badge_updates() -> bool:
    """Commit updated README back to main branch with [skip ci] message."""
    
def find_badge_section(content: str) -> Tuple[int, int]:
    """Locate badge insertion point in README content."""
```

**CI-Only Update Implementation**:
1. Generate badges based on CI test results
2. Update README.md with new badge URLs
3. Commit changes back to main branch
4. Use "[skip ci]" to prevent infinite CI loops
5. Handle git operations safely in CI environment

### Security Integration (`badges/security.py`)

**Purpose**: Integrate security scanning into local test workflow

**Key Functions**:
```python
def run_bandit_scan() -> bool:
    """Execute bandit security scanner and return pass/fail status."""
    
def run_safety_check() -> bool:
    """Execute safety dependency scanner and return pass/fail status."""
    
def run_semgrep_analysis() -> bool:
    """Execute semgrep security analysis and return pass/fail status."""
    
def simulate_codeql_checks() -> bool:
    """Run CodeQL-equivalent checks locally where possible."""
    
def get_github_codeql_status() -> str:
    """Get GitHub CodeQL scan status from GitHub API."""
    
def get_comprehensive_security_status() -> Dict[str, Any]:
    """Combine local security scans with GitHub CodeQL results."""
```

### Configuration (`badges/config.py`)

**Purpose**: Centralize badge configuration and URL templates

**Configuration Structure**:
```python
BADGE_CONFIG = {
    'github_repo': 'username/mypylogger',
    'pypi_package': 'mypylogger',
    'shields_base_url': 'https://img.shields.io',
    'github_api_base': 'https://api.github.com',
    'badge_templates': {
        'quality_gate': 'badge/quality%20gate-{status}-{color}',
        'comprehensive_security': 'badge/security-{status}-{color}',
        'code_style': 'badge/code%20style-ruff-000000',
        'type_checked': 'badge/type%20checked-mypy-blue',
        'python_versions': 'pypi/pyversions/{package}',
        'pypi_version': 'pypi/v/{package}',
        'downloads': 'badge/downloads-development-yellow',
        'license': 'github/license/{repo}'
    },
    'security_badge_links': {
        'codeql_results': 'https://github.com/{repo}/security/code-scanning',
        'security_tab': 'https://github.com/{repo}/security'
    }
}
```

## Data Models

### Badge Data Structure

```python
@dataclass
class Badge:
    """Represents a single project badge."""
    name: str
    url: str
    alt_text: str
    link_url: Optional[str] = None
    status: str = "unknown"  # "passing", "failing", "unknown"

@dataclass
class BadgeSection:
    """Represents the complete badge section for README."""
    title: str
    badges: List[Badge]
    markdown: str
```

### Configuration Model

```python
@dataclass
class BadgeConfig:
    """Badge system configuration."""
    github_repo: str
    pypi_package: str
    shields_base_url: str
    max_retries: int = 10
    retry_delay: int = 5
    badge_section_marker: str = "<!-- BADGES -->"
```

## Error Handling

### File Operation Errors

**Atomic Write Failures**:
- Retry mechanism with exponential backoff
- Fallback to backup file if corruption detected
- Detailed logging of failure reasons

**Race Condition Handling**:
- File locking detection
- Configurable retry attempts (default: 10)
- Graceful degradation if updates fail

### API Communication Errors

**GitHub API Failures**:
- Fallback to "unknown" status badges
- Rate limit handling with appropriate delays
- Authentication token support for higher limits

**PyPI API Failures**:
- Cache last known good values
- Fallback to static version information
- Graceful handling of network timeouts

### Security Scan Failures

**Tool Execution Errors**:
- Continue with other scans if one fails
- Report partial results rather than complete failure
- Provide clear error messages for debugging

## Testing Strategy

### Unit Tests

**Badge Generation Tests**:
```python
def test_generate_quality_gate_badge_success():
    """Test successful quality gate badge generation."""
    
def test_generate_badge_with_api_failure():
    """Test badge generation when API calls fail."""
    
def test_badge_url_formatting():
    """Test correct shields.io URL formatting."""
```

**README Update Tests**:
```python
def test_atomic_write_success():
    """Test successful atomic README update."""
    
def test_atomic_write_with_retries():
    """Test retry mechanism during file contention."""
    
def test_badge_section_insertion():
    """Test correct badge placement in README."""
```

### Integration Tests

**End-to-End Badge Workflow**:
```python
def test_complete_badge_update_workflow():
    """Test full badge generation and README update process."""
    
def test_concurrent_readme_updates():
    """Test race condition prevention during concurrent updates."""
    
def test_security_integration_workflow():
    """Test security scanning integration with badge updates."""
```

### Security Testing

**Security Scan Integration**:
- Verify all security tools execute correctly
- Test integration with run_tests.sh script
- Validate security scan result reporting

**File Security**:
- Test atomic write security (no partial writes)
- Verify temporary file cleanup
- Test permission handling

## Implementation Phases

### Phase 1: Core Badge Generation
1. Implement badge URL generation for all 9 badge types (including comprehensive security)
2. Create shields.io integration with status detection
3. Implement basic configuration management
4. Add GitHub API integration for CodeQL status retrieval

### Phase 2: README Integration
1. Implement atomic README update mechanism
2. Add race condition prevention with retry logic
3. Create badge section insertion logic

### Phase 3: Security Integration
1. Integrate security scanning tools (bandit, safety, semgrep)
2. Enhance run_tests.sh with security checks
3. Implement CodeQL simulation where possible
4. Add GitHub CodeQL API integration for comprehensive security badge
5. Implement security status combination logic (local + GitHub)

### Phase 4: Testing and Validation
1. Comprehensive unit and integration testing
2. End-to-end workflow validation
3. PyPI compatibility verification

## Performance Considerations

### Optimization Constraints

**MVP Focus**: No optimization beyond essential functionality
- Single-threaded badge generation (sufficient for 8 badges)
- Simple retry mechanism (no complex backoff algorithms)
- Basic caching (avoid unnecessary API calls within single run)

**Essential Optimizations**:
- Parallel API calls for independent badge status checks
- Simple result caching to avoid duplicate API requests
- Efficient README parsing (single pass for badge section location)

### Resource Usage

**Network Calls**: Maximum 8 API calls per badge update cycle
**File Operations**: Single atomic write per README update
**Memory Usage**: Minimal - process badges individually
**Execution Time**: Target <30 seconds for complete badge update

## Security Considerations

### API Security

**GitHub API Access**:
- Support for authentication tokens (optional)
- Rate limit respect and handling
- No sensitive data in API requests

**PyPI API Access**:
- Read-only public API usage
- No authentication required
- Standard HTTPS communication

### File Security

**README.md Protection**:
- Atomic writes prevent corruption
- Temporary file cleanup
- Backup creation before updates

**Badge Code Security**:
- Input validation for all external data
- Safe URL construction
- No code execution from external sources

### Local Security Scanning

**Tool Integration**:
- Secure execution of security scanners
- Proper handling of scan results
- No exposure of sensitive scan data

### Comprehensive Security Badge Integration

**GitHub CodeQL Integration**:
- Query GitHub API for CodeQL scan results
- Parse CodeQL alerts and status from security API endpoints
- Handle authentication for private repositories (optional)
- Combine CodeQL results with local security scan results

**Security Status Determination**:
- **"Verified"**: All local scans pass AND no open CodeQL alerts
- **"Issues Found"**: Any local scan fails OR open CodeQL alerts exist
- **"Scanning"**: CodeQL scans in progress or local scans running
- **"Unknown"**: Unable to determine status due to API failures

**Badge Link Strategy**:
- Primary link: GitHub CodeQL results page (`/security/code-scanning`)
- Fallback link: General security tab (`/security`)
- Include repository context in all security links

This design provides a robust, minimal implementation that meets all requirements while maintaining simplicity and reliability for the MVP badge system.