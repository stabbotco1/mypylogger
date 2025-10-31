# Implementation Plan

- [ ] 1. Enhance master test script with coverage file generation
  - Modify `scripts/run_tests.sh` to extract coverage percentage from pytest-cov output
  - Add function to generate structured `docs/test-coverage-results.md` file after test execution
  - Include test count, test results summary, timestamp, and coverage status in results file
  - Implement atomic file write operations to prevent corruption during concurrent access
  - Add error handling for coverage extraction and file generation failures
  - _Requirements: 1.1, 1.2, 1.4, 6.1, 6.2, 6.3, 6.4, 6.5, 8.3_

- [x] 2. Implement file-based coverage data reading
  - Create `get_test_coverage_from_file()` function in `badges/status.py` to read coverage data from results file
  - Add robust parsing of coverage percentage, timestamp, test count, and status from markdown file
  - Implement fallback handling for missing or corrupted coverage results file
  - Add validation for coverage percentage range (0-100) and data format
  - Create `CoverageData` dataclass for structured coverage information
  - _Requirements: 1.3, 1.5, 6.1, 6.2, 6.3, 6.4, 6.5, 8.4_

- [ ] 3. Update test coverage badge generation to use file-based data
  - Modify `generate_test_coverage_badge()` function in `badges/generator.py` to use file-based coverage data
  - Update color logic to use new thresholds: green (≥95%), amber (90-94%), red (<90%)
  - Remove subprocess calls and timeout handling from badge generation
  - Add GitHub file link generation for badge click-through to detailed results
  - Implement error handling with fallback to default green badge (95%)
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 8.1, 8.2_

- [ ] 4. Integrate README badge updates with file-based system
  - Update README badge update functionality to use file-based coverage data instead of running additional coverage commands
  - Ensure badge links to GitHub file URL: `https://github.com/{owner}/{repo}/blob/main/docs/test-coverage-results.md`
  - Integrate file-based badge generation with existing atomic README update mechanism
  - Add badge update to master test script execution after coverage file generation
  - Maintain existing README formatting and badge section structure
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5. Ensure PyPI compatibility and badge display
  - Verify coverage badge displays correctly on PyPI package pages using README content
  - Test badge URL and GitHub file link functionality from PyPI package page context
  - Ensure PyPI markdown rendering supports badge display and click-through links
  - Validate badge appearance and color coding consistency across repository and PyPI
  - Test badge functionality with different coverage percentages and color thresholds
  - _Requirements: 2.4, 3.4, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 6. Clean up existing coverage badge implementation
  - Remove or update existing API-based test coverage badge code in `badges/generator.py`
  - Update `get_test_coverage_percentage()` function in `badges/status.py` to use file-based approach or mark as deprecated
  - Remove subprocess calls and timeout handling from existing coverage badge functions
  - Update all imports and function calls to use new file-based coverage functions
  - Ensure no conflicts between old and new coverage badge implementations
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 7. Update existing tests for file-based coverage system
  - Modify existing test coverage badge tests in `tests/unit/test_badge_generator.py` to use file-based approach
  - Update test mocking to use file content instead of subprocess mocking
  - Add tests for coverage results file parsing and error handling
  - Create tests for different coverage percentages and color logic with new thresholds
  - Add integration tests for complete workflow from test execution to badge update
  - _Requirements: 1.5, 3.1, 3.2, 3.3, 8.4, 8.5_

- [ ] 8. Update documentation and spec references
  - Update all references to test coverage badge implementation in phase-5-project-badges spec
  - Modify design documents to reflect file-based approach instead of API-based approach
  - Update task lists in other specs to reference new file-based coverage badge system
  - Remove obsolete API-based coverage badge tasks and requirements from existing specs
  - Add documentation for new coverage results file format and GitHub file linking
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 9. Validate complete file-based coverage workflow
  - Test complete workflow from test execution through coverage file generation to badge update
  - Verify master test script generates correct coverage results file with all required information
  - Test README badge update uses file-based data and completes within performance requirements
  - Validate badge color coding works correctly for all coverage threshold ranges
  - Test error handling and fallback behavior for missing or corrupted coverage files
  - Ensure badge links work correctly from both repository README and PyPI package page
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_