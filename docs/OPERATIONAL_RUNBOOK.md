# Phase 7 PyPI Publishing - Operational Runbook

## Quick Reference

### Emergency Contacts
- **Primary**: Repository maintainer
- **Secondary**: Security team
- **Escalation**: DevOps team

### Critical Commands
```bash
# Emergency disable automated workflows
gh workflow disable security-driven-release.yml

# Health check
uv run python scripts/integration_orchestrator.py health-check

# Manual publishing (emergency)
gh workflow run pypi-publish.yml --ref main

# Validation suite
uv run python scripts/security_performance_validator.py validate
```

## Incident Response Procedures

### 1. Publishing Failure Response

**Symptoms:**
- PyPI publishing workflow fails
- Package not available on PyPI
- Authentication errors in workflow logs

**Immediate Actions:**
1. Check workflow status in GitHub Actions
2. Verify OIDC authentication is working
3. Check PyPI token validity
4. Review error logs for specific failure cause

**Diagnostic Commands:**
```bash
# Check AWS OIDC authentication
aws sts get-caller-identity

# Verify PyPI token
aws secretsmanager get-secret-value --secret-id pypi-token-secret

# Test package build locally
uv run python -m build
uv run twine check dist/*

# Run publishing validation
uv run python scripts/security_performance_validator.py validate
```

**Resolution Steps:**
1. **Authentication Issues:**
   ```bash
   # Verify AWS role configuration
   aws iam get-role --role-name GitHubActionsRole
   
   # Check GitHub OIDC trust relationship
   # Ensure repository and branch are correctly configured
   ```

2. **Token Issues:**
   ```bash
   # Rotate PyPI token if expired/invalid
   # 1. Generate new token in PyPI web interface
   # 2. Update AWS Secrets Manager
   aws secretsmanager put-secret-value \
     --secret-id pypi-token-secret \
     --secret-string '{"token":"new-token-here"}'
   ```

3. **Package Issues:**
   ```bash
   # Fix package validation errors
   uv run python -m build
   uv run twine check dist/*
   
   # Ensure all quality gates pass
   ./scripts/run_tests.sh
   ```

**Recovery:**
```bash
# Manual publishing after fix
gh workflow run pypi-publish.yml \
  --ref main \
  -f release_type=manual \
  -f release_notes="Emergency fix for publishing issue"
```

### 2. Security Scan Failure Response

**Symptoms:**
- Security-driven release workflow fails
- Security findings not updated
- Missing weekly security scans

**Immediate Actions:**
1. Check security scan workflow logs
2. Verify security tools are accessible
3. Check security reports directory

**Diagnostic Commands:**
```bash
# Run security scans manually
uv run bandit -r src/ -f json -o security/reports/latest/bandit.json
uv run pip-audit --format=json --output=security/reports/latest/pip-audit.json

# Check security findings update
uv run python security/scripts/update-findings.py --verbose

# Validate security reports format
python -m json.tool security/reports/latest/bandit.json
python -m json.tool security/reports/latest/pip-audit.json
```

**Resolution Steps:**
1. **Tool Issues:**
   ```bash
   # Update security tools
   uv add --dev bandit@latest pip-audit@latest
   
   # Test tools work correctly
   uv run bandit --version
   uv run pip-audit --version
   ```

2. **Report Format Issues:**
   ```bash
   # Regenerate reports with correct format
   mkdir -p security/reports/latest
   uv run bandit -r src/ -f json -o security/reports/latest/bandit.json
   uv run pip-audit --format=json --output=security/reports/latest/pip-audit.json
   echo "[]" > security/reports/latest/secrets-scan.json
   ```

**Recovery:**
```bash
# Trigger security-driven workflow manually
gh workflow run security-driven-release.yml --ref main
```

### 3. Status API Degradation Response

**Symptoms:**
- Status API returning errors
- Status page not loading
- Outdated security information

**Immediate Actions:**
1. Check status file integrity
2. Verify file permissions
3. Test status API endpoints

**Diagnostic Commands:**
```bash
# Validate status file format
python -m json.tool docs/security-status/index.json

# Check file permissions
ls -la docs/security-status/

# Test status API performance
uv run python scripts/security_performance_validator.py performance

# Regenerate status files
uv run python scripts/integration_orchestrator.py manual-workflow \
  --notes="Status API recovery"
```

**Resolution Steps:**
1. **File Corruption:**
   ```bash
   # Regenerate status files
   uv run python scripts/integration_orchestrator.py security-workflow
   
   # Verify files are valid
   python -m json.tool docs/security-status/index.json
   ```

2. **Permission Issues:**
   ```bash
   # Fix file permissions
   chmod 644 docs/security-status/index.json
   chmod 644 docs/security-status/index.html
   ```

