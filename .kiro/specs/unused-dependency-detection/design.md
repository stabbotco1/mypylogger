# Design Document

## Overview

This design implements unused dependency detection for the mypylogger project by integrating the `deptry` tool into the existing quality gate infrastructure. The solution will identify unused dependencies in pyproject.toml and provide clear feedback to developers while maintaining consistency with the current testing workflow.

## Architecture

### Tool Selection: deptry

After evaluating available dependency detection tools, `deptry` is selected because:

- **Fast and reliable**: Written in Rust for performance
- **Zero configuration**: Works out-of-the-box with standard Python projects
- **UV compatible**: Integrates seamlessly with the project's UV-based workflow
- **Clear output**: Provides specific information about unused dependencies
- **Active maintenance**: Well-maintained with regular updates

### Integration Points

1. **pyproject.toml**: Add deptry to development dependencies
2. **Master Test Script**: Add new quality gate section for dependency checking
3. **Error Handling**: Follow existing patterns for consistent user experience
4. **Dependency Cleanup**: Remove unused dependencies as part of implementation

## Components and Interfaces

### Component 1: Dependency Detection Tool Integration

**Purpose**: Add deptry to the project's development toolchain

**Configuration**:
```toml
# pyproject.toml addition
[dependency-groups]
dev = [
    # ... existing dev dependencies ...
    "deptry>=0.20.0",  # Unused dependency detection
]
```

**Execution Pattern**:
```bash
uv run --active deptry .
```

### Component 2: Master Test Script Enhancement

**Purpose**: Integrate dependency checking into the quality gate workflow

**New Section Addition**:
- Section number: 7 (after existing security scanning)
- Description: "Dependency Usage Check"
- Command: `uv run --active deptry .`
- Error handling: Follow existing `run_check` function pattern

**Integration Pattern**:
```bash
echo "7. Dependency Usage Check"
echo "-------------------------"
run_check "uv run --active deptry ." "Unused dependency detection"
```

### Component 3: Dependency Cleanup

**Purpose**: Remove currently unused dependencies to achieve zero-dependency goal

**Changes Required**:
1. Remove `jinja2>=3.1.6` from dependencies
2. Remove `python-json-logger>=4.0.0` from dependencies
3. Update project description from "Zero-dependency" to accurately reflect the state
4. Verify all tests still pass after removal

## Data Models

### Dependency Check Result

The deptry tool outputs structured information about dependency usage:

```
Unused dependencies:
- jinja2 (declared in pyproject.toml but not used)
- python-json-logger (declared in pyproject.toml but not used)
```

### Error Reporting Format

Following the existing master test script pattern:

```bash
# Success case
✓ Unused dependency detection

# Failure case  
✗ Unused dependency detection
Error output:
[deptry output with specific unused dependencies]
```

## Error Handling

### Graceful Degradation

1. **Tool Installation Issues**: If deptry fails to install, the check should fail with clear error message
2. **Execution Failures**: If deptry execution fails, provide diagnostic information
3. **False Positives**: Configuration options available if needed (though unlikely with current codebase)

### Error Recovery

1. **Clear Instructions**: Error messages should indicate which dependencies to remove
2. **Helpful Commands**: Suggest `uv remove <package>` commands for cleanup
3. **Verification Steps**: Guide users to re-run tests after dependency removal

## Testing Strategy

### Validation Approach

1. **Before Implementation**: Verify deptry correctly identifies jinja2 and python-json-logger as unused
2. **During Implementation**: Ensure master test script integration works correctly
3. **After Cleanup**: Confirm all quality gates pass with zero dependencies
4. **Regression Testing**: Verify package import and functionality remain intact

### Test Scenarios

1. **Unused Dependencies Present**: Script should fail and report specific packages
2. **All Dependencies Used**: Script should pass cleanly
3. **Tool Execution Failure**: Script should fail with diagnostic information
4. **Zero Dependencies**: Final state should pass all quality gates

### Integration Testing

1. **Master Script Execution**: Full `./scripts/run_tests.sh` run should pass after implementation
2. **Individual Tool Testing**: `uv run deptry .` should work independently
3. **CI/CD Compatibility**: Changes should not break existing automation workflows

## Implementation Phases

### Phase 1: Tool Integration
- Add deptry to development dependencies
- Update master test script with new quality gate
- Verify tool execution and error reporting

### Phase 2: Dependency Cleanup
- Remove unused dependencies from pyproject.toml
- Update project description for accuracy
- Verify all functionality remains intact

### Phase 3: Validation
- Run complete test suite to ensure no regressions
- Verify zero-dependency goal is achieved
- Update documentation if needed

## Configuration Details

### deptry Configuration

Default configuration should work without additional setup:
- Scans `src/` directory automatically
- Checks `pyproject.toml` dependencies
- Reports unused packages clearly

If configuration is needed, it can be added to `pyproject.toml`:
```toml
[tool.deptry]
# Configuration options if needed (likely not required)
```

### UV Integration

The tool will be executed using the established UV pattern:
```bash
uv run --active deptry .
```

This ensures:
- Consistent environment usage
- Proper dependency resolution
- Integration with existing workflow

## Success Criteria

1. **Detection Accuracy**: Tool correctly identifies jinja2 and python-json-logger as unused
2. **Integration Success**: Master test script includes dependency checking seamlessly
3. **Cleanup Completion**: Project achieves true zero-dependency status
4. **Quality Maintenance**: All existing quality gates continue to pass
5. **Performance**: Dependency check completes within 30 seconds
6. **User Experience**: Clear error messages and helpful guidance for developers