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

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Kind (Kubernetes in Docker)
- kubectl
- AWS CLI (configured with `aws configure`)
- Azure CLI (logged in with `az login`)

### Local Development

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

- [Architecture](docs/architecture.md)
- [Detectors Guide](docs/detectors.md)
- [Development Guide](docs/development.md)
- [Deployment](docs/deployment.md)

## License

MIT