**Recovery:**
```bash
# Force status update
uv run python scripts/integration_orchestrator.py manual-workflow \
  --notes="Status API recovery - $(date)"
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Publishing Success Rate**
   - Target: >95%
   - Alert: <90% over 7 days
   - Critical: <80% over 24 hours

2. **Workflow Execution Time**
   - Target: <5 minutes
   - Alert: >7 minutes average
   - Critical: >10 minutes for single execution

3. **Security Scan Frequency**
   - Target: Weekly scans
   - Alert: >10 days since last scan
   - Critical: >14 days since last scan

4. **API Response Time**
   - Target: <200ms
   - Alert: >500ms average
   - Critical: >1000ms or timeouts

### Monitoring Commands

```bash
# Check publishing statistics
uv run python scripts/workflow_monitoring.py stats --days=7

# Generate monitoring dashboard
uv run python scripts/workflow_monitoring.py dashboard

# System health check
uv run python scripts/integration_orchestrator.py health-check

# Performance validation
uv run python scripts/security_performance_validator.py performance
```

### Alert Conditions

**Critical Alerts (Immediate Response Required):**
- Publishing failures >2 consecutive attempts
- OIDC authentication failures
- Security scan failures >24 hours
- Status API completely unavailable

**Warning Alerts (Response Within 4 Hours):**
- Publishing success rate <95%
- Workflow execution time >7 minutes
- Security scan >10 days old
- API response time >500ms

**Info Alerts (Response Within 24 Hours):**
- New security vulnerabilities detected
- Workflow execution time trending up
- Unusual release frequency

## Maintenance Procedures

### Daily Maintenance

**Automated Checks:**
- Security scans run automatically (weekly)
- Publishing workflows monitored automatically
- Status API updated automatically

**Manual Verification:**
```bash
# Quick health check (5 minutes)
uv run python scripts/integration_orchestrator.py health-check

# Review recent workflow executions
gh run list --workflow=security-driven-release.yml --limit=5
gh run list --workflow=pypi-publish.yml --limit=5
```

### Weekly Maintenance

**Security Review:**
```bash
# Review security findings
cat security/findings/SECURITY_FINDINGS.md

# Check for new vulnerabilities
uv run python security/scripts/update-findings.py --verbose

# Verify security status accuracy
python -m json.tool docs/security-status/index.json
```

**Performance Review:**
```bash
# Generate weekly performance report
uv run python scripts/workflow_monitoring.py stats --days=7

# Check workflow execution trends
uv run python scripts/workflow_monitoring.py dashboard
```

### Monthly Maintenance

**Dependency Updates:**
```bash
# Update security tools
uv add --dev bandit@latest pip-audit@latest

# Update publishing tools
uv add --dev build@latest twine@latest

# Update project dependencies
uv sync --upgrade

# Run full test suite after updates
./scripts/run_tests.sh
```

**Credential Review:**
```bash
# Check PyPI token expiration
# (Manual check in PyPI web interface)

# Verify AWS OIDC role configuration
aws iam get-role --role-name GitHubActionsRole

# Review AWS CloudTrail logs for authentication events
aws logs describe-log-groups --log-group-name-prefix="/aws/iam"
```

### Quarterly Maintenance

**Security Audit:**
```bash
# Run comprehensive security validation
uv run python scripts/security_performance_validator.py validate

# Review all security findings and remediation plans
cat security/findings/SECURITY_FINDINGS.md
cat security/findings/remediation-plans.yml

# Audit workflow permissions and access
gh api repos/:owner/:repo/actions/permissions
```

**Performance Optimization:**
```bash
# Analyze workflow performance trends
uv run python scripts/workflow_monitoring.py stats --days=90

# Review and optimize workflow configurations
# Check for opportunities to improve execution time

# Update performance targets if needed
# Review API response time requirements
```

### Annual Maintenance

**Comprehensive Review:**
1. Security architecture review
2. Performance baseline updates
3. Disaster recovery testing
4. Documentation updates
5. Training and knowledge transfer

**Credential Rotation:**
```bash
# Rotate PyPI token (recommended annually)
# 1. Generate new token in PyPI web interface
# 2. Update AWS Secrets Manager
# 3. Test publishing workflow
# 4. Revoke old token

# Review and rotate AWS OIDC credentials if needed
# Update GitHub repository secrets if changed
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "OIDC Authentication Failed"

**Symptoms:**
- Workflow fails with authentication error
- "Unable to assume role" messages
- AWS STS errors in logs

**Diagnosis:**
```bash
# Check AWS role exists and is accessible
aws iam get-role --role-name GitHubActionsRole

# Verify OIDC provider configuration
aws iam list-open-id-connect-providers

# Check GitHub repository configuration
gh api repos/:owner/:repo/actions/oidc/customization/sub
```

