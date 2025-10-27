# YAML Validation CI/CD Test Report

**Generated**: 2025-10-27 01:25:32 UTC
**Total Tests**: 10
**Passed**: 8
**Failed**: 2
**Success Rate**: 80.0%

## Test Results

### Valid YAML Validation
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:31 UTC

**Details**:
- return_code: 0
- stdout: 🔍 Running validation check (no repairs or modifications)...
🔍 Found 1 security files to validate
  V...
- stderr: 
- files_created: 1

### Indentation Corruption Scenario
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- corruption_detected: True
- check_return_code: 1
- repair_return_code: 1
- check_output: 🔍 Running validation check (no repairs or modifications)...
🔍 Found 2 security files to validate
  V...
- repair_output: 🔍 Found 2 security files to validate
  Validating: security/findings/corrupted-timeline.yml
    Atte...

### Special Characters Corruption Scenario
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- return_code: 1
- stdout: 🔍 Running validation check (no repairs or modifications)...
🔍 Found 4 security files to validate
  V...
- stderr: 
- handled_gracefully: True

### Structural Corruption Scenario
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- return_code: 1
- stdout: 🔍 Running validation check (no repairs or modifications)...
🔍 Found 5 security files to validate
  V...
- stderr: 
- validation_completed: True

### Automatic Repair Functionality
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- initially_invalid: True
- repair_attempted: True
- backup_created: True
- repair_return_code: 1
- repair_output: 🔄 Creating backups of all YAML files...
  Created backup: security/backups/corrupted-timeline.backup...

### Graceful Degradation
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- degradation_activated: True
- return_code: 0
- stdout: 🔍 Found 10 security files to validate
  Validating: security/findings/corrupted-timeline.backup.2025...
- stderr: 

### Degraded Mode Operation
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- degraded_mode_activated: True
- emergency_files_created: True
- return_code: 0
- stdout: 🔍 Found 19 security files to validate
  Validating: security/findings/SECURITY_FINDINGS.md
  Validat...

### Error Recovery Mechanisms
**Status**: ✅ PASS
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- recovery_attempted: True
- return_code: 0
- stdout: 🔍 Found 22 security files to validate
  Validating: security/config/valid-config.yml
  Validating: s...
- files_created: 3

### Performance Impact Validation
**Status**: ❌ FAIL
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- validation_time: 0.04409980773925781
- performance_acceptable: True
- validation_successful: False
- files_processed: 10
- return_code: 1

### CI Environment Simulation
**Status**: ❌ FAIL
**Timestamp**: 2025-10-27 01:25:32 UTC

**Details**:
- return_code: 1
- stdout: 🔍 Running validation check (no repairs or modifications)...
🔍 Found 39 security files to validate
  ...
- stderr: 
- ci_environment: True
