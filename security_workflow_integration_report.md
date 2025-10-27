# Security Workflow Integration Test Report

**Generated**: 2025-10-27 01:27:50 UTC
**Total Tests**: 7
**Passed**: 4
**Failed**: 3
**Success Rate**: 57.1%

## Test Results

### YAML Validation with Normal Security Workflow
**Status**: ❌ FAIL
**Timestamp**: 2025-10-27 01:27:49 UTC

**Details**:
- yaml_validation_success: True
- error_handler_success: False
- monitoring_success: False
- yaml_return_code: 0
- error_handler_return_code: 1
- monitoring_return_code: 1
- yaml_output: 🔍 Running validation check (no repairs or modifications)...
🔍 Found 2 security files to validate
  V...

### Error Handling with YAML Corruption
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:27:49 UTC

**Details**:
- yaml_degradation_activated: True
- error_handler_completed: True
- yaml_return_code: 0
- error_handler_return_code: 1
- yaml_output: 🔍 Found 2 security files to validate
  Validating: security/findings/remediation-plans.yml
  Validat...
- error_handler_output: 

### Fallback Mechanisms with Corrupted Data
**Status**: ❌ FAIL
**Timestamp**: 2025-10-27 01:27:49 UTC

**Details**:
- fallback_successful: False
- workflows_continued: True
- emergency_files_created: []
- yaml_return_code: 0
- error_handler_return_code: 1
- monitoring_return_code: 1

### Workflow Performance Impact
**Status**: ❌ FAIL
**Timestamp**: 2025-10-27 01:27:50 UTC

**Details**:
- baseline_time: 0.036016225814819336
- with_yaml_time: 0.06810712814331055
- performance_impact_percent: 89.10123590819724
- performance_acceptable: False
- baseline_success: False
- with_yaml_success: False

### Workflow Coordination with YAML Validation
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:27:50 UTC

**Details**:
- coordination_successful: True
- step_results: [3 items]
- total_steps: 3
- successful_steps: 3

### Error Propagation and Handling
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:27:50 UTC

**Details**:
- errors_detected: True
- degradation_activated: True
- error_handling_completed: True
- yaml_check_return_code: 1
- degradation_return_code: 0
- error_handler_return_code: 1

### Workflow Resilience to YAML Issues
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:27:50 UTC

**Details**:
- overall_resilience: True
- scenarios_tested: 3
- resilient_scenarios: 3
- scenario_results: [3 items]
