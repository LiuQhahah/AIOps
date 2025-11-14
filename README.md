# Multi-Cloud OpsAgent

An intelligent AIOps agent for detecting and auto-remediating resource misconfigurations across Kubernetes, AWS, and Azure environments using GitOps workflows.

## Features

- **Multi-Platform Detection**: K8s, AWS (RDS, Kinesis), Azure (Database, EventHubs)
- **GitOps Automation**: Auto-creates PRs for configuration fixes via GitHub
- **Intelligent Remediation**: Severity-based auto-approval workflows
- **Multi-Channel Notifications**: Teams, Email, Grafana annotations
- **Comprehensive Auditing**: Full audit trail of all detections and fixes
- **Local E2E Testing**: Kind-based local development environment

## Architecture

```
Detection → Analysis → GitOps Fix → PR Creation → Approval → Auto-Deploy → Verification
```

See [docs/architecture.md](docs/architecture.md) for detailed design.

## Quick Start

### Deploy to Kubernetes using Helm (Recommended)

#### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, or local Kind cluster)
- Helm 3.8+
- kubectl configured with cluster access

#### First Time Installation

```bash
# 1. Install the latest version
helm install opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace opsagent \
  --create-namespace

# 2. Verify deployment
kubectl get pods -n opsagent

# 3. Check logs
kubectl logs -n opsagent -l app.kubernetes.io/name=opsagent --tail=50
```

#### Upgrade to New Version

```bash
# 1. Check available versions
# Visit: https://github.com/LiuQhahah/AIOps/pkgs/container/opsagent

# 2. Upgrade to latest version
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace opsagent

# 3. Upgrade to specific version
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent \
  --version 1.0.45 \
  --namespace opsagent

# 4. Verify upgrade
kubectl rollout status deployment/opsagent -n opsagent
```

#### Customize Configuration

```bash
# 1. Create custom values file
cat > custom-values.yaml <<EOF
replicaCount: 1

image:
  pullPolicy: Always

config:
  k8s:
    in_cluster: true

  detection:
    interval: 300

  remediation:
    enabled: true
    dry_run: false  # Enable actual remediation

  logging:
    level: DEBUG
EOF

# 2. Install with custom values
helm install opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace opsagent \
  --create-namespace \
  --values custom-values.yaml

# 3. Upgrade with new values
helm upgrade opsagent oci://ghcr.io/liuqhahah/opsagent \
  --namespace opsagent \
  --values custom-values.yaml
```

#### Uninstall

```bash
# Remove Helm release
helm uninstall opsagent -n opsagent

# Delete namespace (optional)
kubectl delete namespace opsagent
```

#### Common Commands

```bash
# Show current values
helm get values opsagent -n opsagent

# Show all values (including defaults)
helm get values opsagent -n opsagent --all

# View chart information
helm show chart oci://ghcr.io/liuqhahah/opsagent

# View available configuration options
helm show values oci://ghcr.io/liuqhahah/opsagent

# Check release history
helm history opsagent -n opsagent

# Rollback to previous version
helm rollback opsagent -n opsagent
```

For more deployment options, see:
- [Helm Quick Start Guide](HELM_QUICK_START.md)
- [Complete Helm Deployment Guide](HELM_DEPLOYMENT.md)
- [Automated Release Process](HELM_AUTO_RELEASE.md)

---

### Local Development

#### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Kind (Kubernetes in Docker)
- kubectl
- AWS CLI (configured with `aws configure`)
- Azure CLI (logged in with `az login`)

#### Setup and Run

```bash
# 1. Setup local E2E environment
make setup-local

# 2. Run OpsAgent locally
make run-agent-local

# 3. Inject test issues
make inject-issue

# 4. Run E2E tests
make test-e2e

# 5. Cleanup
make clean-local
```

## Project Structure

```
src/
├── detectors/      # Platform-specific detectors (K8s, AWS, Azure)
├── remediation/    # Fix generators (YAML, Terraform, Helm)
├── gitops/         # Git operations & PR management
├── mcp/            # MCP client integrations
└── core/           # Detection & remediation engines

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/            # End-to-end tests with Kind

local-dev/          # Local development environment
├── kind/           # Kind cluster configs
├── test-manifests/ # Local IaC repository
└── mock-services/  # Mock GitHub/Teams APIs
```

## Configuration

- `config/config.yaml` - Production configuration
- `config/config.local.yaml` - Local development configuration
- `config/mcp_servers.json` - MCP server connections

## Documentation

### Deployment Guides
- [Helm Quick Start](HELM_QUICK_START.md) - Get started in 3 minutes
- [Helm Deployment Guide](HELM_DEPLOYMENT.md) - Complete deployment instructions
- [Automated Release Process](HELM_AUTO_RELEASE.md) - How releases work
- [GHCR Image Configuration](GHCR_IMAGE_SETUP.md) - Docker image setup

### Development Guides
- [Architecture](docs/architecture.md)
- [Detectors Guide](docs/detectors.md)
- [Development Guide](docs/development.md)
- [Local Deployment](docs/deployment.md)

## License

MIT
