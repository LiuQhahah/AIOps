# Quick Start Guide

Get the Multi-Cloud OpsAgent up and running locally in 5 minutes.

## Prerequisites

Ensure you have the following installed:

```bash
# Check versions
kind --version          # v0.20.0+
kubectl version --client # v1.28.0+
docker --version        # 20.10.0+
python --version        # 3.11.0+
```

### Install Missing Tools

**Kind:**
```bash
# macOS
brew install kind

# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

**kubectl:**
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

## Setup

### 1. Clone and Install Dependencies

```bash
# Navigate to project
cd AIOps

# Install Python dependencies
make install

# Or manually:
pip install -r requirements.txt
```

### 2. Setup Local E2E Environment

```bash
# One command to set everything up
make setup-local
```

This will:
- ✅ Create a 3-node Kind cluster
- ✅ Create test namespaces (test-app, ops-agent)
- ✅ Deploy test applications with intentional issues
- ✅ Initialize local Git repository
- ✅ Configure kubectl context

**Expected Output:**
```
🚀 Setting up Multi-Cloud OpsAgent Local E2E Environment

📋 Checking prerequisites...
✓ kind v0.20.0
✓ kubectl v1.28.0
✓ docker 24.0.0

📦 Creating Kind cluster...
✓ Cluster created

⏳ Waiting for cluster to be ready...
✓ Cluster is ready

📝 Creating namespaces...
✓ Namespaces created

🐛 Deploying test applications (with intentional issues)...
✓ Test applications deployed

📚 Setting up local IaC Git repository...
✓ Git repository initialized

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Local E2E Environment Ready!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3. Verify Setup

```bash
# Check cluster
kubectl get nodes
# NAME                            STATUS   ROLES           AGE   VERSION
# ops-agent-test-control-plane    Ready    control-plane   1m    v1.27.3
# ops-agent-test-worker           Ready    <none>          1m    v1.27.3
# ops-agent-test-worker2          Ready    <none>          1m    v1.27.3

# Check test deployments
kubectl get deployments -n test-app
# NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
# no-resources-app          2/2     2            2           30s
# excessive-replicas-app    20/20   20           20          30s
# over-provisioned-app      1/1     1            1           30s
# ...
```

### 4. Run E2E Tests

```bash
# Run environment tests
make test-e2e
```

**Expected Output:**
```
🧪 Running E2E Tests

tests/e2e/test_environment.py::TestEnvironmentSetup::test_cluster_is_accessible PASSED
tests/e2e/test_environment.py::TestEnvironmentSetup::test_test_namespace_exists PASSED
tests/e2e/test_environment.py::TestEnvironmentSetup::test_test_deployments_exist PASSED

tests/e2e/test_detection.py::TestK8sDetection::test_detect_deployment_without_resources PASSED
tests/e2e/test_detection.py::TestK8sDetection::test_detect_excessive_replicas PASSED

✅ E2E tests completed
```

## Next Steps

### Option 1: Run OpsAgent Locally (Coming Soon)

```bash
# Configure environment
cp .env.example .env
# Edit .env with your AWS/Azure credentials

# Run agent
make run-agent-local
```

### Option 2: Manually Test Detection

```bash
# Deploy a deployment with issues
kubectl apply -f tests/e2e/fixtures/k8s/01-no-resources-deployment.yaml

# Check the deployment
kubectl describe deployment no-resources-app -n test-app
# Notice: No resource limits defined!

# OpsAgent should detect this and create a fix
```

### Option 3: Inject More Issues

```bash
# Scale a deployment to trigger detection
make inject-issue

# This scales excessive-replicas-app to 20 replicas
# OpsAgent should detect and propose a fix
```

## Development Workflow

```bash
# 1. Write code
vim src/detectors/k8s/pod_resources.py

# 2. Run tests
make test-unit

# 3. Test locally with Kind
make test-e2e

# 4. Format code
make format

# 5. Lint
make lint
```

## Cleanup

```bash
# Delete Kind cluster and cleanup
make clean-local
```

## Troubleshooting

### Kind cluster won't start
```bash
# Check Docker is running
docker ps

# Delete existing cluster
kind delete cluster --name ops-agent-test

# Try again
make setup-local
```

### Tests failing
```bash
# Check kubectl context
kubectl config current-context
# Should be: kind-ops-agent-test

# Check pods are running
kubectl get pods -A

# Check logs
kubectl logs -n test-app deployment/no-resources-app
```

### Can't connect to cluster
```bash
# Reset kubeconfig
kind export kubeconfig --name ops-agent-test

# Verify
kubectl cluster-info
```

## What's Next?

Now that your local environment is ready:

1. **Implement K8s Detector**: Edit `src/detectors/k8s/pod_resources.py`
2. **Implement GitOps**: Edit `src/gitops/pr_creator.py`
3. **Add More Tests**: Add to `tests/e2e/`

See [docs/DEVELOPMENT.md](DEVELOPMENT.md) for detailed development guide.
