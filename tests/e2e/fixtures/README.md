# Test Fixtures

This directory contains intentionally misconfigured resources for E2E testing.

## Kubernetes Fixtures

### 01-no-resources-deployment.yaml
- **Issue**: No resource limits/requests defined
- **Severity**: MEDIUM
- **Expected Detection**: Pod missing resources
- **Expected Fix**: Add resource requests and limits

### 02-excessive-replicas.yaml
- **Issue**: Too many replicas (20) for test environment
- **Severity**: MEDIUM
- **Expected Detection**: Excessive replica count
- **Expected Fix**: Reduce to 2-3 replicas

### 03-over-provisioned.yaml
- **Issue**: Requesting 8Gi memory and 4 CPUs for nginx
- **Severity**: LOW
- **Expected Detection**: Over-provisioned resources
- **Expected Fix**: Reduce to reasonable values (128Mi, 200m)

### 04-no-liveness-probe.yaml
- **Issue**: Missing health check probes
- **Severity**: MEDIUM
- **Expected Detection**: No liveness/readiness probes
- **Expected Fix**: Add HTTP health checks

### 05-multiple-issues.yaml
- **Issue**: Combination of multiple issues
- **Severity**: HIGH
- **Expected Detection**: Multiple issues detected
- **Expected Fix**: Fix all issues

## Terraform Fixtures (AWS)

### rds-oversized.tf
- **Issue**: db.r5.4xlarge for test environment
- **Severity**: MEDIUM
- **Expected Detection**: RDS instance oversized
- **Expected Fix**: Downgrade to db.t3.medium

### kinesis-under-provisioned.tf
- **Issue**: Production stream with only 1 shard
- **Severity**: HIGH
- **Expected Detection**: Kinesis under-provisioned
- **Expected Fix**: Increase shard count to 3-5

## Usage

```bash
# Deploy K8s fixtures
kubectl apply -f k8s/

# List deployed resources
kubectl get deployments -n test-app

# Verify issues are present
kubectl describe deployment no-resources-app -n test-app
```

## Expected OpsAgent Behavior

1. **Detection**: Agent should detect all issues within 60 seconds
2. **Analysis**: Each issue should be categorized by severity
3. **Remediation**:
   - LOW severity: Auto-fix immediately
   - MEDIUM severity: Auto-fix or create PR (based on config)
   - HIGH severity: Create PR for approval
4. **Notification**: Send alerts via Teams/Email
5. **GitOps**: Create PRs in local Git repo with fixes
6. **Verification**: Re-scan and verify issues resolved
