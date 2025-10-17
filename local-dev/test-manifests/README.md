# Test IaC Repository

This is a local Git repository for testing OpsAgent's GitOps workflow.

## Purpose

This repository simulates a real IaC repository where:
- OpsAgent detects issues in K8s/AWS/Azure
- OpsAgent creates branches and commits fixes
- OpsAgent creates PRs (simulated locally)
- Changes are applied back to the cluster

## Structure

```
├── k8s/
│   └── deployments/        # Kubernetes deployment manifests
├── terraform/
│   ├── aws/                # AWS Terraform configurations
│   └── azure/              # Azure Terraform configurations
└── README.md
```

## OpsAgent Workflow

1. **Detection**: OpsAgent scans live resources
2. **Analysis**: Identifies misconfiguration
3. **Git Operations**:
   - Clones this repository
   - Creates fix branch: `fix/ops-agent-{issue-id}`
   - Modifies the relevant file
   - Commits changes
   - (In production) Creates GitHub PR
4. **Deployment**: Changes are applied
5. **Verification**: OpsAgent re-scans to verify fix

## Usage

```bash
# View commit history
git log --oneline

# View branches (OpsAgent creates fix branches)
git branch -a

# View diffs
git diff main..fix/ops-agent-xxx
```

## Note

This is initialized by `scripts/setup-local-env.sh` during local environment setup.
