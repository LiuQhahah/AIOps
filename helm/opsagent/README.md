# OpsAgent Helm Chart

[![Chart Version](https://img.shields.io/badge/chart-1.0.0-blue.svg)](Chart.yaml)
[![App Version](https://img.shields.io/badge/app-1.0.0-green.svg)](Chart.yaml)

AI-powered Operations Automation Platform for Kubernetes

## TL;DR

```bash
helm install opsagent ./helm/opsagent --namespace ops-system --create-namespace
```

## Introduction

This chart deploys OpsAgent on a Kubernetes cluster using the Helm package manager.

OpsAgent automatically detects and optionally remediates operational issues in your Kubernetes infrastructure.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.8+
- kubectl configured to communicate with your cluster

## Installing the Chart

To install the chart with the release name `opsagent`:

```bash
helm install opsagent ./helm/opsagent --namespace ops-system --create-namespace
```

The command deploys OpsAgent on the Kubernetes cluster with default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

## Uninstalling the Chart

To uninstall/delete the `opsagent` deployment:

```bash
helm uninstall opsagent --namespace ops-system
```

This removes all the Kubernetes components associated with the chart and deletes the release.

## Parameters

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `nameOverride` | String to override the name | `""` |
| `fullnameOverride` | String to fully override the fullname | `""` |

### Image Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `opsagent` |
| `image.tag` | Image tag (overrides the Chart appVersion) | `""` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `imagePullSecrets` | Image pull secrets | `[]` |

### Service Account Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `serviceAccount.create` | Create service account | `true` |
| `serviceAccount.annotations` | Service account annotations | `{}` |
| `serviceAccount.name` | Service account name | `""` |

### RBAC Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `rbac.create` | Create RBAC resources | `true` |

### Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Service type | `ClusterIP` |
| `service.ports.http.port` | HTTP service port | `80` |
| `service.ports.metrics.port` | Metrics service port | `9090` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.hosts` | Ingress hosts configuration | `[{"host": "opsagent.local", "paths": [{"path": "/", "pathType": "Prefix"}]}]` |

### Resources Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.requests.cpu` | CPU request | `200m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `512Mi` |

### Application Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.k8s.in_cluster` | Use in-cluster K8s config | `true` |
| `config.detection.interval` | Detection interval in seconds | `300` |
| `config.remediation.enabled` | Enable auto-remediation | `false` |
| `config.remediation.dry_run` | Enable dry-run mode | `true` |
| `config.logging.level` | Log level | `INFO` |
| `config.logging.format` | Log format (json/text) | `json` |

### AWS Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.aws.enabled` | Enable AWS integration | `false` |
| `config.aws.region` | AWS region | `us-east-1` |
| `config.aws.resources.rds.enabled` | Enable RDS monitoring | `false` |
| `config.aws.resources.kinesis.enabled` | Enable Kinesis monitoring | `false` |

### Secrets Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.create` | Create secrets from values | `false` |
| `existingSecret` | Name of existing secret to use | `""` |
| `secrets.aws.accessKeyId` | AWS access key ID | `""` |
| `secrets.aws.secretAccessKey` | AWS secret access key | `""` |

For a complete list of parameters, see [values.yaml](values.yaml).

## Configuration Examples

### Example 1: Basic Installation

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace
```

### Example 2: Custom Detection Interval

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set config.detection.interval=600
```

### Example 3: Enable Remediation

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --set config.remediation.enabled=true \
  --set config.remediation.dry_run=false
```

### Example 4: With Custom Values File

Create `my-values.yaml`:

```yaml
image:
  repository: your-registry/opsagent
  tag: 1.0.0

config:
  detection:
    interval: 600
  remediation:
    enabled: true
    dry_run: false
  logging:
    level: DEBUG

resources:
  requests:
    cpu: 500m
    memory: 512Mi
```

Install:

```bash
helm install opsagent ./helm/opsagent \
  --namespace ops-system \
  --create-namespace \
  --values my-values.yaml
```

## Upgrading

To upgrade an existing release:

```bash
helm upgrade opsagent ./helm/opsagent \
  --namespace ops-system \
  --values my-values.yaml
```

## Rollback

To rollback to a previous release:

```bash
# Rollback to previous release
helm rollback opsagent --namespace ops-system

# Rollback to specific revision
helm rollback opsagent 2 --namespace ops-system
```

## Testing the Chart

```bash
# Lint the chart
helm lint ./helm/opsagent

# Test template rendering
helm template opsagent ./helm/opsagent --debug

# Dry-run installation
helm install opsagent ./helm/opsagent --dry-run --debug
```

## Troubleshooting

### Check Installation Status

```bash
helm status opsagent --namespace ops-system
```

### View Logs

```bash
kubectl logs -f -n ops-system -l app=opsagent
```

### Check Pod Status

```bash
kubectl get pods -n ops-system
kubectl describe pod -n ops-system -l app=opsagent
```

### View Configuration

```bash
helm get values opsagent --namespace ops-system --all
```

## Documentation

For detailed documentation, see:

- [Full Deployment Guide](../../HELM_DEPLOYMENT.md)
- [Kubernetes Deployment](../../KUBERNETES_DEPLOYMENT.md)
- [CI/CD Documentation](../../CICD_README.md)

## Support

For issues and questions:

- GitHub Issues: https://github.com/your-org/opsagent/issues
- Documentation: https://github.com/your-org/opsagent

## License

Apache 2.0
