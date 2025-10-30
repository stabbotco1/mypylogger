# Implementation Plan

- [x] 1. Set up badge system project structure
  - Create ./badges directory with proper Python package structure
  - Create __init__.py, generator.py, updater.py, security.py, and config.py files
  - Set up basic module imports and package initialization
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. Implement badge configuration and URL generation
- [x] 2.1 Create badge configuration system
  - Implement BadgeConfig dataclass with GitHub repo, PyPI package, and shields.io settings
  - Create BADGE_CONFIG dictionary with all 8 badge template URLs
  - Add configuration validation and error handling
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 3.1, 3.4_

- [x] 2.2 Implement shields.io URL generation for static badges
  - Create generate_code_style_badge() function for Ruff compliance badge
  - Create generate_type_check_badge() function for mypy validation badge
  - Create generate_python_versions_badge() function for Python compatibility
  - Create generate_license_badge() function for MIT license badge
  - _Requirements: 1.4, 1.5, 1.9, 3.1, 3.2_

- [x] 2.3 Implement dynamic badge generation with API integration
  - Create generate_quality_gate_badge() function that aggregates all quality checks (linting, style, type checking, security)
  - Create generate_pypi_version_badge() function using PyPI API
  - Add error handling for API failures with fallback to "unknown" status
  - _Requirements: 1.1, 1.2, 1.5, 1.6, 3.1, 3.2, 6.1, 6.2, 6.4_

- [x] 2.6 Implement PyPI downloads badge with shields.io direct integration
  - Create generate_downloads_badge() function using shields.io PyPI monthly downloads endpoint
  - Implement URL generation for `https://img.shields.io/pypi/dm/{package}` format
  - Add configuration support for PyPI package name
  - Test badge displays real-time monthly download counts from PyPI
  - _Requirements: 1.7, 3.1, 3.4_

- [x] 2.5 Implement comprehensive security badge with all security tests
  - Create generate_comprehensive_security_badge() function combining all security results (local + GitHub CodeQL)
  - Implement get_github_codeql_status() function to query GitHub CodeQL API
  - Create get_comprehensive_security_status() function to combine all security scans
  - Add security badge linking to GitHub CodeQL results page
  - Implement security status determination logic ("Verified", "Issues Found", "Scanning", "Unknown")
  - Add GitHub API authentication support for private repositories (optional)
  - _Requirements: 1.2, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 2.4 Write unit tests for badge generation
  - Create tests for all badge URL generation functions including comprehensive security badge
  - Test API failure scenarios and fallback behavior for GitHub CodeQL integration
  - Test shields.io URL formatting correctness for all 8 badge types including PyPI downloads integration
  - Test PyPI downloads badge URL generation with different package names
  - Test security status combination logic (all security tests combined)
  - Test quality gate status aggregation logic (all quality checks combined)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 3. Implement atomic README update system
- [x] 3.1 Create README parsing and badge section management
  - Implement find_badge_section() function to locate badge insertion point
  - Create badge section HTML/markdown generation
  - Add badge section marker detection and replacement logic
  - _Requirements: 2.1, 4.1, 4.5_

- [x] 3.2 Implement atomic write mechanism with race condition prevention
  - Create atomic_write_readme() function using temporary files and rename operations
  - Implement retry logic with 5-second waits up to 10 attempts for file contention
  - Add file integrity verification and backup creation
  - Handle concurrent access scenarios with proper error reporting
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3.3 Create main README update workflow
  - Implement update_readme_with_badges() function coordinating badge generation and file updates
  - Add badge status detection logic (run tests vs read existing results)
  - Integrate all badge types into single update operation
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.4 Write unit tests for README update system
  - Test atomic write functionality and retry mechanisms
  - Test badge section insertion and replacement
  - Test concurrent update scenarios and race condition prevention
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Integrate security scanning into local testing workflow
- [x] 4.1 Implement security scanning functions
  - Create run_bandit_scan() function for Python security analysis
  - Create run_safety_check() function for dependency vulnerability scanning
  - Create run_semgrep_analysis() function for security pattern detection
  - Create simulate_codeql_checks() function for CodeQL-equivalent analysis
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.4 Enhance security integration for comprehensive security badge
  - Integrate local security scan results with GitHub CodeQL API results
  - Update security scanning functions to support comprehensive security badge status
  - Add security scan result caching to avoid redundant API calls
  - Implement security status aggregation logic for badge display
  - _Requirements: 5.6, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 4.2 Enhance run_tests.sh script with security integration
  - Add security scanning execution to existing test script
  - Integrate security scan results into overall test pass/fail logic
  - Add proper error reporting and exit codes for security failures
  - Ensure security scans run before badge generation to reflect current state
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.3 Write unit tests for security integration
  - Test individual security scanning functions
  - Test security scan result processing and reporting
  - Test integration with run_tests.sh workflow
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5. Create badge system entry point and CLI interface
- [x] 5.1 Implement main badge system interface
  - Create Badge and BadgeSection dataclasses for data modeling
  - Implement main badge update workflow in badges/__init__.py
  - Add command-line interface for manual badge updates
  - Create error handling and logging for the complete workflow
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.2 Add badge status detection logic
  - Implement logic to determine when to run tests vs read existing results
  - Add badge status caching to avoid unnecessary API calls within single run
  - Create status validation and verification functions
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5.3 Write integration tests for complete badge workflow
  - Test end-to-end badge generation and README update process
  - Test badge status detection and API integration
  - Test error handling and recovery scenarios
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 6. Implement CI-only badge updates and final integration
- [x] 6.1 Implement CI-only badge update workflow
  - Modify badge updater to work exclusively in CI environment
  - Add git commit functionality for README updates with "[skip ci]" messages
  - Remove local badge update capabilities to prevent inconsistencies
  - Ensure badge updates only occur after successful CI test execution
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6.2 Update local testing to focus on code quality only
  - Modify run_tests.sh to focus on test execution without badge updates
  - Ensure local security scans run for validation but don't update badges
  - Remove any local README update functionality
  - Focus local development on code and test quality only
  - _Requirements: 6.5, 8.5_

- [x] 6.3 Create CI workflow integration
  - Design GitHub Actions workflow step for badge updates
  - Implement badge update as post-test CI step
  - Add proper git configuration and commit handling in CI
  - Test CI badge update workflow with actual GitHub Actions
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6.4 Verify PyPI compatibility and documentation
  - Test badge functionality with PyPI package structure
  - Ensure badges work correctly after package publication
  - Create documentation for CI-only badge update workflow
  - Document local vs CI development workflow separation
  - _Requirements: 3.4, 7.4, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 6.5 Final testing and validation
  - Run complete local test suite focusing on code quality only
  - Validate badge generation functions work correctly (without README updates)
  - Test CI badge update workflow in actual GitHub Actions environment
  - Verify badges reflect actual CI test results and GitHub CodeQL status
  - Ensure local development workflow is clean and focused on code quality
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_