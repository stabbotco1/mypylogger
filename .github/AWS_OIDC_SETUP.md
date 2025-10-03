# AWS OIDC Integration Setup Guide

## Overview

This document provides the setup requirements for integrating GitHub Actions with AWS using OIDC (OpenID Connect) for secure, credential-free CI/CD pipelines.

## Prerequisites

- AWS account with administrative access
- GitHub repository with Actions enabled
- AWS CLI configured locally (for setup only)

## AWS Configuration Requirements

### 1. OIDC Identity Provider (Already Configured)

The following AWS OIDC Identity Provider should be configured in your AWS account:

```yaml
# AWS OIDC Identity Provider Configuration
URL: https://token.actions.githubusercontent.com
Audience: sts.amazonaws.com
Thumbprint: [GitHub's certificate thumbprint]
```

### 2. IAM Role for GitHub Actions

**Role Name**: `GitHubActionsRole` (or as configured)

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR-ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": [
            "repo:stabbotco1/mypylogger:ref:refs/heads/main",
            "repo:stabbotco1/mypylogger:ref:refs/heads/pre-release",
            "repo:stabbotco1/mypylogger:ref:refs/tags/*"
          ]
        }
      }
    }
  ]
}
```

**Permissions Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": [
        "arn:aws:ssm:*:YOUR-ACCOUNT:parameter/mypylogger/prod/*"
      ]
    }
  ]
}
```

### 3. AWS SSM Parameters

Create the following encrypted parameters in AWS Systems Manager Parameter Store:

```bash
# PyPI API Token
aws ssm put-parameter \
  --name "/mypylogger/prod/pypi-token" \
  --value "YOUR_PYPI_API_TOKEN" \
  --type "SecureString" \
  --description "PyPI API token for mypylogger package publishing"

# Codecov Upload Token
aws ssm put-parameter \
  --name "/mypylogger/prod/codecov-token" \
  --value "YOUR_CODECOV_TOKEN" \
  --type "SecureString" \
  --description "Codecov upload token for mypylogger coverage reporting"
```

## GitHub Repository Configuration

### Repository Variables (Not Secrets!)

Configure the following repository variables in GitHub:

1. Go to **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Add these variables:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `AWS_GITHUB_ROLE_ARN` | `arn:aws:iam::YOUR-ACCOUNT:role/GitHubActionsRole` | ARN of the IAM role for OIDC |
| `AWS_REGION` | `us-east-1` | AWS region for SSM parameters |

### No Secrets Required!

**Important**: With OIDC integration, no long-term AWS credentials are stored in GitHub secrets. All authentication happens through short-lived OIDC tokens.

## Verification

### Test OIDC Integration

Create a simple test workflow to verify the integration:

```yaml
# .github/workflows/test-oidc.yml
name: Test OIDC Integration
on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_GITHUB_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Test SSM access
        run: |
          echo "Testing SSM parameter access..."
          aws ssm get-parameter --name "/mypylogger/prod/pypi-token" --with-decryption --query Parameter.Value --output text | head -c 10
          echo "...SUCCESS"
```

### Expected Results

- ✅ GitHub Actions can assume the AWS role
- ✅ Temporary credentials are issued (15-minute expiry)
- ✅ SSM parameters can be retrieved
- ✅ No long-term credentials stored anywhere

## Security Benefits

### Zero-Credential Architecture
- **No AWS access keys** stored in GitHub
- **No long-term credentials** anywhere in the system
- **Automatic token rotation** every 15 minutes
- **Fine-grained permissions** via IAM policies

### Audit and Compliance
- **Complete audit trail** in AWS CloudTrail
- **Least privilege access** to only required resources
- **Conditional access** limited to specific repositories and branches
- **Encryption at rest** for all stored tokens

### Scalability
- **Reusable pattern** for other projects
- **Centralized secret management** in AWS
- **Easy token rotation** without GitHub changes
- **Multi-environment support** (dev/staging/prod)

## Troubleshooting

### Common Issues

#### "Unable to assume role"
- Verify the trust policy includes your repository
- Check that the OIDC provider is configured correctly
- Ensure the role ARN is correct in repository variables

#### "Access denied to SSM parameter"
- Verify the IAM role has SSM permissions
- Check the parameter path matches exactly
- Ensure the parameter exists and is encrypted

#### "Invalid OIDC token"
- Verify the workflow has `id-token: write` permission
- Check that the audience is set to `sts.amazonaws.com`
- Ensure the GitHub OIDC provider thumbprint is current

### Support Resources

- [AWS OIDC Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

---

**Security Note**: This configuration provides bank-grade security for CI/CD pipelines. The zero-credential approach eliminates the most common attack vector for compromised CI/CD systems.
