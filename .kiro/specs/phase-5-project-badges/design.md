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
2. **Atomic Operations**: Prevent file corruption during concurrent access
3. **Shields.io Integration**: Leverage external service for badge generation
4. **Local Security Validation**: Catch issues before GitHub Actions
5. **PyPI Compatibility**: Ensure badges work post-publication

## Components and Interfaces

### Badge Generator (`badges/generator.py`)

**Purpose**: Generate shields.io URLs for each badge type

**Key Functions**:
```python
def generate_quality_gate_badge() -> str:
    """Generate GitHub Actions workflow status badge URL."""
    
def generate_security_scan_badge() -> str:
    """Generate security scan workflow status badge URL."""
    
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
- **GitHub Actions badges**: Use GitHub API to check workflow status
- **Code quality badges**: Run local checks (ruff, mypy) to determine status
- **Static badges**: Use project configuration (pyproject.toml, LICENSE)
- **PyPI badges**: Use PyPI API for version and download information

### README Updater (`badges/updater.py`)

**Purpose**: Atomically update README.md with generated badges

**Key Functions**:
```python
def update_readme_with_badges(badges: List[str]) -> bool:
    """Update README.md with badge markdown using atomic writes."""
    
def atomic_write_readme(content: str, max_retries: int = 10) -> bool:
    """Perform atomic write with retry logic for race condition prevention."""
    
def find_badge_section(content: str) -> Tuple[int, int]:
    """Locate badge insertion point in README content."""
```

**Atomic Write Implementation**:
1. Create temporary file with new content
2. Verify content integrity
3. Rename temporary file to README.md (atomic operation)
4. Handle file contention with 5-second waits, up to 10 retries

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
```

### Configuration (`badges/config.py`)

**Purpose**: Centralize badge configuration and URL templates

**Configuration Structure**:
```python
BADGE_CONFIG = {
    'github_repo': 'username/mypylogger',
    'pypi_package': 'mypylogger',
    'shields_base_url': 'https://img.shields.io',
    'badge_templates': {
        'quality_gate': 'github/actions/workflow/status/{repo}/quality-gate.yml',
        'security_scan': 'github/actions/workflow/status/{repo}/security-scan.yml',
        'code_style': 'badge/code%20style-ruff-000000',
        'type_checked': 'badge/type%20checked-mypy-blue',
        'python_versions': 'pypi/pyversions/{package}',
        'pypi_version': 'pypi/v/{package}',
        'downloads': 'badge/downloads-development-yellow',
        'license': 'github/license/{repo}'
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
1. Implement badge URL generation for all 8 badge types
2. Create shields.io integration with status detection
3. Implement basic configuration management

### Phase 2: README Integration
1. Implement atomic README update mechanism
2. Add race condition prevention with retry logic
3. Create badge section insertion logic

### Phase 3: Security Integration
1. Integrate security scanning tools (bandit, safety, semgrep)
2. Enhance run_tests.sh with security checks
3. Implement CodeQL simulation where possible

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

This design provides a robust, minimal implementation that meets all requirements while maintaining simplicity and reliability for the MVP badge system.