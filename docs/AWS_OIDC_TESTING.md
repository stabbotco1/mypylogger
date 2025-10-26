# AWS OIDC Workflow Testing Documentation

## Overview

This document describes the testing and validation procedures for the AWS OIDC configuration in the PyPI publishing workflow.

## Test Coverage

### 1. AWS Configuration Validation Tests

**Script**: `scripts/validate_aws_config.py`

**Test Scenarios**:
- ✅ Valid AWS configuration with all required parameters
- ✅ Missing AWS_ROLE_ARN detection and error handling
- ✅ Invalid AWS region format detection
- ✅ Default region fallback to `us-east-1`
- ✅ AWS secret name validation

**Validation Rules**:
- AWS regions must match pattern: `^[a-z]{2,3}-[a-z]+-\d+$`
- AWS Role ARN must match pattern: `^arn:aws:iam::\d{12}:role/[a-zA-Z0-9+=,.@_-]+$`
- AWS secret names must contain only alphanumeric characters and `/_+=.@-`

### 2. Workflow YAML Syntax Tests

**Test Scenarios**:
- ✅ Valid YAML syntax parsing
- ✅ Required workflow sections present (`name`, `on`, `jobs`)
- ✅ `publish-to-pypi` job exists
- ✅ AWS authentication steps present

### 3. AWS Region Scenarios

**Tested Regions**:
- ✅ `us-east-1` (Default US East region)
- ✅ `eu-west-1` (EU West region)
- ✅ `ap-southeast-1` (Asia Pacific region)
- ✅ `ca-central-1` (Canada Central region)
- ✅ No region specified (defaults to `us-east-1`)

### 4. Error Message Quality Tests

**Test Scenarios**:
- ✅ Missing AWS_ROLE_ARN provides helpful error message
- ✅ Invalid region format provides clear guidance
- ✅ Error messages include troubleshooting steps

## Retry Logic Implementation

### Exponential Backoff Strategy

The workflow implements a 3-attempt retry strategy with exponential backoff:

1. **Attempt 1**: Immediate execution
2. **Attempt 2**: 2-second delay after first failure
3. **Attempt 3**: 4-second delay after second failure (final attempt)

### Retry Implementation

```yaml
- name: Configure AWS OIDC authentication (Attempt 1)
  id: aws-auth-1
  uses: aws-actions/configure-aws-credentials@v4
  continue-on-error: true
  # ... configuration

- name: Wait and retry AWS authentication (Attempt 2)
  if: steps.aws-auth-1.outcome == 'failure'
  run: sleep 2

- name: Configure AWS OIDC authentication (Attempt 2)
  id: aws-auth-2
  if: steps.aws-auth-1.outcome == 'failure'
  # ... retry configuration

# Similar pattern for attempt 3
```

## Configuration Parameters

### Required GitHub Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ROLE_ARN` | IAM Role ARN for OIDC authentication | `arn:aws:iam::123456789012:role/GitHubActions-PyPI-Role` |
| `AWS_SECRET_NAME` | Secrets Manager secret name | `pypi-token-secret` |
| `AWS_REGION` | AWS region (optional, defaults to `us-east-1`) | `us-east-1` |

### Default Values

- **AWS Region**: `us-east-1` (if not specified)
- **Session Name**: `GitHubActions-PyPI-Publishing`
- **Session Duration**: 900 seconds (15 minutes)
- **Retry Mode**: `adaptive`
- **Max Attempts**: 3

## Running Tests

### Automated Test Suite

```bash
# Run complete AWS OIDC workflow tests
python scripts/test_aws_oidc_workflow.py
```

### Manual Validation

```bash
# Test AWS configuration validation
export AWS_REGION="us-east-1"
export AWS_ROLE_ARN="arn:aws:iam::123456789012:role/GitHubActions-PyPI-Role"
export AWS_SECRET_NAME="pypi-token-secret"
python scripts/validate_aws_config.py

# Validate workflow YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/pypi-publish.yml')); print('✅ Valid YAML')"
```

## Troubleshooting Guide

### Common Issues

1. **Missing aws-region parameter**
   - **Error**: "Input required and not supplied: aws-region"
   - **Solution**: Ensure `aws-region: ${{ secrets.AWS_REGION || 'us-east-1' }}` is present

2. **Invalid AWS region format**
   - **Error**: "Invalid AWS region format"
   - **Solution**: Use valid AWS region (e.g., `us-east-1`, `eu-west-2`)

3. **Missing AWS_ROLE_ARN**
   - **Error**: "AWS_ROLE_ARN is required"
   - **Solution**: Set AWS_ROLE_ARN in GitHub repository secrets

4. **Secrets Manager access denied**
   - **Error**: "Access denied to secret"
   - **Solution**: Verify IAM role has SecretsManagerReadWrite permissions

### Validation Checklist

Before deploying to production:

- [ ] All test scenarios pass (`python scripts/test_aws_oidc_workflow.py`)
- [ ] AWS_ROLE_ARN is configured in GitHub secrets
- [ ] AWS_SECRET_NAME is configured in GitHub secrets
- [ ] IAM role has proper trust relationship with GitHub OIDC
- [ ] IAM role has SecretsManagerReadWrite permissions
- [ ] PyPI token is stored in AWS Secrets Manager
- [ ] Workflow YAML syntax is valid

## Test Results

**Last Test Run**: 2025-10-26T19:56:38Z

**Results**:
- AWS Configuration Validation: ✅ PASS
- Workflow YAML Syntax: ✅ PASS
- AWS Region Scenarios: ✅ PASS
- Error Messages: ✅ PASS

**Success Rate**: 100% (4/4 tests passed)

## Security Considerations

### OIDC Authentication Benefits

1. **No long-lived credentials**: Uses temporary tokens
2. **Scoped permissions**: Role-based access control
3. **Audit trail**: All actions logged in AWS CloudTrail
4. **Automatic rotation**: Tokens expire after 15 minutes

### Best Practices

1. Use least-privilege IAM policies
2. Regularly rotate PyPI tokens in Secrets Manager
3. Monitor AWS CloudTrail for authentication events
4. Set up alerts for authentication failures
5. Use separate AWS accounts for different environments

## Future Enhancements

### Potential Improvements

1. **Health checks**: Add periodic connectivity tests
2. **Metrics collection**: Track authentication success rates
3. **Alert integration**: Notify on repeated failures
4. **Multi-region support**: Failover to backup regions
5. **Enhanced logging**: Structured logs for better debugging