**Solutions:**
1. Verify AWS role ARN in repository secrets
2. Check OIDC trust relationship includes correct repository
3. Ensure GitHub Actions has proper permissions
4. Verify AWS region configuration

#### Issue: "PyPI Token Invalid"

**Symptoms:**
- Publishing fails with authentication error
- "Invalid token" messages from PyPI
- 403 Forbidden errors

**Diagnosis:**
```bash
# Check token in AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id pypi-token-secret

# Test token manually (if safe to do so)
# twine upload --repository testpypi dist/* --username __token__ --password <token>
```

**Solutions:**
1. Generate new PyPI token with correct permissions
2. Update AWS Secrets Manager with new token
3. Verify token scope includes package publishing
4. Check PyPI account permissions

#### Issue: "Security Scan Timeout"

**Symptoms:**
- Security workflows timeout
- Incomplete security reports
- Missing vulnerability data

**Diagnosis:**
```bash
# Run security scans manually with timeout
timeout 300 uv run bandit -r src/ -f json
timeout 300 uv run pip-audit --format=json

# Check for large files or complex code patterns
find src/ -name "*.py" -size +100k
```

**Solutions:**
1. Increase workflow timeout limits
2. Exclude large or generated files from scanning
3. Update security tools to latest versions
4. Split large scans into smaller chunks

#### Issue: "Status API Slow Response"

**Symptoms:**
- Status page loads slowly
- API response times >1 second
- Timeout errors accessing status

**Diagnosis:**
```bash
# Test local file access performance
time python -c "import json; json.load(open('docs/security-status/index.json'))"

# Check file size
ls -lh docs/security-status/index.json

# Test API performance
uv run python scripts/security_performance_validator.py performance
```

**Solutions:**
1. Optimize status data structure
2. Reduce amount of historical data stored
3. Implement caching if needed
4. Use CDN for static file serving

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set debug environment variable
export DEBUG=true
export VERBOSE=true

# Run commands with debug output
uv run python scripts/integration_orchestrator.py security-workflow

# Check detailed logs
tail -f /tmp/integration_orchestrator.log
```

### Log Analysis

**GitHub Actions Logs:**
1. Navigate to Actions tab in repository
2. Select failed workflow run
3. Expand failed job steps
4. Download logs for offline analysis

**Local Logs:**
```bash
# Check workflow monitoring logs
ls -la metrics/workflow-*.json

# Analyze error patterns
grep -r "ERROR" metrics/
grep -r "FAILED" metrics/

# Review security scan logs
ls -la security/reports/latest/
```

## Disaster Recovery

### Backup Procedures

**Critical Data to Backup:**
- AWS OIDC role configuration
- PyPI token (securely stored)
- Security findings history
- Workflow metrics and logs

**Backup Commands:**
```bash
# Export security findings
cp -r security/findings/ backup/security-findings-$(date +%Y%m%d)/

# Export workflow metrics
cp -r metrics/ backup/metrics-$(date +%Y%m%d)/

# Export configuration
cp -r .github/workflows/ backup/workflows-$(date +%Y%m%d)/
```

### Recovery Procedures

**Complete System Recovery:**
1. Restore repository from backup
2. Reconfigure AWS OIDC infrastructure
3. Update GitHub repository secrets
4. Test all workflows in dry-run mode
5. Gradually enable automated workflows

**Partial Recovery:**
```bash
# Restore security findings
cp -r backup/security-findings-latest/* security/findings/

# Restore workflow configurations
cp -r backup/workflows-latest/* .github/workflows/

# Regenerate status files
uv run python scripts/integration_orchestrator.py security-workflow
```

### Testing Recovery

```bash
# Test all components after recovery
uv run python scripts/security_performance_validator.py validate

# Test workflows in dry-run mode
gh workflow run pypi-publish.yml --ref main -f dry_run=true

# Verify monitoring is working
uv run python scripts/integration_orchestrator.py health-check
```

## Contact Information

### Escalation Path

1. **Level 1**: Repository maintainer (immediate response)
2. **Level 2**: Security team (within 4 hours)
3. **Level 3**: DevOps team (within 8 hours)
4. **Level 4**: Management escalation (within 24 hours)

### External Dependencies

- **PyPI**: https://status.python.org/
- **GitHub Actions**: https://www.githubstatus.com/
- **AWS Services**: https://status.aws.amazon.com/

### Documentation Links

- [Phase 7 Documentation](PHASE_7_PYPI_PUBLISHING.md)
- [Security Findings](../security/findings/SECURITY_FINDINGS.md)
- [AWS OIDC Setup](../infrastructure/README.md)
- [GitHub Actions Workflows](../.github/workflows/README.md)

---

**Last Updated**: $(date)
**Version**: 1.0
**Next Review**: $(date -d "+3 months")