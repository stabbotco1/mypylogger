# Credential Security Guide

This document outlines the secure credential management practices for mypylogger PyPI publishing using AWS OIDC authentication.

## Overview

The mypylogger project uses AWS OIDC (OpenID Connect) authentication for secure PyPI publishing. This approach eliminates the need to store long-lived credentials in GitHub while providing secure, temporary access to PyPI publishing capabilities.

## Security Architecture

### AWS OIDC Authentication Flow

1. **GitHub Actions Workflow** requests an OIDC token from GitHub
2. **AWS STS** validates the OIDC token and GitHub repository identity
3. **Temporary AWS credentials** are issued for the specific workflow
4. **PyPI token** is retrieved from AWS Secrets Manager using temporary credentials
5. **Package publishing** occurs using the retrieved PyPI token
6. **Credentials automatically expire** after workflow completion

### Security Benefits

- **No long-lived credentials** stored in GitHub repository
- **Temporary access tokens** with automatic expiration (15 minutes)
- **Role-based permissions** with minimal required access
- **Audit trail** through AWS CloudTrail
- **Credential rotation** support through AWS Secrets Manager

## Credential Types and Management

### 1. PyPI API Token

**Storage**: AWS Secrets Manager
**Format**: `pypi-<base64-encoded-token>`
**Permissions**: Package-specific publishing rights
**Rotation**: Manual (recommended every 90 days)

**Security Measures**:
- Stored encrypted at rest in AWS Secrets Manager
- Retrieved only during publishing workflows
- Never logged or exposed in workflow outputs
- Automatically masked in GitHub Actions logs

### 2. AWS OIDC Role

**Type**: AWS IAM Role with OIDC trust relationship
**Permissions**: Minimal access to specific Secrets Manager secret
**Trust Policy**: Restricted to specific GitHub repository

**Security Configuration**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:ORG/REPO:*"
        }
      }
    }
  ]
}
```

### 3. GitHub Repository Secrets

**Required Secrets**:
- `AWS_ROLE_ARN`: ARN of the AWS IAM role for OIDC authentication
- `AWS_SECRET_NAME`: Name of the PyPI token secret in AWS Secrets Manager
- `AWS_REGION`: AWS region where resources are deployed

**Security Practices**:
- Repository secrets are encrypted by GitHub
- Only accessible during workflow execution
- Not visible in workflow logs
- Restricted to repository collaborators with appropriate permissions

## Security Validation

### Automated Security Scanning

The project includes automated credential security validation:

```bash
# Run comprehensive credential security scan
./scripts/credential_security_validator.py

# Generate security report
./scripts/credential_security_validator.py --output-format markdown --output-file security-report.md

# Fail CI/CD on security violations
./scripts/credential_security_validator.py --fail-on-violations
```

### Security Checks Performed

1. **Credential Exposure Detection**:
   - Scans workflow files for exposed tokens
   - Checks script files for hardcoded credentials
   - Validates log files for credential leakage
   - Identifies unsafe environment variable usage

2. **GitHub Secrets Validation**:
   - Ensures proper secrets syntax in workflows
   - Validates required secrets are configured
   - Checks for secret reference patterns

3. **Pattern Recognition**:
   - PyPI token patterns (`pypi-*`)
   - GitHub token patterns (`ghp_*`, `ghs_*`)
   - AWS access key patterns (`AKIA*`)
   - Generic base64 token patterns

### Manual Security Review

Regular security reviews should include:

1. **Credential Rotation**:
   - PyPI tokens every 90 days
   - AWS access keys (if any) every 90 days
   - GitHub personal access tokens every 90 days

2. **Access Review**:
   - Repository collaborator permissions
   - AWS IAM role permissions
   - PyPI package maintainer access

3. **Audit Trail Review**:
   - AWS CloudTrail logs for unusual activity
   - GitHub Actions workflow execution logs
   - PyPI package upload history

## Incident Response

### Credential Compromise Response

If credentials are potentially compromised:

1. **Immediate Actions**:
   - Rotate the compromised credential immediately
   - Review recent activity logs
   - Check for unauthorized package uploads
   - Disable the compromised credential

2. **Investigation**:
   - Identify the scope of potential exposure
   - Review all systems that may have been affected
   - Check for any unauthorized changes

3. **Recovery**:
   - Generate new credentials with proper security
   - Update all systems with new credentials
   - Verify system integrity
   - Document the incident and lessons learned

### Emergency Contacts

- **PyPI Security**: security@pypi.org
- **GitHub Security**: https://github.com/security
- **AWS Security**: aws-security@amazon.com

## Best Practices

### Development Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for local development
3. **Implement credential masking** in all logging
4. **Regular security scans** as part of CI/CD
5. **Principle of least privilege** for all access

### Workflow Security

1. **Minimize credential scope** to specific operations
2. **Use short-lived tokens** whenever possible
3. **Implement proper error handling** to prevent credential exposure
4. **Regular security audits** of workflow configurations
5. **Monitor for unusual activity** in publishing workflows

### Infrastructure Security

1. **Enable AWS CloudTrail** for audit logging
2. **Use AWS Secrets Manager** for credential storage
3. **Implement proper IAM policies** with minimal permissions
4. **Regular security assessments** of AWS infrastructure
5. **Monitor for security alerts** and respond promptly

## Compliance and Auditing

### Audit Requirements

The credential management system supports:

- **SOC 2 Type II** compliance through AWS services
- **ISO 27001** compliance through documented procedures
- **GDPR** compliance through data protection measures
- **Industry best practices** for credential management

### Audit Trail

All credential operations are logged:

- **AWS CloudTrail**: All AWS API calls and credential usage
- **GitHub Actions**: Workflow execution and secret access
- **PyPI**: Package upload and publishing activities
- **Application Logs**: Credential retrieval and validation

### Reporting

Regular security reports include:

- **Credential usage statistics**
- **Security scan results**
- **Compliance status**
- **Incident reports**
- **Recommendations for improvement**

## Troubleshooting

### Common Issues

1. **OIDC Authentication Failures**:
   - Verify GitHub repository configuration
   - Check AWS IAM role trust policy
   - Validate OIDC provider configuration

2. **Secrets Manager Access Denied**:
   - Verify IAM role permissions
   - Check secret resource policy
   - Validate secret name and region

3. **PyPI Publishing Failures**:
   - Verify PyPI token validity
   - Check token permissions for package
   - Validate package metadata

### Diagnostic Tools

```bash
# Test OIDC credential management
./scripts/oidc_credential_manager.py --action summary

# Validate credential security
./scripts/credential_security_validator.py

# Test PyPI token retrieval
./scripts/oidc_credential_manager.py --action retrieve --secret-name mypylogger/pypi-token
```

## Updates and Maintenance

### Regular Maintenance Tasks

1. **Monthly**:
   - Review security scan results
   - Check for credential expiration warnings
   - Validate backup and recovery procedures

2. **Quarterly**:
   - Rotate PyPI tokens
   - Review and update IAM policies
   - Conduct security assessments

3. **Annually**:
   - Comprehensive security audit
   - Update security documentation
   - Review and update incident response procedures

### Version Updates

When updating the credential management system:

1. **Test in staging environment** first
2. **Validate all security measures** remain intact
3. **Update documentation** as needed
4. **Communicate changes** to team members
5. **Monitor for issues** after deployment

This credential security guide ensures that mypylogger maintains the highest standards of security for PyPI publishing while providing transparency and auditability for all credential operations.